from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Smart Education Scheduling Service"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "postgresql+psycopg://scheduling:scheduling@localhost:5437/scheduling_db"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    JWT_JWKS_URL: str = "http://localhost:8001/.well-known/jwks.json"
    JWT_ISSUER: str = "http://localhost:8001"
    JWT_AUDIENCE: str = "smart-education-api"
    JWT_ALGORITHM: str = "RS256"
    JWT_JWKS_CACHE_SECONDS: int = 300
    JWT_JWKS_STALE_SECONDS: int = 900

    ACADEMIC_SERVICE_BASE_URL: str = "http://localhost:8002"
    ACADEMIC_SERVICE_TIMEOUT_SECONDS: float = 3.0
    ACADEMIC_SECTION_PATH_TEMPLATE: str = "/api/v1/sections/{section_id}"
    ACADEMIC_TEACHER_ASSIGNMENT_PATH: str = "/api/v1/teacher-assignments/validate"
    ACADEMIC_STUDENT_ENROLLMENT_PATH: str = "/api/v1/enrollments/validate"
    ACADEMIC_STUDENT_SECTIONS_PATH_TEMPLATE: str = "/api/v1/students/{student_user_id}/sections"

    MAX_TIMETABLE_RANGE_DAYS: int = 62
    DEFAULT_TIMEZONE: str = "UTC"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
