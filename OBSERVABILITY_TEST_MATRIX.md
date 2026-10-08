# Sprint 21 Observability Test Matrix

## Service instrumentation

For each of the ten FastAPI services verify:

```text
/health works
/ready works
/metrics works internally
public Gateway cannot expose /metrics
request response contains X-Request-ID
request response contains X-Correlation-ID
JSON log contains request/correlation ID
trace is emitted when tracing is enabled
service remains functional with Collector stopped
```

## Metric cardinality

Generate requests with at least 100 distinct UUIDs.

Verify Prometheus series count does not create one route series per UUID.

Expected:

```text
route="/api/v1/resources/{resource_id}"
```

not:

```text
route="/api/v1/resources/uuid-1"
route="/api/v1/resources/uuid-2"
...
```

Search labels for:

```text
email
user UUID
request_id
correlation_id
trace_id
```

They must be absent.

## Logs

Exercise:

```text
successful request
403
404
validation failure
unexpected 500 in isolated QA
dependency 503
```

Verify JSON formatting and IDs.

Attempt safe synthetic inputs containing fields named:

```text
password
authorization
refresh_token
```

and verify redaction.

Do not use real credentials for redaction testing.

## Synchronous traces

Exercise at least:

```text
Attendance -> Academic
Assessment -> Academic
Facility -> Scheduling where HTTP applies
```

Verify a single trace connects client/server spans.

## Event traces

Exercise at least:

```text
Attendance outbox -> Reporting
Assessment outbox -> Reporting
domain event -> Notification
```

Verify:

```text
same correlation_id
consumer span
event type attribute
processing lag metric
```

## Database

For every service with SQLAlchemy:

```text
DB client spans visible
no sensitive bind parameters recorded
pool checkout metric changes under concurrent load
pool metric returns to baseline after load
```

## Outbox

For every outbox owner:

1. stop publisher
2. create a valid event
3. confirm pending/age metrics rise
4. start publisher
5. confirm metrics drain
6. confirm alert state resolves if threshold was crossed

Do not delete outbox rows to reset the test.

## RabbitMQ

Verify Prometheus target is up.

Create controlled backlog and confirm:

```text
queue metric rises
RabbitMQQueueBacklog can be evaluated
consumers drain backlog
```

## Notification SLO

Use Sprint 20 notification timing test.

Verify the event-lag histogram reflects comparable timing and the SLO dashboard
shows the 5-second target.

## PostgreSQL exporter

Verify:

```text
monitor user is not superuser
monitor user has no application DML grants
Prometheus target is up
database/session metrics appear
```

## Redis exporters

Verify separate targets for:

```text
cache
durable
```

Check that exporter credentials cannot perform administrative actions beyond
what monitoring requires.

## Gateway

Verify JSON access logging does not contain:

```text
Authorization
Cookie
Set-Cookie
```

Verify Nginx exporter/stub status is internal only.

## Grafana

Verify:

```text
Prometheus datasource healthy
Loki datasource healthy
Tempo datasource healthy
Platform dashboard loads
Service dashboard loads
SLO dashboard loads
```

## Trace/log pivot

1. execute one traced request
2. find log by correlation ID
3. open Tempo trace from log trace ID
4. navigate back to service logs for trace window

## Alerts

Synthetic tests:

```text
one service down
high 5xx ratio
general latency threshold
Attendance latency threshold
outbox stale/backlog
worker failures
RabbitMQ backlog
```

At least one warning and one critical alert must reach the configured staging
receiver.

## Failure isolation

Stop one at a time:

```text
Prometheus
Grafana
Loki
Tempo
OTel Collector
Alertmanager
Promtail
```

Business service requests must continue.

Loss of observability may create telemetry/export errors, but must not convert
healthy business requests into failures.

## Performance overhead

Compare Sprint 20 baseline:

```text
observability disabled
observability enabled
```

Report:

```text
p95 difference
CPU difference
memory difference
request throughput difference
trace volume
log volume
metrics scrape size
```

Do not accept instrumentation that causes SRS performance regression.

## Security

Verify host ports remain loopback-only in the local compose.

Production access must use deployment authentication/network restrictions.

Run Sprint 18 secret/container/dependency security checks after final integration.
