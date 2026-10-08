from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .constants import (
    CAUSATION_ID_HEADER,
    CORRELATION_ID_HEADER,
    REQUEST_ID_HEADER,
    SERVICE_NAME_HEADER,
)
from .context import (
    new_context_id,
    reset_request_context,
    sanitize_context_id,
    set_request_context,
)


class RequestContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, service_name: str):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = sanitize_context_id(request.headers.get(REQUEST_ID_HEADER)) or new_context_id()
        correlation_id = (
            sanitize_context_id(request.headers.get(CORRELATION_ID_HEADER)) or request_id
        )
        causation_id = sanitize_context_id(request.headers.get(CAUSATION_ID_HEADER))

        tokens = set_request_context(request_id, correlation_id, causation_id)
        request.state.request_id = request_id
        request.state.correlation_id = correlation_id
        request.state.causation_id = causation_id

        try:
            response = await call_next(request)
        finally:
            reset_request_context(tokens)

        response.headers[REQUEST_ID_HEADER] = request_id
        response.headers[CORRELATION_ID_HEADER] = correlation_id
        response.headers[SERVICE_NAME_HEADER] = self.service_name
        return response


def install_request_context(app: FastAPI, *, service_name: str) -> None:
    app.add_middleware(RequestContextMiddleware, service_name=service_name)
