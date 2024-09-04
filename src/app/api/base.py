from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession as AsyncSessionType,
)
from sqlalchemy import URL
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from fastapi import Depends, HTTPException, status

from app.settings import Settings
from app.repositories import PaymentRepository
from app.custom_types import FAST_API_SCHEME
from app.repositories.utils import SECRET_KEY, ALGORITHM, oauth2_scheme, get_user


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


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(db, email)
    if user is None:
        raise credentials_exception
    return user
