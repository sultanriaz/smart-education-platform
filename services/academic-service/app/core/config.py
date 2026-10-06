from __future__ import annotations

from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "Smart Education Academic Service"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "postgresql+psycopg://academic:academic@localhost:5435/academic_db"
    JWT_ISSUER: str = "http://localhost:8001"
    JWT_ACCESS_AUDIENCE: str = "smart-education-api"
    JWT_JWKS_URL: str = "http://localhost:8001/.well-known/jwks.json"
    JWT_LEEWAY_SECONDS: int = Field(default=5, ge=0, le=30)
    JWT_JWKS_CACHE_SECONDS: int = Field(default=300, ge=1, le=3600)
    JWT_JWKS_TIMEOUT_SECONDS: float = Field(default=5, gt=0, le=10)
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    @model_validator(mode="after")
    def validate_contract(self) -> Settings:
        if make_url(self.DATABASE_URL).get_backend_name() != "postgresql":
            raise ValueError("Academic Service requires its own PostgreSQL database.")
        if not self.JWT_ISSUER or not self.JWT_ACCESS_AUDIENCE:
            raise ValueError("JWT issuer and audience must be configured.")
        if not self.JWT_JWKS_URL.startswith(("http://", "https://")):
            raise ValueError("JWKS URL must be a trusted HTTP(S) endpoint.")
        if self.ENVIRONMENT == "production" and not self.JWT_ISSUER.startswith("https://"):
            raise ValueError("Production JWT issuer must use HTTPS.")
        if not self.API_V1_PREFIX.startswith("/"):
            raise ValueError("API prefix must start with /.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
