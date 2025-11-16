from sqlalchemy import Numeric, Column, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.enum.CurrencyEnum import CurrencyType
from decimal import Decimal
from typing import TYPE_CHECKING
from src.db import Base

if TYPE_CHECKING:
    from src.models.UserModel import User

# модель таблицы для сохранения данных о счетах
class Account(Base):
    __tablename__ = "accounts"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    currency: Mapped[CurrencyType] = mapped_column(nullable=False, default=CurrencyType.USD)
    available: Mapped[Decimal] = mapped_column(Numeric(28, 8), default=0)
    locked: Mapped[Decimal] = mapped_column(Numeric(28, 8), default=0)

    owner = relationship("User", back_populates="accounts")