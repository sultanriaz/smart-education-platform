# Sprint 21 Distributed Tracing Policy

## HTTP

Each inbound FastAPI request gets a server span.

HTTPX client instrumentation propagates W3C Trace Context automatically:

```text
traceparent
tracestate
```

Do not manually invent another proprietary trace-header format.

## Events

When creating an outbox EventEnvelope:

```python
event.metadata = inject_trace_context(event.metadata)
```

The existing `correlation_id` remains the human/operator correlation mechanism.

On consumption:

```python
with consume_event(...):
    ...
```

creates a consumer span whose parent is extracted from event metadata.

## Attributes

Safe useful attributes:

```text
service.name
deployment.environment
http route template
event type
source service
dependency name
operation name
```

Avoid high-cardinality or sensitive span attributes unless they are essential
for incident diagnosis and approved:

```text
email
password
JWT
message body
assessment answers
full uploaded file content
```

## Sampling

Sampling affects trace storage volume, not application correctness.

Suggested starting values:

```text
development 1.0
staging     0.5–1.0
production  0.1
```

Tune from actual trace volume.

The final production strategy may add tail-based sampling to retain failures and
slow requests, but that requires collector configuration and capacity evidence.

## Database traces

SQLAlchemy instrumentation can record operation timing.

Do not enable capture of sensitive bind parameters.

The Sprint 21 helper deliberately does not add SQL commenter or request data.

## Trace-to-logs

JSON logs include trace/span IDs.

Grafana Loki has a derived `trace_id` field that can link a log line to Tempo.

This is preferred over copying entire log bodies into traces.
