from pydantic import BaseModel, Field, condecimal, constr
from decimal import Decimal
from typing import Literal, Optional

Amount = condecimal(max_digits=28, decimal_places=8)
Price = condecimal(max_digits=28, decimal_places=8)




class OrderCreate(BaseModel):
    pair: constr(min_length=3)  # "BTC/USD"
    side: Literal["buy", "sell"]
    type: Literal["limit", "market"]
    amount: Amount
    price: Optional[Price] = None  # for limit required; for market ignored

class OrderOut(BaseModel):
    id: int
    pair: str
    side: str
    type: str
    price: Optional[Decimal]
    amount: Decimal
    filled: Decimal
    status: str