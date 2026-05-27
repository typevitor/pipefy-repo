from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./app.db"
    pipefy_token: str = ""
    pipefy_pipe_id: int = 0
    pipefy_webhook_secret: str = ""
    pipefy_endpoint: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
