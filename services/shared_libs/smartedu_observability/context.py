from __future__ import annotations

import contextvars
import uuid
from dataclasses import dataclass

_request_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id",
    default="",
)
_correlation_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id",
    default="",
)


@dataclass(frozen=True, slots=True)
class RequestContext:
    request_id: str
    correlation_id: str


def new_id() -> str:
    return str(uuid.uuid4())


def set_request_context(
    *,
    request_id: str | None = None,
    correlation_id: str | None = None,
) -> RequestContext:
    request_id = (request_id or "").strip() or new_id()
    correlation_id = (correlation_id or "").strip() or request_id
    _request_id.set(request_id)
    _correlation_id.set(correlation_id)
    return RequestContext(
        request_id=request_id,
        correlation_id=correlation_id,
    )


def get_request_id() -> str:
    return _request_id.get()


def get_correlation_id() -> str:
    return _correlation_id.get()


def clear_request_context() -> None:
    _request_id.set("")
    _correlation_id.set("")
