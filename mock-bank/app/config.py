from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent/".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    database_user: str
    database_port: str
    database_host: str
    database_name: str
    database_password: SecretStr

settings = Settings()