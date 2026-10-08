# Sprint 21 Application Instrumentation Guide

## FastAPI

Each service receives:

```text
services/<service>/app/sprint21.py
```

The intended application setup is:

```python
app = FastAPI(...)

runtime = install_sprint21(app)
```

If Sprint 16 already owns request/correlation middleware, merge behavior rather
than stacking two competing ID generators.

The final behavior must be:

```text
valid incoming X-Request-ID preserved or replaced by a safe generated ID
valid incoming X-Correlation-ID preserved
IDs returned in response headers
IDs present in structured logs
trace/span IDs present when tracing is active
```

## SQLAlchemy

After creating the service-owned engine:

```python
from smartedu_observability import (
    install_pool_metrics,
    instrument_sqlalchemy,
)

instrument_sqlalchemy(engine)

install_pool_metrics(
    engine,
    metrics=runtime.metrics,
    database_name="academic_db",
)
```

Use the real database name owned by the service.

Do not instrument another service's database because services must not connect
to it.

## HTTP dependencies

HTTPX automatic tracing is installed globally by the Sprint 21 FastAPI helper.

For important dependency SLI metrics:

```python
from smartedu_observability import observe_dependency

with observe_dependency(
    runtime.metrics,
    dependency="academic-service",
    operation="student_enrollment_check",
):
    response = academic_client...
```

Use stable operation names. Do not use UUIDs in the operation label.

## Transactional outbox

A publisher worker should periodically record:

```python
runtime.metrics.set_outbox(
    pending=pending_count,
    oldest_created_at=oldest_created_at,
)
```

Suggested refresh cadence:

```text
15-30 seconds
```

Do not execute an expensive unindexed full-table scan on every request merely
to expose observability.

Add or reuse appropriate outbox status/created-at indexes only through measured
query review.

## Event producer tracing

Before persisting the EventEnvelope:

```python
from smartedu_observability import inject_trace_context

metadata = inject_trace_context(existing_metadata)

event = EventEnvelope(
    ...,
    metadata=metadata,
)
```

Trace metadata travels through the same transactional outbox record, preserving
the relationship between the source transaction and async consumer.

## Event consumer tracing

Wrap actual consumer work:

```python
from smartedu_observability import consume_event

with consume_event(
    metrics=runtime.metrics,
    event_type=event.event_type,
    source=event.source,
    metadata=event.metadata,
    correlation_id=event.correlation_id,
    occurred_at=event.occurred_at,
):
    handle_event(event)
```

This records:

```text
consumer trace span
success/failure event count
event processing lag
correlation context
```

Inbox deduplication remains authoritative and should happen at the correct point
in the real consumer workflow.

## Worker metrics

For bounded known queues:

```python
runtime.metrics.worker_queue_depth.labels(
    runtime.metrics.service_name,
    "notification-email",
).set(depth)
```

On terminal worker failures:

```python
runtime.metrics.worker_failures.labels(
    runtime.metrics.service_name,
    "email-delivery",
    "provider_error",
).inc()
```

Keep reason values bounded.

Bad:

```text
SMTP exception full message
user email
event UUID
```

Good:

```text
timeout
provider_4xx
provider_5xx
invalid_recipient
unexpected
```

## Logging

Use standard Python logging for ordinary messages.

For structured fields:

```python
structured_log(
    logger,
    logging.INFO,
    "attendance_session_finalized",
    session_id=str(session.id),
    record_count=len(records),
)
```

Do not log request/response bodies by default.

## Metrics path

`/metrics` is an operational endpoint.

It should:

```text
be reachable from Prometheus on the backend network
not be exposed by the public Gateway
not require normal end-user JWT auth
not execute business queries synchronously
```

## Health versus readiness versus metrics

Keep semantics distinct:

```text
/health   process is alive
/ready    critical own dependencies are ready
/metrics  operational telemetry
```

Do not make `/health` fail simply because Tempo/Prometheus/Loki is unavailable.

Observability outages must not take the business platform down.
