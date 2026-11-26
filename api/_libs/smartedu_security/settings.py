from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SecuritySettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    environment: str = Field(default="development", alias="ENVIRONMENT")

    password_min_length: int = Field(default=12, ge=10, le=128, alias="PASSWORD_MIN_LENGTH")
    password_max_length: int = Field(default=128, ge=32, le=1024, alias="PASSWORD_MAX_LENGTH")

    login_failure_window_seconds: int = Field(
        default=900, ge=60, alias="LOGIN_FAILURE_WINDOW_SECONDS"
    )
    login_max_failures: int = Field(default=5, ge=3, le=50, alias="LOGIN_MAX_FAILURES")
    login_lock_seconds: int = Field(default=900, ge=60, alias="LOGIN_LOCK_SECONDS")

    password_reset_ttl_seconds: int = Field(
        default=1800, ge=300, le=86400, alias="PASSWORD_RESET_TTL_SECONDS"
    )
    email_verification_ttl_seconds: int = Field(
        default=86400, ge=900, le=604800, alias="EMAIL_VERIFICATION_TTL_SECONDS"
    )

    auth_redis_url: str = Field(
        default="redis://redis-durable:6379/2", alias="AUTH_SECURITY_REDIS_URL"
    )
    security_token_pepper: str = Field(
        default="development-only-change-me",
        alias="SECURITY_TOKEN_PEPPER",
    )
    security_notification_encryption_key: str = Field(
        default="",
        alias="SECURITY_NOTIFICATION_ENCRYPTION_KEY",
    )

    trusted_frontend_origins: str = Field(
        default="http://localhost:5173,http://localhost:3000",
        alias="TRUSTED_FRONTEND_ORIGINS",
    )
    trusted_hosts: str = Field(default="localhost,127.0.0.1", alias="TRUSTED_HOSTS")

    refresh_cookie_name: str = Field(default="sep_refresh", alias="REFRESH_COOKIE_NAME")
    refresh_cookie_path: str = Field(default="/api/v1/identity/auth", alias="REFRESH_COOKIE_PATH")
    refresh_cookie_secure: bool = Field(default=False, alias="REFRESH_COOKIE_SECURE")
    refresh_cookie_samesite: str = Field(default="strict", alias="REFRESH_COOKIE_SAMESITE")
    refresh_cookie_max_age_seconds: int = Field(
        default=604800, ge=300, alias="REFRESH_COOKIE_MAX_AGE_SECONDS"
    )

    max_upload_bytes: int = Field(default=25 * 1024 * 1024, ge=1024, alias="MAX_UPLOAD_BYTES")
    clamav_host: str = Field(default="clamav", alias="CLAMAV_HOST")
    clamav_port: int = Field(default=3310, ge=1, le=65535, alias="CLAMAV_PORT")
    malware_scan_required: bool = Field(default=False, alias="MALWARE_SCAN_REQUIRED")
    require_email_verification: bool = Field(default=False, alias="REQUIRE_EMAIL_VERIFICATION")

    @property
    def frontend_origins(self) -> tuple[str, ...]:
        return tuple(
            item.strip().rstrip("/")
            for item in self.trusted_frontend_origins.split(",")
            if item.strip()
        )

    @property
    def host_allowlist(self) -> tuple[str, ...]:
        return tuple(item.strip() for item in self.trusted_hosts.split(",") if item.strip())
