from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Smart Education Learning Service"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+psycopg://learning:learning@localhost:5440/learning_db"

    JWT_JWKS_URL: str = "http://localhost:8001/.well-known/jwks.json"
    JWT_ISSUER: str = "http://localhost:8001"
    JWT_AUDIENCE: str = "smart-education-api"
    JWT_ALGORITHMS: list[str] = ["RS256"]
    JWT_JWKS_CACHE_TTL_SECONDS: int = 300

    ACADEMIC_SERVICE_BASE_URL: str = "http://localhost:8002"
    ACADEMIC_SERVICE_TIMEOUT_SECONDS: float = 5.0
    ACADEMIC_INTERNAL_TOKEN: str = "change-me-academic-internal-token"

    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_PATH: Path = Path("./data/objects")
    MAX_UPLOAD_BYTES: int = 25 * 1024 * 1024
    MALWARE_SCAN_REQUIRED: bool = False
    CLAMAV_HOST: str = "clamav"
    CLAMAV_PORT: int = 3310
    ALLOWED_UPLOAD_MIME_TYPES: list[str] = [
        "application/pdf",
        "text/plain",
        "image/png",
        "image/jpeg",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ]

    S3_ENDPOINT_URL: str | None = None
    S3_REGION: str = "us-east-1"
    S3_BUCKET: str = "learning-resources"
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    S3_USE_SSL: bool = False

    NOTIFICATION_SERVICE_BASE_URL: str = "http://localhost:8005"
    NOTIFICATION_INTERNAL_EVENT_TOKEN: str = "change-me-notification-internal-token"
    OUTBOX_BATCH_SIZE: int = 50

    RECOMMENDATION_RECENT_DAYS: int = 14

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
