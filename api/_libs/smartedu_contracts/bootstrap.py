from __future__ import annotations

from fastapi import FastAPI

from .errors import install_error_handlers
from .idempotency import IdempotencyMiddleware, IdempotencyStore
from .middleware import install_request_context


def install_platform_contracts(
    app: FastAPI,
    *,
    service_name: str,
    idempotency_store: IdempotencyStore | None = None,
    idempotency_excluded_path_prefixes: tuple[str, ...] = (),
    expose_internal_errors: bool = False,
) -> None:
    if idempotency_store is not None:
        app.add_middleware(
            IdempotencyMiddleware,
            store=idempotency_store,
            excluded_path_prefixes=idempotency_excluded_path_prefixes,
        )
    install_error_handlers(
        app,
        expose_internal_errors=expose_internal_errors,
    )
    install_request_context(app, service_name=service_name)
