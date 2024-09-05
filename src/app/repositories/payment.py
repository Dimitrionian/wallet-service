from typing import Self
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession as AsyncSessionType,
)

from app import schemas
from app.models import User, Transaction
from app.repositories.utils import hash_password, change_balance, balance_strategy
from app.schemas import TransactionAdd


class PaymentRepository:

    def __init__(self, db_session_maker: async_sessionmaker[AsyncSessionType]):
        self.db_session_maker = db_session_maker

    async def create_user(self, payment_repo: Self, data: schemas.UserCreate) -> User:
        async with payment_repo.db_session_maker() as session:
            async with session.begin():
                result = await session.execute(select(User).filter_by(email=data.email))
                existing_user = result.scalars().first()
                if existing_user:
                    raise HTTPException(status_code=409, detail="User already exists")

                hashed_password = hash_password(data.password)
                new_user = User(name=data.name, email=data.email, hashed_password=hashed_password)
                session.add(new_user)
            await session.commit()

        return new_user

    async def get_user_balance(self, payment_repo: Self, user_id: str, ts: int):
        async with payment_repo.db_session_maker() as session:
            async with session.begin():
                balance_method = balance_strategy[bool(ts)]
                balance = await balance_method(payment_repo, user_id=user_id, ts=ts)
            await session.commit()

        return balance

    async def add_transaction(self, payment_repo: Self, data: TransactionAdd, user: User) -> Transaction:
        async with payment_repo.db_session_maker() as session:
            async with session.begin():
                tx_id = str(uuid4())
                # Check if a transaction with such id already exists
                result = await session.execute(select(Transaction).filter_by(transaction_id=tx_id))
                existing_transaction = result.scalars().first()
                if existing_transaction:
                    raise HTTPException(status_code=409, detail="Transaction already exists")

                new_transaction = Transaction(
                    amount=data.amount,
                    type=data.type,
                    transaction_id=tx_id,
                    user=user
                )
                await change_balance(user, data)
                session.add(new_transaction)
            await session.commit()

        return new_transaction

    async def get_transaction(self, payment_repo: Self, tx_id: str) -> Transaction:
        async with payment_repo.db_session_maker() as session:
            async with session.begin():
                result = await session.execute(select(Transaction).filter_by(transaction_id=tx_id))
                transaction = result.scalars().first()
                if not transaction:
                    raise HTTPException(status_code=404, detail="Transaction not found")

            await session.commit()

        return transaction
