# Sprint 20 — Performance & Scalability Engineering

Sprint 20 adds the performance engineering layer for the distributed Smart
Education Platform.

It is not a replacement for correctness testing from Sprint 19.

## Deliverables

### Shared performance toolkit

```text
libs/python/smartedu_perf
```

Provides:

```text
latency percentile helpers
performance budget evaluation
Locust CSV parsing
connection-pool capacity calculations
Little's Law helpers
baseline/candidate result comparison
```

### Load profiles

```text
smoke        20 users / 2m
baseline    100 users / 5m
srs-500     500 users / 10m
stress-750  750 users / 10m
stress-1000 1000 users / 10m
soak-250    250 users / 30m
```

### Representative workload

Default role mix:

```text
Student 75%
Teacher 20%
Admin    5%
```

Locust users exercise:

```text
Academic
Attendance
Scheduling
Notification
Facility
Learning
Assessment
Reporting
Platform
```

Long-running tests can log in with QA credentials and exercise the Sprint 18
HttpOnly refresh-cookie rotation path rather than relying on artificially
long-lived access tokens.

### Performance budgets

The package encodes the original SRS expectations:

```text
>=500 concurrent users
normal interactions p95 <=3s
Attendance p95 <=2s
Notification end-to-end visibility p95 <=5s
steady-state error rate <=1%
```

### Distributed load generation

`docker-compose.performance.yml` supports a Locust master plus multiple workers.

This helps ensure the load generator itself does not become the bottleneck when
testing 500–1000 users.

### Database performance

Included:

```text
PostgreSQL active-session diagnostics
lock-wait diagnostics
dead tuple/vacuum review
table/index IO
relation sizes
pg_stat_statements query review
index review
query-plan capture
connection-pool budget model
```

The sprint does not blindly add indexes. Query changes require measured evidence.

### Infrastructure benchmarks

Included micro-benchmarks for:

```text
Redis
RabbitMQ
S3/MinIO
```

They are diagnostic tools, not substitutes for end-to-end load testing.

### Cache strategy

Sprint 20 defines safe caching rules around Sprint 17 Redis:

```text
cache derived/repeatable reads
bounded TTLs
explicit namespaces
invalidation rules
no source-of-truth state in Redis cache
```

### Worker scaling

Notification workers, Reporting projection workers, outbox publishers, and
large import/export jobs are treated separately from HTTP replicas.

### Browser page timing

A Playwright performance spec extends Sprint 19 E2E and checks role workspace
navigation against the 3-second smoke budget.

### Notification timing

A dedicated configurable probe measures:

```text
source request -> recipient inbox visibility
```

so the 5-second SRS target is not incorrectly measured as only a Notification
GET endpoint.

### CI

`performance.yml` provides:

```text
weekly baseline run
manual smoke
manual SRS-500
manual stress
manual soak
artifact upload
budget evaluation
```

The staging environment URL and QA credentials remain CI secrets.

## Main commands

Install:

```powershell
python -m pip install -r .\requirements.performance.txt
python -m pip install -e .\libs\python\smartedu_perf
```

Run local toolkit/config checks:

```powershell
.\scripts\run-sprint20.ps1
```

Run smoke load:

```powershell
.\scripts\run-sprint20.ps1 -Load -Profile smoke
```

Run SRS acceptance:

```powershell
.\scripts\run-load.ps1 -Profile srs-500
```

Check PostgreSQL connection budget:

```powershell
python .\scripts\check-connection-budget.py
```

Capture database diagnostics:

```powershell
.\scripts\capture-db-performance.ps1
```

Run infrastructure micro-benchmarks:

```powershell
.\scripts\benchmark-infrastructure.ps1
```
