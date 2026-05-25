from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./app.db"
    pipefy_token: str
    pipefy_pipe_id: int
    pipefy_webhook_secret: str
    pipefy_field_nome: str = "employee_name"
    pipefy_field_email: str = "email"
    pipefy_field_patrimonio: str = "patrimonio"
    pipefy_field_status: str = "status"
    pipefy_field_prioridade: str = "prioridade"


@lru_cache
def get_settings() -> Settings:
    return Settings()
