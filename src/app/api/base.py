from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession as AsyncSessionType,
)
from sqlalchemy import URL

from app.settings import Settings
from app.repositories import PaymentRepository
from custom_types import FAST_API_SCHEME


def get_dsn(scheme: str | None = None) -> URL:
    settings = Settings(scheme=scheme)
    return settings.db_dsn


def get_settings() -> Settings:
    raise NotImplementedError


engine = create_async_engine(get_dsn(scheme=FAST_API_SCHEME), echo=True)
async_session = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSessionType
)


async def get_db() -> async_sessionmaker[AsyncSessionType]:
    async with async_session() as session:
        yield session


def get_payment_repo(
    db: async_sessionmaker[AsyncSessionType] = Depends(get_db),
) -> PaymentRepository:
    return PaymentRepository(
        db_session_maker=db,
    )
