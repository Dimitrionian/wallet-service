import bcrypt
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import URL
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from starlette import status
from sqlalchemy.future import select

from datetime import datetime, timedelta

from app.settings import Settings
from app.models import User

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Utility function for password hashing and verification
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(db: 'PaymentRepository', email: str):
    async with db() as session:
        async with session.begin():
            result = await session.execute(select(User).filter_by(email=email))
            user = result.scalars().first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_user(db: 'PaymentRepository', email: str, password: str):
    user = await get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_dsn(scheme: str | None = None) -> URL:
    settings = Settings(scheme=scheme)
    return settings.db_dsn
