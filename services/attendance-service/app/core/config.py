from __future__ import annotations

from functools import lru_cache
from urllib.parse import urlparse

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Smart Education Attendance Service"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "postgresql+psycopg://attendance:attendance@localhost:5436/attendance_db"
    SCHEDULING_SERVICE_BASE_URL: str = "http://localhost:8004"
    SCHEDULING_SERVICE_TIMEOUT_SECONDS: float = Field(default=4, gt=0, le=30)
    VERIFY_SCHEDULE_OCCURRENCES: bool = False
    ACADEMIC_SERVICE_BASE_URL: str = "http://localhost:8002"
    ACADEMIC_SERVICE_TIMEOUT_SECONDS: float = Field(default=5, gt=0, le=30)
    ACADEMIC_SERVICE_MAX_PAGES: int = Field(default=100, ge=1, le=1000)
    JWT_ISSUER: str = "http://localhost:8001"
    JWT_ACCESS_AUDIENCE: str = "smart-education-api"
    JWT_JWKS_URL: str = "http://localhost:8001/.well-known/jwks.json"
    JWT_LEEWAY_SECONDS: int = Field(default=5, ge=0, le=30)
    JWT_JWKS_CACHE_SECONDS: int = Field(default=300, ge=1, le=3600)
    JWT_JWKS_TIMEOUT_SECONDS: float = Field(default=5, gt=0, le=10)
    LOW_ATTENDANCE_THRESHOLD_PERCENT: float = Field(default=75, ge=0, le=100)
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    @model_validator(mode="after")
    def validate_contract(self) -> Settings:
        if make_url(self.DATABASE_URL).get_backend_name() != "postgresql":
            raise ValueError("Attendance requires a service-owned PostgreSQL database.")
        for url in (self.ACADEMIC_SERVICE_BASE_URL, self.JWT_JWKS_URL, self.JWT_ISSUER):
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username:
                raise ValueError("Service URLs and issuer must be trusted HTTP(S) configuration.")
        if not self.JWT_ACCESS_AUDIENCE:
            raise ValueError("JWT access audience cannot be empty.")
        if self.ENVIRONMENT == "production" and not self.JWT_ISSUER.startswith("https://"):
            raise ValueError("Production issuer must use HTTPS.")
        if self.API_V1_PREFIX != "/api/v1":
            raise ValueError("Sprint 3 APIs use /api/v1.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
