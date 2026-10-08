# Sprint 21 Integration Checklist

Sprint 21 assumes Sprints 1–20 are merged.

## 1. Install shared package

```powershell
.\scripts\build-observability-wheel.ps1
.\scripts\install-observability-wheel.ps1
```

Add the built `smartedu-observability` wheel/package to every Python service
image.

## 2. Wire all ten FastAPI services

Run:

```powershell
python .\scripts\apply_sprint21_wiring.py .
```

Inspect every `app/main.py` diff.

The final application should call:

```python
runtime = install_sprint21(app)
```

exactly once.

If Sprint 16 already installs request/correlation middleware, merge the behavior
instead of leaving two competing middleware stacks.

Required final behavior:

```text
safe request ID
safe correlation ID
response headers
JSON logs
HTTP metrics
OTLP traces
```

## 3. Preserve operational endpoint semantics

Keep:

```text
/health
/ready
/metrics
```

separate.

Do not make business readiness depend on:

```text
Grafana
Prometheus
Loki
Tempo
Alertmanager
OTel Collector
```

Telemetry failure must not take the platform offline.

## 4. Metrics must remain private

Prometheus should scrape service containers directly on the backend network.

Confirm the public Gateway does not expose service `/metrics`.

Do not put JWT/end-user authentication on internal Prometheus scraping unless
the deployment has a dedicated machine-auth design.

## 5. SQLAlchemy instrumentation

For each service-owned engine:

```text
Identity        identity_db
Academic        academic_db
Attendance      attendance_db
Scheduling      scheduling_db
Notification    notification_db
Facility        facility_db
Learning        learning_db
Assessment      assessment_db
Reporting       reporting_db
Platform        platform_db
```

install:

```text
OpenTelemetry SQLAlchemy instrumentation
pool checkout/checkin metrics
```

Do not connect a service to another service's DB for observability.

## 6. HTTP dependency timing

Inspect all service clients from Sprints 2–10.

Use standard HTTPX tracing automatically.

Add `observe_dependency(...)` only for stable important operations where an
explicit dependency SLI is useful.

Do not use user/resource UUIDs as metric labels.

## 7. Event producer trace propagation

Inspect every transactional outbox producer.

Before persisting `EventEnvelope.metadata`, call:

```python
inject_trace_context(...)
```

Preserve existing metadata.

Do not change the canonical Sprint 17 envelope merely to create a new tracing
schema.

## 8. Event consumer instrumentation

Wrap real consumer processing with:

```python
consume_event(...)
```

Record:

```text
event_type
success/failure
processing lag
consumer trace span
correlation context
```

Reconcile this wrapper with actual inbox/dedup transaction order.

Do not weaken inbox idempotency.

## 9. Outbox metrics

For services with outboxes, expose:

```text
pending count
oldest pending age
```

Refresh periodically from efficient indexed queries.

Do not run expensive counts on every HTTP request.

## 10. Worker metrics

Instrument actual:

```text
Notification email/event workers
Reporting projection workers
outbox relay workers
Platform background jobs
large import/export workers
```

Use bounded worker/queue/reason label values.

## 11. Gateway

Read:

```text
infra/gateway/sprint21-http-context.conf
infra/gateway/sprint21-proxy-observability.conf
infra/gateway/sprint21-stub-status.conf
```

Reconcile them with the actual Sprint 11/16 Nginx configuration.

Preserve existing Gateway security headers, internal-route blocking, CORS, and
rate limiting.

Do not duplicate/conflict with Sprint 16 request/correlation logic.

Enable `stub_status` only on the backend network.

## 12. Start local observability

```powershell
Copy-Item .\.env.observability.example .\.env.observability
```

Set:

```text
GRAFANA_ADMIN_PASSWORD
```

Then:

```powershell
.\scripts\run-observability.ps1
```

Optional Docker log collection:

```powershell
.\scripts\run-observability.ps1 -Logs
```

Promtail's Docker-file mounts are primarily Linux-oriented. On Docker Desktop,
verify the actual Docker logging path before relying on them.

## 13. OTLP

All service containers should resolve:

```text
otel-collector:4317
```

Configure:

```text
TRACING_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
TRACE_SAMPLE_RATIO=1.0
```

for local/staging.

Use a lower production sample ratio initially.

Verify collector loss does not fail business requests.

## 14. Grafana

Verify provisioned datasources:

```text
Prometheus
Loki
Tempo
```

Verify dashboards:

```text
Smart Education Platform Overview
Smart Education Service Detail
```

Check trace-to-log and log-to-trace navigation.

## 15. Docker logs / Loki

Run with `-Logs` on a compatible Linux Docker host.

Verify logs contain:

```text
service
request_id
correlation_id
trace_id
```

and do not contain:

```text
Authorization
cookies
passwords
JWTs
reset tokens
verification tokens
```

If production uses another log shipper/runtime, preserve the JSON log contract
and replace Promtail rather than forcing Docker-file scraping.

## 16. PostgreSQL exporter

Create a monitoring role using:

```text
infra/observability/postgres-exporter/create-monitoring-role.sql
```

Supply the password through `psql -v`, not Git.

Set:

```text
POSTGRES_MONITOR_DSN
```

The monitoring role should have:

```text
pg_monitor
CONNECT
no application DML
no superuser
```

## 17. Redis exporters

Configure monitoring URLs for:

```text
redis-cache
redis-durable
```

Use Redis ACL/auth credentials in staging/production.

Do not expose Redis directly to Prometheus outside the backend network.

## 18. RabbitMQ

Enable:

```text
rabbitmq_prometheus
```

through the real Sprint 17 broker image/config.

Verify:

```text
rabbitmq:15692/metrics
```

is reachable only internally.

## 19. Gateway exporter

Merge internal `stub_status`.

Start the exporter overlay and verify Prometheus scrapes:

```text
gateway-exporter:9113
```

## 20. Container metrics

cAdvisor is optional because host mounts are environment-specific.

Use it only where the Docker/Linux host supports the required read-only mounts.

Production container metrics may come from Kubernetes/cloud/container-platform
telemetry instead.

## 21. Prometheus

Run:

```text
promtool check config
promtool check rules
```

Verify all ten application targets are up.

Run:

```powershell
.\scripts\observability-smoke.ps1 -RequireServices
```

## 22. Alertmanager

The bundled receiver is intentionally a no-op.

Read:

```text
ALERTING_INTEGRATION.md
```

Configure approved staging/production delivery without committing secrets.

Trigger at least one synthetic alert and verify resolution behavior.

## 23. SLOs

Read:

```text
SLOS.md
```

Verify recording rules and dashboards support:

```text
99% availability
3-second general p95
2-second Attendance p95
5-second Notification p95 end-to-end lag
```

Do not redefine the SRS performance targets to make dashboards green.

## 24. Alert runbooks

Review every alert in:

```text
infra/observability/prometheus/rules/alerts.yml
```

Ensure it maps to a real section in:

```text
RUNBOOKS.md
```

Update runbook commands to match the final deployment topology.

## 25. Sampling

Test trace volumes at:

```text
1.0 staging
0.1 candidate production
```

Ensure tracing overhead remains within the Sprint 20 performance budgets.

If adding tail sampling, benchmark the collector before production.

## 26. Cardinality

Inspect Prometheus label cardinality.

Reject metrics containing:

```text
user IDs
emails
UUID resource IDs
request IDs
correlation IDs
trace IDs
raw URLs
```

Route labels must use templates.

## 27. Security

Rerun Sprint 18:

```text
secret scan
container audit
dependency audit
RBAC regression
```

Grafana/Prometheus/Loki/Tempo/Alertmanager must not be Internet-public by
default.

Protect production observability with authentication/network controls.

## 28. Performance

Rerun Sprint 20 baseline with observability enabled.

Compare overhead.

Observability must not cause the platform to violate:

```text
3s general p95
2s Attendance p95
5s Notification p95
```

## 29. Quality

Run Sprint 19 plus Sprint 21 package/config tests.

All ten service tests remain green.

## 30. Definition of done

Sprint 21 is integrated only when:

- all ten services expose internal metrics
- logs are structured/redacted
- request and correlation IDs propagate
- synchronous HTTP traces work
- event traces work across RabbitMQ
- SQLAlchemy spans/pool metrics work
- outbox backlog metrics exist where applicable
- worker metrics exist where applicable
- Prometheus sees 10/10 service targets
- Grafana dashboards render
- Loki logs are searchable or production log backend replacement is validated
- Tempo traces are searchable
- trace-to-log correlation works
- Prometheus rules validate
- at least one alert is delivered in staging
- runbooks map to alerts
- SLO dashboards preserve SRS targets
- observability outage does not break business APIs
- Sprint 18/19/20 regressions remain green
