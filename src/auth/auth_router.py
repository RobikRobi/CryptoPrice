from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.UserModel import User

from src.db import get_session
from src.auth.auth_shema import RegUser, UserShema, LoginUser
from src.auth.auth_utilits import decode_password, create_access_token, check_password
from src.get_current_user import get_current_user




app = APIRouter(prefix="/users", tags=["Users"])

# регистрация пользователя
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

# авторизация
@app.post("/login")
async def auth_user(data: LoginUser, session: AsyncSession = Depends(get_session)):
    stmt = select(User).where(User.login == data.login)
    user = await session.scalar(stmt)
    if user:
        if await check_password(password=data.password, old_password=user.password):
            user_token = await create_access_token(user_id=user.id)
            return {"token": user_token}
    raise HTTPException(status_code=401, detail={
                "details":"user is not exists",
                "status":401
        })

# получение данных пользователя
@app.get("/me", response_model=UserShema)
def get_me(me: User = Depends(get_current_user)):
            return me


# получение всех зарегистрированных пользователей
@app.get("/all_users", response_model=list[UserShema])
async def get_users(session: AsyncSession = Depends(get_session)):
    users = await session.scalars(select(User))
    return users.all()

