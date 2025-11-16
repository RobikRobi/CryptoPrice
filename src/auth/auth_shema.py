import datetime
from pydantic import BaseModel, EmailStr


class RegUser(BaseModel):
    login: str
    email: EmailStr
    password: str | bytes
    dob: datetime.date


class UserShema(BaseModel):
    login: str
    email: EmailStr

class LoginUser(BaseModel):
    login: str
    password: str   