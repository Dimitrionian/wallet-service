import pydantic
from pydantic import BaseModel, EmailStr
from decimal import Decimal


class Base(BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)


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


class Transaction(Base):
    hash: str
