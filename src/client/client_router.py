# import asyncio
# import requests as r
# import httpx
# from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# from src.client.WebsocetConnect import ConnectionManager
# from src.config import CryptoData


# app = APIRouter(prefix="/client", tags=["Client"])

# manager = ConnectionManager()

# params = {
#         "ids": ",".join(CryptoData.COINS),
#         "vs_currencies": CryptoData.VS_CURRENCY,
#         "include_24hr_change": "true"
#     }
# req = r.get(CryptoData.CR_URL, params=params, timeout=10)
# print(req.json())


# async def get_crypto_prices():
#     """Функция для получения курса криптовалют."""
#     params = {
#         "ids": ",".join(CryptoData.COINS),
#         "vs_currencies": CryptoData.VS_CURRENCY,
#         "include_24hr_change": "true"
#     }
#     async with httpx.AsyncClient(timeout=10) as client:
#         response = await client.get(CryptoData.CR_URL, params=params)
#         response.raise_for_status()
#         return response.json()


# @app.websocket("/ws/crypto")
# async def websocket_endpoint(websocket: WebSocket):
#     await manager.connect(websocket)
#     try:
#         while True:
#             # Получаем курс
#             data = await get_crypto_prices()
#             # Отправляем всем клиентам
#             await manager.broadcast(data)
#             # Интервал обновления
#             await asyncio.sleep(10)
#     except WebSocketDisconnect:
#         manager.disconnect(websocket)


import asyncio
import httpx
import requests as r
from src.config import CryptoData
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.client.WebsocetConnect import ConnectionManager

app = APIRouter(prefix="/client", tags=["Client"])

manager = ConnectionManager()


params = {
        "ids": ",".join(CryptoData.COINS),
        "vs_currencies": CryptoData.VS_CURRENCY,
        "include_24hr_change": "true"
    }
req = r.get(CryptoData.CR_URL, params=params, timeout=10)
print(req.json())


async def crypto_price_watcher(interval: int = 5):
    """
    Асинхронный генератор, возвращает новые данные
    ТОЛЬКО когда курс криптовалют меняется.
    """
    previous_data = None

    while True:
        params = {
            "ids": ",".join(CryptoData.COINS),
            "vs_currencies": CryptoData.VS_CURRENCY,
            "include_24hr_change": "true"
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(CryptoData.CR_URL, params=params)
            response.raise_for_status()
            current_data = response.json()

        # Первой итерации нет с чем сравнивать
        if previous_data is None:
            previous_data = current_data
            yield current_data
        else:
            if current_data != previous_data:      # сравниваем всё JSON
                previous_data = current_data
                yield current_data

        await asyncio.sleep(interval)


@app.websocket("/ws/crypto")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        async for data in crypto_price_watcher(interval=5):
            await manager.broadcast(data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
