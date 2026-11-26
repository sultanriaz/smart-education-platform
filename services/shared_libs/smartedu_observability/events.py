from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from opentelemetry import propagate, trace
from opentelemetry.trace import SpanKind

from .context import clear_request_context, set_request_context
from .metrics import Metrics


def inject_trace_context(
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Add W3C trace context to an event metadata object.

    The canonical Sprint 17 EventEnvelope already has `metadata`, so this does
    not require a cross-service schema fork.
    """
    carrier = dict(metadata or {})
    propagate.inject(carrier)
    return carrier


@contextmanager
def consume_event(
    *,
    metrics: Metrics,
    event_type: str,
    source: str,
    metadata: dict[str, Any] | None,
    correlation_id: str | None,
    occurred_at=None,
) -> Iterator[None]:
    carrier = {
        str(key): str(value)
        for key, value in (metadata or {}).items()
        if isinstance(value, (str, int, float, bool))
    }
    parent = propagate.extract(carrier)
    tracer = trace.get_tracer("smartedu.events")

    set_request_context(
        request_id=None,
        correlation_id=correlation_id,
    )
    outcome = "success"

    with tracer.start_as_current_span(
        f"consume {event_type}",
        context=parent,
        kind=SpanKind.CONSUMER,
        attributes={
            "messaging.system": "rabbitmq",
            "messaging.operation": "process",
            "messaging.message.type": event_type,
            "messaging.source.name": source,
        },
    ) as span:
        try:
            yield
        except Exception as exc:
            outcome = "failure"
            span.record_exception(exc)
            raise
        finally:
            metrics.observe_event(
                event_type=event_type,
                outcome=outcome,
                occurred_at=occurred_at,
            )
            clear_request_context()
