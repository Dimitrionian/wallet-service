from pydantic_settings import BaseSettings
from pydantic import field_validator
from pydantic import FieldValidationInfo


class Settings(BaseSettings):
    scheme: str
    name: str
    user: str
    password: str
    host: str
    port: str
    db_dsn: str = None

    service_name: str = "Wallet API"
    debug: bool = False

    # def __init__(self, scheme: str):
    #     self.scheme = scheme if scheme is not None else
    #     super().__init__(scheme=scheme)

    @field_validator("db_dsn", mode="before")
    def assemble_dsn(cls, v, info: FieldValidationInfo):
        if isinstance(v, str):
            return v

        return f"{info.data['scheme']}://{info.data['user']}:{info.data['password']}@{info.data['host']}:" \
               f"{info.data['port']}/{info.data['name']}"

    model_config = {
        "env_file": ".env",
    }
