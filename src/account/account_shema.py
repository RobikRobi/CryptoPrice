from pydantic import BaseModel, Field
from src.enum import CurrencyEnum



class AccountCreate(BaseModel):
    currency: CurrencyEnum
    available: float = Field(ge=0.0)

# схема для пополнения баланса счёта
class AccountUpdate(BaseModel):
    available: float = Field(ge=0.0)


class TransferSchema(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: float = Field(gt=0)