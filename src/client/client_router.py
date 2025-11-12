import asyncio
import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.client.WebsocetConnect import ConnectionManager
from config import config


app = APIRouter(prefix="/client", tags=["Client"])

manager = ConnectionManager()

params = {
        "ids": ",".join(config.COINS),
        "vs_currencies": config.VS_CURRENCY,
        "include_24hr_change": "true"
    }
req = r.get(config.CR_URL, params=params, timeout=10)
print(req.json())


async def get_crypto_prices():
    """Функция для получения курса криптовалют."""
    params = {
        "ids": ",".join(config.COINS),
        "vs_currencies": config.VS_CURRENCY,
        "include_24hr_change": "true"
    }
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(config.CR_URL, params=params)
        response.raise_for_status()
        return response.json()


@app.websocket("/ws/crypto")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Получаем курс
            data = await get_crypto_prices()
            # Отправляем всем клиентам
            await manager.broadcast(data)
            # Интервал обновления
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        manager.disconnect(websocket)