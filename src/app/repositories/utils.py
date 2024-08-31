import bcrypt
from passlib.context import CryptContext
from sqlalchemy import URL

from app.settings import Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Utility function for password hashing and verification
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def get_dsn(scheme: str | None = None) -> URL:
    settings = Settings(scheme=scheme)
    return settings.db_dsn
