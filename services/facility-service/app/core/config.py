from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Smart Education Facility Service"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+psycopg://facility:facility@localhost:5439/facility_db"

    JWT_JWKS_URL: str = "http://localhost:8001/.well-known/jwks.json"
    JWT_ISSUER: str = "http://localhost:8001"
    JWT_AUDIENCE: str = "smart-education-api"
    JWT_ALGORITHM: str = "RS256"
    JWT_JWKS_CACHE_SECONDS: int = 300
    JWT_JWKS_STALE_SECONDS: int = 900

    INTERNAL_SERVICE_TOKEN: str = "CHANGE_ME_INTERNAL_SERVICE_TOKEN"

    NOTIFICATION_SERVICE_BASE_URL: str = "http://localhost:8005"
    NOTIFICATION_INTERNAL_EVENT_TOKEN: str | None = None
    OUTBOX_RELAY_BATCH_SIZE: int = 100
    OUTBOX_RELAY_INTERVAL_SECONDS: float = 2.0

    MAX_BOOKING_DURATION_HOURS: int = 8
    MIN_BOOKING_NOTICE_MINUTES: int = 0
    CANCELLATION_CUTOFF_MINUTES: int = 30
    PENDING_BOOKINGS_RESERVE_SLOT: bool = True
    MAX_PAGE_SIZE: int = 200

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
