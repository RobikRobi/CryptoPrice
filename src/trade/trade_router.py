from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal

from src.get_current_user import get_current_user
from src.db import get_session
from src.models.AccountModel import Account
from src.models.UserModel import User
from src.redis_connect import redis_client  # твой клиент Redis
from src.enum.CurrencyEnum import CurrencyType


app = APIRouter(prefix="/trade", tags=["Trading"])


# --- Покупка криптовалюты ---
@app.post("/buy")
async def buy_crypto(
    symbol: CurrencyType,
    amount_usd: Decimal,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # 1. Получаем цену из Redis
    price = await redis_client.get(f"prices:{symbol.value}")
    if not price:
        raise HTTPException(400, "Price not available")

    price = Decimal(price)

    # 2. Проверяем есть ли USD счёт
    usd_acc = await session.scalar(
        select(Account).filter(
            Account.owner_id == current_user.id,
            Account.currency == CurrencyType.USD
        )
    )
    if not usd_acc:
        raise HTTPException(404, "USD account not found")

    if usd_acc.available < amount_usd:
        raise HTTPException(400, "Not enough USD balance")

    # 3. Рассчитываем сколько крипты купить
    crypto_amount = amount_usd / price

    # 4. Получаем крипто-счёт (BTC, ETH...)
    crypto_acc = await session.scalar(
        select(Account).filter(
            Account.owner_id == current_user.id,
            Account.currency == symbol
        )
    )
    if not crypto_acc:
        crypto_acc = Account(
            owner_id=current_user.id,
            currency=symbol,
            available=0,
            locked=0
        )
        session.add(crypto_acc)
        await session.flush()

    # 5. Изменяем балансы
    usd_acc.available -= amount_usd
    crypto_acc.available += crypto_amount

    await session.commit()

    return {
        "message": "Crypto purchased",
        "symbol": symbol,
        "crypto_amount": float(crypto_amount),
        "spent_usd": float(amount_usd),
        "price": float(price)
    }

# --- Продажа криптовалюты ---
@app.post("/sell")
async def sell_crypto(
    symbol: CurrencyType,
    amount_crypto: Decimal,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # 1. Цена в USD
    price = await redis_client.get(f"prices:{symbol.value}")
    if not price:
        raise HTTPException(400, "Price not available")

    price = Decimal(price)

    # 2. Ищем крипто-счёт
    crypto_acc = await session.scalar(
        select(Account).filter(
            Account.owner_id == current_user.id,
            Account.currency == symbol
        )
    )

    if not crypto_acc or crypto_acc.available < amount_crypto:
        raise HTTPException(400, "Not enough crypto balance")

    # 3. USD счёт
    usd_acc = await session.scalar(
        select(Account).filter(
            Account.owner_id == current_user.id,
            Account.currency == CurrencyType.USD
        )
    )
    if not usd_acc:
        raise HTTPException(404, "USD account not found")

    # 4. Конвертация
    earned_usd = amount_crypto * price

    # 5. Изменение балансов
    crypto_acc.available -= amount_crypto
    usd_acc.available += earned_usd

    await session.commit()

    return {
        "message": "Crypto sold",
        "symbol": symbol,
        "sold_amount": float(amount_crypto),
        "earned_usd": float(earned_usd),
        "price": float(price)
    }
