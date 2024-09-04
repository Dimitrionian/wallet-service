import pydantic
from pydantic import BaseModel, EmailStr
from decimal import Decimal

from app.custom_types import TransactionType


class Base(BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)


class TokenRequestForm(Base):
    email: EmailStr
    password: str | None


class User(Base):
    id: int
    name: str | None
    email: EmailStr


class UserBalance(Base):
    amount: Decimal


class UserCreate(Base):
    name: str | None
    email: EmailStr
    password: str


class TransactionAdd(Base):
    amount: Decimal
    type: TransactionType


class Transaction(Base):
    transaction_id: str
    amount: Decimal
    type: TransactionType
