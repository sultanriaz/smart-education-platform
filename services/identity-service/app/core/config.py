from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Smart Education Identity Service"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"
    DATABASE_URL: str = "postgresql+psycopg://identity:identity@localhost:5434/identity_db"
    JWT_ALGORITHM: Literal["RS256"] = "RS256"
    JWT_PRIVATE_KEY_FILE: Path = Path(".secrets/identity-private.pem")
    JWT_KEY_ID: str = Field(default="identity-dev-1", min_length=1)
    JWT_PREVIOUS_PUBLIC_KEYS: dict[str, Path] = Field(default_factory=dict)
    JWT_ISSUER: str = "http://localhost:8001"
    JWT_ACCESS_AUDIENCE: str = Field(default="smart-education-api", min_length=1)
    JWT_REFRESH_AUDIENCE: str = Field(default="identity-service", min_length=1)
    JWT_LEEWAY_SECONDS: int = Field(default=5, ge=0, le=60)
    ACCESS_TOKEN_MINUTES: int = Field(default=15, ge=1, le=60)
    REFRESH_TOKEN_DAYS: int = Field(default=14, ge=1, le=90)
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    BOOTSTRAP_ADMIN_EMAIL: str | None = None
    BOOTSTRAP_ADMIN_PASSWORD: str | None = None
    BOOTSTRAP_ADMIN_NAME: str = "Platform Administrator"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_authentication(self):
        if not self.JWT_ISSUER.startswith(("http://", "https://")):
            raise ValueError("JWT_ISSUER must be an absolute HTTP(S) issuer URL.")
        if self.JWT_ACCESS_AUDIENCE == self.JWT_REFRESH_AUDIENCE:
            raise ValueError("Access and refresh audiences must be different.")
        if self.JWT_KEY_ID in self.JWT_PREVIOUS_PUBLIC_KEYS:
            raise ValueError("The active key ID cannot also be a previous key ID.")
        if any(not kid.strip() for kid in self.JWT_PREVIOUS_PUBLIC_KEYS):
            raise ValueError("Previous public keys must have nonempty key IDs.")
        if self.ENVIRONMENT not in {"development", "test"}:
            if not self.JWT_ISSUER.startswith("https://"):
                raise ValueError("Production JWT_ISSUER must use HTTPS.")
            if self.JWT_KEY_ID == "identity-dev-1":
                raise ValueError("Production requires an explicitly configured JWT_KEY_ID.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
