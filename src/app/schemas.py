import pydantic
from pydantic import BaseModel
from decimal import Decimal


class Base(BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)


class User(Base):
    id: str
    name: str


class UserBalance(Base):
    amount: Decimal


class UserCreate(Base):
    id: str
    name: str


class TransactionAdd(Base):
    amount: Decimal


class Transaction(Base):
    hash: str
