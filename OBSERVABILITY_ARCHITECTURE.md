# Sprint 21 Observability Architecture

Sprint 21 adds a common operational telemetry layer without coupling domain
services to each other.

## Telemetry flow

```text
Browser / API client
        ↓
API Gateway
        ↓
FastAPI service
        ├── Prometheus metrics ──────────→ Prometheus ──→ Grafana / Alerts
        ├── JSON stdout logs ────────────→ Promtail ────→ Loki ──→ Grafana
        └── OTLP traces ─────────────────→ OTel Collector ─→ Tempo ─→ Grafana
```

Event consumers preserve:

```text
correlation_id
W3C trace context in EventEnvelope.metadata
```

so asynchronous operations can be connected to the originating HTTP trace.

## Shared package

`smartedu_observability` supplies:

- request/correlation context
- JSON logging
- sensitive-field redaction
- HTTP metrics
- dependency metrics
- outbox/event metrics
- worker metrics
- SQLAlchemy pool metrics
- OpenTelemetry tracing
- event trace-context injection/extraction

It must remain domain-neutral.

## Cardinality rules

Prometheus labels must remain bounded.

Allowed labels include:

```text
service
method
route template
status class
dependency
operation
event type
outcome
worker
queue
```

Do not label metrics with:

```text
user_id
student_id
teacher_id
email
request_id
correlation_id
trace_id
raw URL
resource UUID
message ID
```

Those values belong in logs/traces where appropriate, not Prometheus labels.

## Metrics endpoint

Each service exposes:

```text
/metrics
```

on the internal service network.

The public Gateway must not expose service metrics to end users.

## Logging

Application services emit JSON logs to stdout.

Sprint 21 does not write application log files inside service containers.

The container runtime is responsible for capture/rotation/forwarding.

## Tracing

HTTPX instrumentation propagates W3C trace context across synchronous service
calls.

RabbitMQ/outbox flows propagate W3C context through the existing event metadata
object.

Trace sampling is configurable:

```text
development: 1.0 is acceptable
production: start lower, e.g. 0.05–0.20, then tune from observed volume/cost
```

Errors and important transactions should remain diagnosable without capturing
sensitive request bodies.

## Infrastructure observability

Optional exporters provide:

```text
PostgreSQL
Redis cache
Redis durable state
Nginx Gateway
container resource metrics
RabbitMQ built-in metrics
```

The exporter overlay is separate so least-privilege credentials can be
configured explicitly.

## Local versus production

The bundled stack uses local persistent volumes and single-node:

```text
Prometheus
Grafana
Loki
Tempo
Alertmanager
```

It is appropriate for development/staging/FYP demonstration.

Sprint 23 deployment work must decide whether production uses managed
observability or replicated/persistent equivalents.
