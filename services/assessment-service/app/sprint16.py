from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI
from smartedu_contracts import (
    InternalTokenSigner,
    InternalTokenVerifier,
    MemoryIdempotencyStore,
    RedisIdempotencyStore,
    install_platform_contracts,
)

SERVICE_NAME = "assessment-service"


def _environment() -> str:
    return os.getenv("ENVIRONMENT", "development").lower()


@lru_cache
def _idempotency_store():
    redis_url = os.getenv("IDEMPOTENCY_REDIS_URL", "").strip()
    if redis_url:
        try:
            from redis.asyncio import Redis
        except ImportError as exc:
            raise RuntimeError(
                "IDEMPOTENCY_REDIS_URL is set but redis package is not installed"
            ) from exc
        return RedisIdempotencyStore(
            Redis.from_url(redis_url, decode_responses=False),
            namespace=f"smartedu:idempotency:{SERVICE_NAME}",
        )

    if (
        _environment() in {"production", "prod"}
        and os.getenv("ALLOW_IN_MEMORY_IDEMPOTENCY_IN_PRODUCTION", "false").lower() != "true"
    ):
        raise RuntimeError("Production requires IDEMPOTENCY_REDIS_URL for durable idempotency")

    return MemoryIdempotencyStore()


def install_sprint16(app: FastAPI) -> None:
    install_platform_contracts(
        app,
        service_name=SERVICE_NAME,
        idempotency_store=_idempotency_store(),
        expose_internal_errors=_environment() == "development",
    )


def _read_secret(value_env: str, file_env: str) -> str:
    direct = os.getenv(value_env, "").strip()
    if direct:
        return direct.replace("\\n", "\n")

    path = os.getenv(file_env, "").strip()
    if path:
        return Path(path).read_text(encoding="utf-8")
    raise RuntimeError(f"Missing {value_env} or {file_env}")


@lru_cache
def internal_token_signer() -> InternalTokenSigner:
    return InternalTokenSigner(
        service_name=SERVICE_NAME,
        private_key_pem=_read_secret(
            "INTERNAL_SERVICE_PRIVATE_KEY_PEM",
            "INTERNAL_SERVICE_PRIVATE_KEY_FILE",
        ),
        issuer=os.getenv(
            "INTERNAL_SERVICE_TOKEN_ISSUER",
            "smart-education-internal",
        ),
        ttl_seconds=int(os.getenv("INTERNAL_SERVICE_TOKEN_TTL_SECONDS", "60")),
    )


@lru_cache
def internal_token_verifier() -> InternalTokenVerifier:
    raw = os.getenv("TRUSTED_INTERNAL_PUBLIC_KEYS_JSON", "{}")
    values = json.loads(raw)
    if not isinstance(values, dict):
        raise RuntimeError("TRUSTED_INTERNAL_PUBLIC_KEYS_JSON must be a JSON object")

    trusted = {
        str(service): str(public_key).replace("\\n", "\n") for service, public_key in values.items()
    }
    return InternalTokenVerifier(
        trusted_public_keys=trusted,
        issuer=os.getenv(
            "INTERNAL_SERVICE_TOKEN_ISSUER",
            "smart-education-internal",
        ),
    )
