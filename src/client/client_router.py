import httpx
import asyncio
import requests as r
from src.config import CryptoData
from src.redis_connect import redis_client
from fastapi import APIRouter, WebSocket

from src.client.WebsocketConnect import ConnectionManager
from src.client.crypto_price_watcher import crypto_price_watcher





app = APIRouter(prefix="/client", tags=["Client"])

manager = ConnectionManager()


params = {
        "ids": ",".join(CryptoData.COINS),
        "vs_currencies": CryptoData.VS_CURRENCY,
        "include_24hr_change": "true"
    }
req = r.get(CryptoData.CR_URL, params=params, timeout=10)


@app.websocket("/ws/crypto")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        async for data in crypto_price_watcher(interval=5):
            print(data)
            await manager.broadcast(data)
    except: pass
    manager.disconnect(websocket)
        


COINGECKO_TO_ENUM = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "tether": "USDT",
    "ripple": "XRP",
    "binancecoin": "BNB",
}

async def crypto_price_watcher(interval: int = 5):
    while True:
        params = {
            "ids": ",".join(CryptoData.COINS),
            "vs_currencies": CryptoData.VS_CURRENCY,
            "include_24hr_change": "true"
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(CryptoData.CR_URL, params=params)
            data = response.json()

        for coin_id, values in data.items():
            symbol = COINGECKO_TO_ENUM.get(coin_id)
            if not symbol:
                continue  # пропускаем неизвестные монеты

            price = values["usd"]

            await redis_client.set(f"prices:{symbol}", price)

        # USD фиксируем вручную
        await redis_client.set("prices:USD", 1)

        yield data
        await asyncio.sleep(interval)
