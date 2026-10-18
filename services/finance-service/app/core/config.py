from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Smart Education Finance Service"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+psycopg://finance_svc:finance_dev_secret@localhost:15432/finance_db"

    JWT_JWKS_URL: str = "http://localhost:8001/.well-known/jwks.json"
    JWT_ISSUER: str = "http://localhost:8001"
    JWT_AUDIENCE: str = "smart-education-api"
    JWT_ALGORITHMS: list[str] = ["RS256"]
    JWKS_CACHE_SECONDS: int = 300

    INTERNAL_EVENT_TOKEN: str = "change-me"
    ACADEMIC_SERVICE_BASE_URL: str = "http://localhost:8002"
    IDENTITY_SERVICE_BASE_URL: str = "http://localhost:8001"

    DEFAULT_CURRENCY: str = "PKR"
    DEFAULT_TIMEZONE: str = "Asia/Karachi"
    LATE_FEE_AMOUNT: float = 500.00
    LATE_FEE_GRACE_DAYS: int = 10
    PAYMENT_WEBHOOK_SECRET: str = "demo-payment-webhook-secret-wave17"

    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 200

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
