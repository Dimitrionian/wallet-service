from typing import Self

from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession as AsyncSessionType,
)

from app import schemas
from app.models import User
from repositories.utils import hash_password


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
