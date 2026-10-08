from __future__ import annotations

import contextvars
import re
import uuid

_request_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "smartedu_request_id", default=None
)
_correlation_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "smartedu_correlation_id", default=None
)
_causation_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "smartedu_causation_id", default=None
)

_SAFE_ID = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


def sanitize_context_id(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    if not _SAFE_ID.fullmatch(value):
        return None
    return value


def new_context_id() -> str:
    return str(uuid.uuid4())


def set_request_context(
    request_id: str,
    correlation_id: str,
    causation_id: str | None = None,
) -> tuple[contextvars.Token, contextvars.Token, contextvars.Token]:
    return (
        _request_id.set(request_id),
        _correlation_id.set(correlation_id),
        _causation_id.set(causation_id),
    )


def reset_request_context(
    tokens: tuple[contextvars.Token, contextvars.Token, contextvars.Token],
) -> None:
    request_token, correlation_token, causation_token = tokens
    _request_id.reset(request_token)
    _correlation_id.reset(correlation_token)
    _causation_id.reset(causation_token)


def get_request_id() -> str | None:
    return _request_id.get()


def get_correlation_id() -> str | None:
    return _correlation_id.get()


def get_causation_id() -> str | None:
    return _causation_id.get()


def ensure_correlation_id() -> str:
    current = get_correlation_id()
    if current:
        return current
    value = new_context_id()
    _correlation_id.set(value)
    return value
