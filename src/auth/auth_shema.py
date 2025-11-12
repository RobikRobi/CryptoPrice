import datetime
from pydantic import BaseModel, EmailStr


class RegUser(BaseModel):
    login: str
    email: EmailStr
    password: str | bytes
    dob: datetime.date
