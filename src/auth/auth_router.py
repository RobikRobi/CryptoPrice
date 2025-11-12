from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.UserModel import User

from src.db import get_session
from src.auth.auth_shema import RegUser
from src.auth.auth_utilits import decode_password, create_access_token




app = APIRouter(prefix="/users", tags=["Users"])

@app.post("/reg")
async def reg_user(data:RegUser, session: AsyncSession = Depends(get_session)):
    stmt = select(User).where(User.login == data.login)
    isUserEx = await session.scalar(stmt)
    if isUserEx:
        raise HTTPException(status_code=411, detail={
        "status":411,
        "data":"user is exists"
        })
        
    data_dict = data.model_dump()
        
    data_dict["password"] = await decode_password(password=data.password)
    
    user = User(**data_dict)
    session.add(user) 
    await session.flush()

    user_id = user.id
        
    await session.commit()
        
    user_token = await create_access_token(user_id=user_id)
    data_dict["token"] = user_token  
        
    return data_dict