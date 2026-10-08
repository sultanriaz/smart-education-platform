from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI
from smartedu_security import (
    RedisFixedWindowLimiter,
    RedisLockoutStore,
    SecuritySettings,
    install_backend_security,
)

try:
    from redis.asyncio import Redis
except ImportError:  # pragma: no cover
    Redis = None  # type: ignore[assignment]


@lru_cache
def security_settings() -> SecuritySettings:
    settings = SecuritySettings()
    if (
        settings.environment.lower() in {"production", "prod"}
        and settings.security_token_pepper == "development-only-change-me"
    ):
        raise RuntimeError("Production SECURITY_TOKEN_PEPPER is not configured")
    if (
        settings.environment.lower() in {"production", "prod"}
        and not settings.refresh_cookie_secure
    ):
        raise RuntimeError("Production requires REFRESH_COOKIE_SECURE=true")
    if (
        settings.environment.lower() in {"production", "prod"}
        and not settings.security_notification_encryption_key
    ):
        raise RuntimeError("Production SECURITY_NOTIFICATION_ENCRYPTION_KEY is not configured")
    return settings


@lru_cache
def auth_security_redis():
    if Redis is None:
        raise RuntimeError("redis package is required for Sprint 18 auth security")
    settings = security_settings()
    return Redis.from_url(
        settings.auth_redis_url,
        decode_responses=True,
        socket_timeout=2,
        socket_connect_timeout=2,
    )


@lru_cache
def login_lockout_store() -> RedisLockoutStore:
    settings = security_settings()
    return RedisLockoutStore(
        auth_security_redis(),
        namespace="smartedu:identity:lockout",
        max_failures=settings.login_max_failures,
        failure_window_seconds=settings.login_failure_window_seconds,
        lock_seconds=settings.login_lock_seconds,
    )


@lru_cache
def identity_rate_limiter() -> RedisFixedWindowLimiter:
    return RedisFixedWindowLimiter(
        auth_security_redis(),
        namespace="smartedu:identity:rate",
    )


def install_sprint18(app: FastAPI) -> None:
    settings = security_settings()
    install_backend_security(
        app,
        allowed_hosts=settings.host_allowlist
        + (("testserver",) if settings.environment == "test" else ()),
        # TLS terminates at the public Gateway. Internal service hops can remain HTTP.
        force_https=False,
    )
