import httpx
import asyncio
import requests as r
from src.config import CryptoData
from src.redis_connect import redis_client
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.client.WebsocetConnect import ConnectionManager
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
            await manager.broadcast(data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)


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

        # --- сохраняем цены в redis ---
        for coin, values in data.items():
            price = values["usd"]
            await redis_client.set(f"prices:{coin.upper()}", price)

        yield data
        await asyncio.sleep(interval)