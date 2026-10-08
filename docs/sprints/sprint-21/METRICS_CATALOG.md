# Sprint 21 Metrics Catalog

## HTTP

```text
smartedu_http_requests_total
smartedu_http_request_duration_seconds
smartedu_http_inflight_requests
```

Labels:

```text
service
method
route
status_class
```

`route` is the FastAPI route template, never the raw UUID-containing URL.

## Dependencies

```text
smartedu_dependency_requests_total
smartedu_dependency_request_duration_seconds
```

Use for explicitly important service dependencies where custom operation-level
timing is valuable in addition to OpenTelemetry.

## Messaging / outbox

```text
smartedu_outbox_pending
smartedu_outbox_oldest_age_seconds
smartedu_events_processed_total
smartedu_event_processing_lag_seconds
```

Outbox workers should refresh the backlog gauges on a bounded periodic cadence.

Consumer code should observe success/failure and event lag.

## Workers

```text
smartedu_worker_queue_depth
smartedu_worker_failures_total
```

Queue-depth source depends on the worker implementation.

Do not publish arbitrary user-controlled queue names as labels.

## Database pool

```text
smartedu_db_pool_checked_out
smartedu_db_pool_checkout_failures_total
```

Install pool listeners against the service-owned SQLAlchemy engine.

## Infrastructure

Through exporters / built-in integrations:

```text
PostgreSQL session/transaction/table statistics
Redis memory/commands/connections
RabbitMQ queues/connections/messages
Nginx request/connection metrics
container CPU/memory
```

Exact exporter metric names are exporter-owned and should not be reimplemented
inside application services.

## Recording rules

Sprint 21 defines:

```text
smartedu:http_requests:rate5m
smartedu:http_5xx:rate5m
smartedu:http_error_ratio:5m
smartedu:http_request_duration:p95
smartedu:http_request_duration:p99
smartedu:event_processing_lag:p95
```
