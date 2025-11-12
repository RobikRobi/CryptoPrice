import jwt
import bcrypt
import datetime

from binascii import Error
from fastapi import HTTPException

from src.config import config


# хэширование пароля
async def decode_password(password: str) -> bytes:
    new_password = bcrypt.hashpw(password=password.encode(), salt=bcrypt.gensalt())
    return new_password


# проверка пароля
async def check_password(password: str, old_password: bytes) -> bool:
    return bcrypt.checkpw(password=password.encode(), hashed_password=old_password)


# создание токена
async def create_access_token(
    user_id: int,
    algorithm: str = config.auth_data.algorithm,
    private_key: str = config.auth_data.private_key.read_text()
) -> str:
    payload = {
        "user_id": user_id,
        "exec": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=config.auth_data.days)).timestamp()}
    
    token = jwt.encode(payload=payload, algorithm=algorithm, key=private_key)
    return token


async def valid_access_token(
        token, 
        algorithm:str = config.auth_data.algorithm,
        public_key:str = config.auth_data.public_key.read_text()
        ) -> dict:
        
    
        try:
            payload = jwt.decode(jwt = token, key=public_key, algorithms=[algorithm])
        except Error as e:
            raise HTTPException(status_code=401, detail={
                "token":e,
                "status":401
        })
            
        if payload.get("exec"):
            times = payload['exec']
            if times > datetime.datetime.now(datetime.timezone.utc).timestamp():
                    return int(payload["user_id"])
        raise HTTPException(status_code=404, detail={
                "token":"this token is expired",
                "status":404
        })