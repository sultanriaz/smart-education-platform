from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Smart Education Platform Operations Service"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "sqlite+pysqlite:///./platform.db"
    REDIS_URL: str = "redis://localhost:6381/0"

    JWT_JWKS_URL: str = "http://localhost:8001/.well-known/jwks.json"
    JWT_ISSUER: str = "http://localhost:8001"
    JWT_AUDIENCE: str = "smart-education-api"
    JWT_ALGORITHMS: list[str] = ["RS256"]
    JWKS_CACHE_SECONDS: int = 300
    JWKS_STALE_GRACE_SECONDS: int = 900

    INTERNAL_EVENT_TOKEN: str = "change-me"
    SERVICE_INTERNAL_TOKEN: str = "change-me"

    DEFAULT_SERVICE_TIMEOUT_SECONDS: float = 3.0
    SEARCH_MAX_RESULTS: int = 100
    SUPPORT_DEFAULT_PRIORITY: str = "MEDIUM"
    JOB_MAX_RETRIES: int = 3

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
