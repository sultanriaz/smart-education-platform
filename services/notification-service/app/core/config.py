from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Smart Education Notification Service"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = (
        "postgresql+psycopg://notification:notification@localhost:5438/notification_db"
    )

    JWT_JWKS_URL: str = "http://localhost:8001/.well-known/jwks.json"
    JWT_ISSUER: str = "http://localhost:8001"
    JWT_AUDIENCE: str = "smart-education-api"
    JWT_ALGORITHM: str = "RS256"
    JWT_JWKS_CACHE_SECONDS: int = 300
    JWT_JWKS_STALE_SECONDS: int = 900

    IDENTITY_SERVICE_BASE_URL: str = "http://localhost:8001"
    IDENTITY_SERVICE_TIMEOUT_SECONDS: float = 5.0
    IDENTITY_SERVICE_TOKEN: str | None = None

    ACADEMIC_SERVICE_BASE_URL: str = "http://localhost:8002"
    ACADEMIC_SERVICE_TIMEOUT_SECONDS: float = 5.0
    ACADEMIC_SERVICE_TOKEN: str | None = None
    ACADEMIC_SECTION_ROSTER_PATH_TEMPLATE: str = "/api/v1/sections/{section_id}/roster"

    INTERNAL_EVENT_TOKEN: str = "CHANGE_ME_INTERNAL_EVENT_TOKEN"

    TASK_MODE: str = "inline"
    REDIS_URL: str = "redis://localhost:6380/0"

    EMAIL_PROVIDER: str = "console"
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_FROM_EMAIL: str = "no-reply@example.edu"
    SMTP_USE_TLS: bool = False

    DEFAULT_EMAIL_ENABLED: bool = False
    DEFAULT_IN_APP_ENABLED: bool = True
    MAX_PAGE_SIZE: int = 200

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
