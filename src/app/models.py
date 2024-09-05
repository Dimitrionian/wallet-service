import logging
import typing
import sqlalchemy as sa

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Enum

from app.custom_types import TransactionType

logger = logging.getLogger(__name__)


METADATA: typing.Final = sa.MetaData()

transaction_type_enum = Enum(TransactionType, name="transactiontype")


class Base(DeclarativeBase):
    metadata = METADATA


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    balance = Column(Numeric(precision=10, scale=2), default=0.00)
    transactions = relationship("Transaction", back_populates="user")


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(precision=10, scale=2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", back_populates="transactions")
    type = Column(transaction_type_enum, nullable=False)
    transaction_id = Column(String, unique=True, nullable=False)
