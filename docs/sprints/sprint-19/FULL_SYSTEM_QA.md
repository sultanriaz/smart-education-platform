# Full-System QA Plan

## Precondition

Run only against an isolated QA/staging environment with dedicated test
credentials and disposable domain data.

## Phase 1 — Static and unit gates

Run:

```text
smartedu-contracts
smartedu-infra
smartedu-security
smartedu-testkit
all ten service unit suites
frontend typecheck/lint/unit/build
Gateway tests
security scanners
```

No live environment is required for pure/static tests.

## Phase 2 — Databases and migrations

For every service:

```text
one Alembic head
upgrade head
current == head
alembic check / no drift
rollback test where supported
clean database -> full migration chain
existing database -> forward migration
```

Re-run PostgreSQL-specific concurrency suites.

## Phase 3 — Infrastructure

Verify:

```text
PostgreSQL
Redis cache
Redis durable
RabbitMQ
MinIO/S3
ClamAV when enabled
```

Exercise:

```text
broker retry/DLQ
Redis idempotency across replicas
private object-storage permissions
per-service DB login isolation
```

## Phase 4 — Contracts

Capture OpenAPI snapshots.

Fail the release on an unexplained breaking change.

Validate:

```text
Gateway public prefixes
internal namespace 404
error envelope
EventEnvelope v1
pagination shapes where adopted
correlation/request IDs
```

## Phase 5 — Authorization

Run the backend authorization matrix for:

```text
anonymous
Student
Teacher
Admin
```

Then run service-specific ownership/scoping cases, including:

```text
Student can access only own records
Teacher only assigned sections/courses
Teacher cannot Admin operations
Admin-only reporting/platform operations
no Student assessment answer-key exposure
no Teacher access to unassigned section data
```

## Phase 6 — Resilience

Kill/degrade one dependency at a time.

Expected behaviors:

```text
bounded failure time
503 where dependency is synchronously required
no cross-DB fallback
retry only safe/idempotent operations
circuit breaker opens
recovery succeeds
outbox preserves events
duplicate event is idempotent
```

## Phase 7 — Role workflows

Execute workflow specifications:

```text
tests/workflows/student.yaml
tests/workflows/teacher.yaml
tests/workflows/admin.yaml
```

These are acceptance-level journeys spanning multiple services.

## Phase 8 — Browser E2E

Run Playwright in Chromium.

Capture traces/screenshots only on failure.

Never put QA passwords into screenshots, console logging, or source control.

## Phase 9 — NFR smoke

This sprint does not replace Sprint 20 performance engineering, but it should
detect obvious regressions:

```text
health endpoint < 1s
normal UI navigation remains responsive
attendance operation does not obviously violate the 2-second SRS expectation
normal page/API flows remain within the 3-second SRS expectation in staging
```

Formal load/concurrency targets belong to Sprint 20.

## Phase 10 — Release evidence

Archive:

```text
JUnit XML
QA summary JSON
Playwright report
OpenAPI candidate snapshots
security scan summaries
migration output
concurrency test output
known test exceptions
```

Do not archive plaintext secrets/tokens.
