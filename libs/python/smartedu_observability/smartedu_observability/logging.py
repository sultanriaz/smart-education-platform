from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from opentelemetry import trace

from .context import get_correlation_id, get_request_id

SENSITIVE_KEYS = frozenset(
    {
        "authorization",
        "cookie",
        "set-cookie",
        "password",
        "new_password",
        "confirm_password",
        "access_token",
        "refresh_token",
        "token",
        "secret",
        "private_key",
        "api_key",
        "encrypted_payload",
    }
)


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            if str(key).casefold() in SENSITIVE_KEYS:
                result[str(key)] = "[REDACTED]"
            else:
                result[str(key)] = _redact(item)
        return result
    if isinstance(value, (list, tuple)):
        return [_redact(item) for item in value]
    return value


def _trace_fields() -> tuple[str, str]:
    span = trace.get_current_span()
    context = span.get_span_context()
    if not context.is_valid:
        return "", ""
    return f"{context.trace_id:032x}", f"{context.span_id:016x}"


class JsonFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        service_name: str,
        environment: str,
        service_version: str,
    ):
        super().__init__()
        self.service_name = service_name
        self.environment = environment
        self.service_version = service_version

    def format(self, record: logging.LogRecord) -> str:
        trace_id, span_id = _trace_fields()
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
            "environment": self.environment,
            "service_version": self.service_version,
            "request_id": get_request_id() or None,
            "correlation_id": get_correlation_id() or None,
            "trace_id": trace_id or None,
            "span_id": span_id or None,
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        extras = getattr(record, "structured", None)
        if isinstance(extras, dict):
            payload["fields"] = _redact(extras)

        return json.dumps(
            _redact(payload),
            separators=(",", ":"),
            ensure_ascii=False,
            default=str,
        )


def configure_logging(
    *,
    service_name: str,
    environment: str,
    service_version: str = "unknown",
    level: str = "INFO",
    json_logs: bool = True,
) -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)
    if json_logs:
        handler.setFormatter(
            JsonFormatter(
                service_name=service_name,
                environment=environment,
                service_version=service_version,
            )
        )
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    root.addHandler(handler)

    for noisy in (
        "httpcore",
        "httpx",
        "urllib3",
        "botocore",
    ):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def structured_log(
    logger: logging.Logger,
    level: int,
    message: str,
    **fields: Any,
) -> None:
    logger.log(
        level,
        message,
        extra={"structured": fields},
    )
