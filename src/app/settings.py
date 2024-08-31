from pydantic_settings import BaseSettings
from pydantic import field_validator
from pydantic import FieldValidationInfo


class Settings(BaseSettings):
    name: str
    user: str
    password: str
    host: str
    port: str
    db_dsn: str = None

    service_name: str = "Wallet API"
    debug: bool = False

    @field_validator("db_dsn", mode="before")
    def assemble_dsn(cls, v, info: FieldValidationInfo):
        if isinstance(v, str):
            return v

        return f"postgresql+asyncpg://{info.data['user']}:{info.data['password']}@{info.data['host']}:" \
               f"{info.data['port']}/{info.data['name']}"

    model_config = {
        "env_file": ".env",
    }
