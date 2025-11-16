import requests as r
from src.config import CryptoData
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from src.client.WebsocetConnect import ConnectionManager
from src.db import get_session
from src.client.crypto_price_watcher import crypto_price_watcher
from src.get_current_user import get_current_user
from src.models.UserModel import User
from src.models.AccountModel import Account
from src.client.client_shema import AccountCreate



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
