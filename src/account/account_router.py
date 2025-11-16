from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db import get_session
from src.enum.CurrencyEnum import CurrencyType
from decimal import Decimal
from src.get_current_user import get_current_user
from src.models.AccountModel import Account
from src.models.UserModel import User
from src.account.account_shema import AccountCreate, AccountUpdate, TransferSchema



app = APIRouter(prefix="/accounts", tags=["Accounts"])

#создание счёта
@app.post("/")
async def create_account(account_create: AccountCreate, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    account = Account(owner_id=current_user.id, currency=account_create.currency, available=account_create.available)
    session.add(account)
    await session.commit()
    await session.refresh(account)
    return account

# получение сведений о всех счетах пользователя
@app.get("/")
async def list_accounts(session: AsyncSession = Depends(get_session), current_user: User = Depends(get_current_user)):
    stmt = select(Account).where(Account.owner_id == current_user.id)
    result = await session.execute(stmt)
    accounts = result.scalars.all()
    return accounts

# получения данных о балансе определённого счёта
@app.get("/{account_id}/balance", response_model=float)
async def get_balance(account_id: int, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    account = await session.scalar(select(Account).filter(Account.id == account_id, Account.owner_id == current_user.id))
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account.available


# пополнение счёта
@app.put("/{account_id}/deposit")
async def deposit_to_account(account_id: int, account_update: AccountUpdate, 
                       session: AsyncSession = Depends(get_session), 
                       current_user: User = Depends(get_current_user)):
    account = await session.scalar(select(Account).filter(Account.id == account_id, Account.owner_id == current_user.id))
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    account.available += Decimal(account_update.available)
    session.commit()
    session.refresh(account)

    return {"message": f"Deposit of {account_update.balance} to account {account_id}"}

# Списание средств со счёта
@app.put("/{account_id}/withdraw")
async def withdraw_from_account(
    account_id: int,
    account_update: AccountUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 1. Найти счёт пользователя
    account = await session.scalar(
        select(Account).filter(
            Account.id == account_id,
            Account.owner_id == current_user.id
        )
    )

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    withdraw_amount = Decimal(account_update.available)

    # 2. Проверить достаточно ли денег
    if account.available < withdraw_amount:
        raise HTTPException(status_code=400, detail="Not enough available balance")

    # 3. Списать со счёта
    account.available -= withdraw_amount

    # 4. Сохранить
    await session.commit()
    await session.refresh(account)

    return {
        "message": f"Withdraw of {withdraw_amount} from account {account_id} successful",
        "remaining_balance": float(account.available)
    }

# Переводы между счетами
@app.post("/transfer")
async def transfer_between_accounts(
    transfer_data: TransferSchema,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    from_id = transfer_data.from_account_id
    to_id = transfer_data.to_account_id
    amount = Decimal(str(transfer_data.amount))

    # 1. Нельзя переводить сам себе на тот же счёт
    if from_id == to_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same account")

    # 2. Найти оба счёта
    from_account = await session.scalar(
        select(Account).filter(
            Account.id == from_id,
            Account.owner_id == current_user.id
        )
    )
    to_account = await session.scalar(
        select(Account).filter(
            Account.id == to_id,
            Account.owner_id == current_user.id
        )
    )

    if not from_account or not to_account:
        raise HTTPException(status_code=404, detail="One or both accounts not found")

    # 3. Проверить валюты — перевод возможен только между одинаковыми валютами
    if from_account.currency != to_account.currency:
        raise HTTPException(status_code=400, detail="Accounts must have the same currency")

    # 4. Проверка баланса
    if from_account.available < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # 5. Списываем и начисляем
    from_account.available -= amount
    to_account.available += amount

    # 6. Сохраняем
    await session.commit()

    return {
        "message": f"Transferred {amount} from account {from_id} to account {to_id}",
        "from_account_balance": float(from_account.available),
        "to_account_balance": float(to_account.available),
    }

# удаление счёта
@app.delete("/{account_id}")
async def close_account(account_id: int,  current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    account = await session.scalar(select(Account).filter(Account.id == account_id, Account.owner_id == current_user.id))
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.available != 0 or account.locked != 0:
        raise HTTPException(status_code=400, detail="Account must have zero balance to be closed")
    session.delete(account)
    session.commit()
    return {"message": f"Account with ID {account_id} closed successfully"}
