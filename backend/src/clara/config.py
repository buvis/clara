from functools import lru_cache

from pydantic import PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "CLARA"
    debug: bool = False
    secret_key: SecretStr

    database_url: PostgresDsn
    redis_url: RedisDsn = "redis://localhost:6379/0"

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30
    cookie_domain: str | None = None
    cookie_secure: bool = True
    cookie_httponly: bool = True
    cookie_samesite: str = "lax"

    cors_origins: list[str] = []

    storage_path: str = "./uploads"

    @property
    def async_database_url(self) -> str:
        return str(self.database_url).replace(
            "postgresql://", "postgresql+asyncpg://"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
