from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Smart Education Assessment Service"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "sqlite+pysqlite:///./assessment.db"

    JWT_JWKS_URL: str = "http://localhost:8001/.well-known/jwks.json"
    JWT_ISSUER: str = "http://localhost:8001"
    JWT_AUDIENCE: str = "smart-education-api"
    JWT_ALGORITHMS: list[str] = ["RS256"]
    JWKS_CACHE_SECONDS: int = 300

    ACADEMIC_SERVICE_BASE_URL: str = "http://localhost:8002"
    ACADEMIC_SERVICE_TIMEOUT_SECONDS: float = 5.0

    NOTIFICATION_SERVICE_BASE_URL: str = "http://localhost:8005"
    NOTIFICATION_INTERNAL_EVENT_TOKEN: str = "change-me"
    OUTBOX_BATCH_SIZE: int = 50

    DEFAULT_ATTEMPT_LIMIT: int = 1
    DEFAULT_PASS_PERCENT: float = 50.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
