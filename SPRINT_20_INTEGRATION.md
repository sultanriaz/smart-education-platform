# Sprint 20 Integration Checklist

Sprint 20 assumes Sprints 1–19 are merged and green.

## 1. Install tooling

```powershell
python -m pip install -r .\requirements.performance.txt
python -m pip install -e .\libs\python\smartedu_perf
```

Run:

```powershell
.\scripts\run-sprint20.ps1
```

## 2. Reconcile final API routes

Inspect the actual Gateway/OpenAPI contracts.

Update only the Locust route environment defaults that differ from the merged
system.

Keep task names stable where possible because performance baselines are keyed by
task name.

## 3. Create dedicated QA data

Performance testing needs dedicated:

```text
Student
Teacher
Admin
courses
sections
enrollments
attendance session
quiz/assignment
facilities
learning resources
notification targets
```

Do not use production records.

For mutation tests, create disposable fixtures that can be safely reset.

## 4. Authentication

Prefer QA credentials for baseline/SRS/stress/soak runs.

This exercises:

```text
login
access token
HttpOnly refresh cookie
rotation
```

Do not increase JWT lifetime merely to simplify tests.

## 5. Baseline

With one documented topology, run:

```powershell
.\scripts\run-load.ps1 -Profile baseline
```

Save:

```text
Locust CSV
evaluation.json
database diagnostics
replica counts
pool settings
infrastructure utilization
```

This becomes the known-good comparison point.

## 6. SRS 500-user acceptance

Run:

```powershell
.\scripts\run-load.ps1 -Profile srs-500
```

Verify the generator actually sustained 500 active users.

Required evidence:

```text
p50/p95/p99
requests/sec
error rate
service CPU/memory
DB connections
slow SQL/locks
Redis
RabbitMQ
workers
object storage
```

## 7. Attendance write target

Create a disposable Attendance session/roster.

Configure:

```text
PERF_ATTENDANCE_WRITE_PATH
PERF_ATTENDANCE_WRITE_PAYLOAD
```

Run `AttendanceMutationUser` separately.

Do not mix a repeated destructive mutation with the read-heavy acceptance run.

Target:

```text
p95 <= 2 seconds
error rate <= 1%
```

## 8. Notification target

Configure the real notification/campaign request and recipient inbox routes.

Run:

```powershell
python .\scripts\measure-notification-latency.py ...
```

Repeat sufficiently to calculate p95.

Target:

```text
event/request accepted -> recipient notification visible <= 5 seconds p95
```

Include RabbitMQ/worker queue time.

## 9. Browser timing

Merge:

```text
tests/e2e/specs/performance.spec.ts
```

into Sprint 19 Playwright.

Run key role pages repeatedly.

Treat the five-sample smoke test as regression protection, not final statistical
evidence.

## 10. PostgreSQL

Enable `pg_stat_statements` in QA if supported.

Before and during load, capture:

```text
active sessions
pool exhaustion
lock waits
slow queries
temp IO
sequential scan amplification
dead tuples
```

Use:

```powershell
.\scripts\capture-db-performance.ps1
```

For a suspected query, use:

```powershell
python .\scripts\explain-query.py `
  --database-url $env:DATABASE_URL `
  --sql-file .\query.sql `
  --output .\plan.json
```

Use `--execute` only for safe QA SELECTs or explicitly safe statements.

## 11. Index tuning

Inspect real repository/query plans.

Add indexes only through the owning service Alembic history.

For every index change:

```text
record query plan before
record latency before
apply migration
record query plan after
record latency after
measure write impact
```

Run Sprint 19 concurrency tests after index changes.

## 12. N+1 and ORM review

During load, correlate endpoints with SQL count.

Fix:

```text
lazy-load loops
per-row repository calls
unbounded relationship loads
unbounded result sets
```

Prefer explicit eager loading/pagination where appropriate.

## 13. Connection pools

Run:

```powershell
python .\scripts\check-connection-budget.py
```

Reconcile:

```text
replicas
pool_size
max_overflow
PostgreSQL max_connections
reserved operational headroom
```

The included candidate model assumes one shared 250-connection server and is not
a final production sizing guarantee.

## 14. Redis cache

Identify repeat read paths from measured traces.

Before adding a cache, record uncached behavior.

After caching, measure:

```text
hit rate
Redis latency
DB query reduction
p95 change
memory
staleness behavior
```

Add invalidation tests.

Do not cache correctness-critical booking/attempt/attendance truth.

## 15. RabbitMQ/workers

During notification/reporting/outbox load, measure:

```text
messages/sec
queue depth
oldest-message age
worker throughput
retry rate
DLQ
```

Scale workers independently from HTTP replicas.

## 16. S3/MinIO

For Learning/download-heavy flows, measure object-storage p95.

Use the included micro-benchmark only as a diagnostic.

The real acceptance metric is the application-authorized resource flow.

## 17. Horizontal scaling

Test at least:

```text
single-replica reference
candidate topology
```

If p95 is database-bound, do not simply add API replicas.

Use `SCALABILITY_PLAN.md` to identify the bottleneck first.

## 18. Stress

Run:

```text
stress-750
stress-1000
```

Stop increasing load when the system reaches unsafe saturation.

Record the first bottleneck and failure mode.

Stress results are capacity evidence, not necessarily release gates.

## 19. Soak

Run:

```powershell
.\scripts\run-load.ps1 -Profile soak-250
```

Inspect:

```text
RSS/memory trend
DB connections
open file/socket count where available
Redis memory
queue backlog
error drift
latency drift
```

A soak test must be long enough to expose growth; extend beyond 30 minutes in
staging when practical.

## 20. Regression baseline

Keep approved performance artifacts outside source-control if large.

Compare candidate evaluation JSON:

```powershell
python .\scripts\compare-performance.py `
  <baseline\evaluation.json> `
  <candidate\evaluation.json>
```

Absolute SRS budgets still take precedence over relative comparison.

## 21. CI

Merge `.github/workflows/performance.yml` with current workflows.

Weekly CI should normally use `baseline`, not a heavy 1000-user stress run.

Run SRS/stress/soak manually or in a dedicated performance environment.

## 22. Definition of done

Sprint 20 is complete only when:

```text
baseline recorded
500-user run sustained
general p95 <=3s
Attendance p95 <=2s
Notification visibility p95 <=5s
error rate <=1%
connection budget validated
top DB queries reviewed
critical N+1 issues resolved
candidate replica topology tested
worker lag measured
stress capacity documented
soak run completed
performance regression artifacts archived
Sprint 19 correctness/security suites remain green
```
