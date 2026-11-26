from __future__ import annotations

from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware

try:
    from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
except ImportError:  # pragma: no cover
    HTTPSRedirectMiddleware = None  # type: ignore[assignment]


def install_backend_security(
    app: FastAPI,
    *,
    allowed_hosts: tuple[str, ...],
    force_https: bool = False,
) -> None:
    if allowed_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=list(allowed_hosts),
        )
    if force_https:
        if HTTPSRedirectMiddleware is None:
            raise RuntimeError("HTTPSRedirectMiddleware is unavailable")
        app.add_middleware(HTTPSRedirectMiddleware)


def no_store_headers() -> dict[str, str]:
    return {
        "Cache-Control": "no-store, max-age=0",
        "Pragma": "no-cache",
    }
