import logging
import typing
import sqlalchemy as sa

from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)


METADATA: typing.Final = sa.MetaData()


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
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Numeric(precision=10, scale=2))
    description = Column(String)
    user = relationship("User", back_populates="transactions")
