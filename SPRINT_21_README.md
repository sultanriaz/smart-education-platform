# Sprint 21 — Observability & Operational Monitoring

Sprint 21 adds production-oriented metrics, logging, distributed tracing,
dashboards, alerts, SLO definitions, and incident runbooks to the Smart
Education Platform.

It builds on:

```text
Sprint 16 request/correlation contracts
Sprint 17 infrastructure/events
Sprint 18 security/redaction
Sprint 19 quality gates
Sprint 20 performance budgets
```

## Shared observability package

New package:

```text
libs/python/smartedu_observability
```

It provides:

```text
request/correlation context
JSON logs
secret-field redaction
Prometheus HTTP metrics
dependency timing
outbox backlog/age metrics
event processing metrics
worker metrics
SQLAlchemy pool metrics
OpenTelemetry OTLP traces
HTTPX tracing
SQLAlchemy tracing
W3C event trace propagation
```

## Telemetry stack

New stack:

```text
Prometheus
Grafana
Loki
Promtail
Tempo
OpenTelemetry Collector
Alertmanager
```

Optional exporter overlay adds:

```text
PostgreSQL exporter
Redis cache exporter
Redis durable exporter
Nginx Gateway exporter
cAdvisor
```

RabbitMQ uses its built-in Prometheus plugin.

## Standard metrics

Application services expose:

```text
smartedu_http_requests_total
smartedu_http_request_duration_seconds
smartedu_http_inflight_requests

smartedu_dependency_requests_total
smartedu_dependency_request_duration_seconds

smartedu_outbox_pending
smartedu_outbox_oldest_age_seconds

smartedu_events_processed_total
smartedu_event_processing_lag_seconds

smartedu_worker_queue_depth
smartedu_worker_failures_total

smartedu_db_pool_checked_out
smartedu_db_pool_checkout_failures_total
```

Prometheus labels deliberately use bounded values such as route templates and
service names.

## Structured logs

Every service can emit JSON including:

```text
service
environment
service_version
request_id
correlation_id
trace_id
span_id
structured fields
```

Sensitive keys are redacted.

Sprint 18's stricter rule still applies: secrets must not be placed into free
text just because key redaction exists.

## Distributed tracing

Synchronous calls:

```text
FastAPI -> HTTPX -> downstream FastAPI
```

use W3C Trace Context.

Asynchronous calls use:

```text
EventEnvelope.metadata
```

for trace propagation while keeping the Sprint 17 `correlation_id`.

## Dashboards

Provisioned Grafana dashboards:

```text
Smart Education Platform Overview
Smart Education Service Detail
```

They cover:

```text
request rate
5xx ratio
p50/p95/p99 latency
dependency latency
outbox backlog
event-processing lag
application logs
```

Codex should add domain-specific panels after inspecting actual queue names and
database exporter metrics.

## Alerts

Included alerts cover:

```text
service unavailable
high/critical 5xx ratio
general p95 >3s
Attendance p95 >2s
Notification event p95 lag >5s
outbox backlog/staleness
worker failure bursts
RabbitMQ queue backlog
```

Each alert references `RUNBOOKS.md`.

## SLOs

Operational targets preserve the SRS:

```text
99.0% availability over rolling 30 days
95% normal user interactions <=3s
95% Attendance operations <=2s
95% Notification end-to-end visibility <=5s
```

## Local startup

Copy:

```powershell
Copy-Item .\.env.observability.example .\.env.observability
```

Set a strong local Grafana admin password.

Then:

```powershell
.\scripts\run-observability.ps1
```

With Docker-log collection:

```powershell
.\scripts\run-observability.ps1 -Logs
```

With infrastructure exporters:

```powershell
.\scripts\run-observability.ps1 -Exporters
```

After service instrumentation:

```powershell
.\scripts\observability-smoke.ps1 -RequireServices
```

## Local endpoints

```text
Grafana       http://localhost:3001
Prometheus    http://localhost:9090
Alertmanager  http://localhost:9093
Loki          http://localhost:3100
Tempo         http://localhost:3200
```

All bound host ports are loopback-only by default.

## Production note

The bundled stack is a development/staging/FYP reference deployment.

Sprint 23 must decide production persistence, replication, managed-service
choices, authentication, TLS, backup, and retention.
