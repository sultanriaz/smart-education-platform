from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI
from smartedu_security import SecuritySettings, install_backend_security


@lru_cache
def security_settings() -> SecuritySettings:
    return SecuritySettings()


def install_sprint18(app: FastAPI) -> None:
    settings = security_settings()
    install_backend_security(
        app,
        allowed_hosts=settings.host_allowlist
        + (("testserver",) if settings.environment == "test" else ()),
        # Public TLS is terminated by the API Gateway.
        force_https=False,
    )
