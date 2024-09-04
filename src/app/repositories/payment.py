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
from app.repositories.utils import hash_password
from app.schemas import TransactionAdd


class PaymentRepository:

    def __init__(self, db_session_maker: async_sessionmaker[AsyncSessionType]):
        self.db_session_maker = db_session_maker

    async def create_user(self, data: schemas.UserCreate, payment_repo: Self) -> User:
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

    async def add_transaction(self, data: TransactionAdd, payment_repo: Self, user: User) -> Transaction:
        async with payment_repo.db_session_maker() as session:
            async with session.begin():
                tx_id = str(uuid4())
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
                session.add(new_transaction)
            await session.commit()

        return new_transaction
