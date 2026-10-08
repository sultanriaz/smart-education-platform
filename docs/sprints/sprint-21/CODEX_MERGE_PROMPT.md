Integrate Sprint 21 Observability & Operational Monitoring into the current
Smart Education Platform.

FIRST inspect the actual merged Sprints 1–20. Preserve all existing:
- service boundaries
- RBAC
- security controls
- request/correlation behavior
- transactional outbox/inbox behavior
- migrations
- performance budgets

The goal is to add operational visibility without changing business semantics.

1. Shared observability package

   Integrate:
   `libs/python/smartedu_observability`

   Add the package to all ten Python service images/environments.

   Preserve the package as domain-neutral. Do not import domain ORM models into
   the shared observability package.

2. Service installation

   Every service has:
   `services/<service>/app/sprint21.py`

   Run:
   `python scripts/apply_sprint21_wiring.py .`

   Inspect every changed `app/main.py`.

   Install observability exactly once per FastAPI app.

3. Reconcile Sprint 16 request/correlation IDs

   Inspect the actual Sprint 16 middleware.

   The final behavior must have one coherent implementation, not two competing
   request-ID generators.

   Preserve:
   - valid incoming request/correlation IDs
   - invalid-ID sanitization
   - response headers
   - propagation to downstream calls/events
   - standard error envelope IDs

   If Sprint 16 is stronger than the Sprint 21 helper, keep Sprint 16 as the
   source of truth and bind Sprint 21 logging context to it.

4. Logging

   Configure all Python services for structured JSON stdout logs.

   Required fields:
   - timestamp
   - level
   - service
   - environment
   - service_version
   - request_id
   - correlation_id
   - trace_id
   - span_id
   - message

   Apply Sprint 18 redaction rules.

   Search existing logging for:
   - Authorization
   - Cookie / Set-Cookie
   - password
   - access/refresh JWT
   - reset/verification token
   - private key
   - security encryption key
   - full assessment answers

   Remove/redact unsafe logging.

5. Metrics

   Every FastAPI service should expose internal `/metrics`.

   Public Gateway must not expose those endpoints.

   Standard application metrics:
   - smartedu_http_requests_total
   - smartedu_http_request_duration_seconds
   - smartedu_http_inflight_requests
   - smartedu_dependency_requests_total
   - smartedu_dependency_request_duration_seconds
   - smartedu_outbox_pending
   - smartedu_outbox_oldest_age_seconds
   - smartedu_events_processed_total
   - smartedu_event_processing_lag_seconds
   - smartedu_worker_queue_depth
   - smartedu_worker_failures_total
   - smartedu_db_pool_checked_out
   - smartedu_db_pool_checkout_failures_total

6. Cardinality

   Inspect every metric label.

   Never use:
   - user UUID
   - student/teacher UUID
   - email
   - request ID
   - correlation ID
   - trace ID
   - message/event ID
   - raw URL
   - uploaded filename
   - arbitrary exception text

   Use route templates.

7. SQLAlchemy

   For each real service-owned engine:
   - enable OpenTelemetry SQLAlchemy instrumentation
   - install pool checkout/checkin metrics
   - use that service's own database name

   Do not connect services to another service's DB for observability.

   Do not capture SQL bind values containing sensitive data.

8. HTTP clients

   Reconcile actual HTTPX service clients.

   Enable distributed tracing.

   Add explicit dependency metrics only for stable important operations.

   Preserve Sprint 16 finite timeouts/retries/circuit-breaker behavior.

9. Event producers

   Inspect every Sprint 17 transactional outbox producer.

   Before persisting EventEnvelope.metadata:
   `inject_trace_context(...)`

   Preserve existing metadata and canonical envelope version.

   Do not invent another event envelope just for observability.

10. Event consumers

    Integrate `consume_event(...)` around real event work.

    Reconcile it with:
    - inbox dedup
    - transaction boundary
    - retry
    - DLQ
    - projection update

    Record:
    - event type
    - success/failure
    - processing lag
    - trace context
    - correlation context

    Do not weaken idempotency.

11. Outbox metrics

    For every service with an outbox:
    - pending event count
    - oldest pending age

    Refresh on a bounded cadence.

    Ensure the query is indexed/cheap enough.

    Do not issue full table scans on every API request.

12. Worker metrics

    Instrument:
    - Notification workers
    - Reporting consumers
    - outbox publishers
    - Platform jobs
    - import/export/background workers

    Keep queue/worker/reason label values bounded.

13. Gateway

    Reconcile:
    - `infra/gateway/sprint21-http-context.conf`
    - `infra/gateway/sprint21-proxy-observability.conf`
    - `infra/gateway/sprint21-stub-status.conf`

    with the real Sprint 11/16 Nginx files.

    Preserve:
    - internal route blocking
    - CORS
    - security headers
    - auth rate limits
    - request/correlation IDs

    Gateway access logs should be JSON and must not contain auth headers/cookies.

14. Gateway metrics

    Enable internal `stub_status` only if using the included Nginx exporter.

    Keep it off the public route surface.

15. RabbitMQ metrics

    Enable `rabbitmq_prometheus` through the actual Sprint 17 broker image/config.

    Verify Prometheus can scrape:
    `rabbitmq:15692`

    Do not expose the port publicly.

16. PostgreSQL metrics

    Use:
    `infra/observability/postgres-exporter/create-monitoring-role.sql`

    Create `smartedu_monitor` with:
    - pg_monitor
    - CONNECT
    - no app DML
    - no superuser

    Configure `POSTGRES_MONITOR_DSN` through secrets.

17. Redis metrics

    Reconcile Redis ACL/auth from Sprint 18.

    Monitor:
    - cache Redis
    - durable Redis

    Do not put admin/root credentials in Git.

18. Observability stack

    Integrate:
    - docker-compose.observability.yml
    - optional exporter overlay

    Verify:
    - Prometheus
    - Grafana
    - Loki
    - Tempo
    - OTel Collector
    - Alertmanager

    bind only to loopback in local development as generated.

19. Promtail

    Promtail Docker-file scraping is Linux/Docker-host oriented.

    Test it on the actual environment.

    If production uses another log backend/shipper, preserve the JSON log
    contract and replace Promtail rather than forcing incompatible mounts.

20. OpenTelemetry Collector

    Verify all service containers resolve:
    `otel-collector:4317`

    Trace export must be asynchronous/batched.

    Collector outage must not make business requests fail.

21. Sampling

    Use:
    - development/staging: high sampling for validation
    - candidate production: start around 0.1, then tune

    Measure overhead with Sprint 20.

    Do not set 100% production trace sampling without volume/cost evidence.

22. Grafana

    Verify provisioned data sources:
    - Prometheus
    - Loki
    - Tempo

    Verify dashboards:
    - Smart Education Platform Overview
    - Smart Education Service Detail

    Add domain dashboards only after inspecting actual metrics/queue names.

23. Trace/log correlation

    Verify:
    - request log has trace_id
    - Grafana can pivot Loki log -> Tempo trace
    - Tempo trace can pivot to relevant Loki service logs

24. Prometheus

    Run:
    - promtool check config
    - promtool check rules

    Then verify 10/10 FastAPI targets are up.

    Use:
    `scripts/observability-smoke.ps1 -RequireServices`

25. Alerts

    Preserve included:
    - service down
    - high/critical 5xx
    - general >3s p95
    - Attendance >2s p95
    - Notification >5s event lag p95
    - outbox backlog/staleness
    - worker failure burst
    - RabbitMQ backlog

    Reconcile thresholds with real traffic only where not dictated by SRS.

    Do not weaken SRS thresholds to silence alerts.

26. Runbooks

    Every active alert must map to RUNBOOKS.md.

    Update commands/names for the final deployment topology.

27. Alertmanager

    The bundled receivers are intentionally no-op.

    Configure approved staging/production notification channels using secret
    storage.

    Test one synthetic warning and one critical alert.

28. SLOs

    Preserve:
    - availability >=99%
    - general p95 <=3s
    - Attendance p95 <=2s
    - Notification end-to-end p95 <=5s

    Implement dashboards/recording rules for these SLIs.

    Do not count `/health`, `/ready`, `/metrics` as user-facing latency traffic.

29. Burn-rate alerts

    Once the final request SLI is validated in staging, add multi-window
    availability error-budget burn alerts.

    Document maintenance-window treatment explicitly.

30. Privacy / retention

    Read:
    - LOGGING_POLICY.md
    - RETENTION_AND_PRIVACY.md
    - TRACING_POLICY.md

    Ensure telemetry does not become a shadow database of educational data.

31. Security

    Observability UIs/endpoints must not be Internet-public by default.

    Preserve Sprint 18 security.

    Rerun:
    - secret scan
    - dependency audit
    - container audit
    - auth/RBAC tests

32. Performance overhead

    Rerun Sprint 20 baseline with observability disabled and enabled.

    Report overhead.

    Ensure the instrumented build still meets:
    - general 3s p95
    - Attendance 2s p95
    - Notification 5s p95

33. Failure test

    Stop:
    - OTel Collector
    - Loki
    - Prometheus

    one at a time.

    Confirm business APIs remain operational.

    Observability must not be a synchronous availability dependency.

34. CI

    Reconcile `.github/workflows/observability.yml` with the existing CI.

    Required:
    - smartedu-observability tests
    - observability config tests
    - promtool config
    - promtool rules
    - Compose config validation

35. Full regression

    Run:
    - all 10 service suites
    - Sprint 18 security
    - Sprint 19 quality/E2E
    - Sprint 20 baseline
    - Gateway tests
    - frontend checks

36. Do not solve Sprint 21 by:
    - logging passwords/tokens
    - putting UUIDs into metric labels
    - exposing /metrics publicly
    - exposing Grafana/Prometheus/Loki/Tempo publicly without auth/network controls
    - making business readiness depend on telemetry
    - querying another service DB
    - removing outbox/inbox reliability
    - enabling SQL bind-value capture for sensitive queries
    - using observability admin credentials in application services
    - suppressing alerts by changing SRS targets
    - sampling 100% in production without capacity evidence

At completion report:
- service instrumentation status for all 10 services
- request/correlation propagation result
- metrics endpoint status 10/10
- Prometheus target status
- structured log/redaction checks
- HTTP trace example across at least 2 services
- RabbitMQ async trace example
- SQLAlchemy trace/pool metric status
- outbox metrics by service
- worker metrics by worker
- PostgreSQL exporter permissions/status
- Redis exporter status
- RabbitMQ metrics status
- Gateway metrics/logging status
- Grafana datasource/dashboard status
- Loki log ingestion status
- Tempo trace ingestion status
- trace-to-log navigation status
- promtool results
- alert delivery tests
- SLO dashboard results
- observability failure-isolation tests
- performance overhead before/after
- Sprint 18/19/20 regression totals
- any remaining observability gap and why
