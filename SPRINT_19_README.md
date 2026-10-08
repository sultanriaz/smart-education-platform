# Sprint 19 — Testing Maturity & Full-System QA

Sprint 19 adds the shared quality framework required to prove the behavior built
during Sprints 1–18.

It does not add a new business domain.

## Deliverables

### `smartedu-testkit`

Location:

```text
libs/python/smartedu_testkit
```

Provides deterministic helpers for:

- stable UUID fixtures
- UTC frozen time
- Ed25519 access-JWT/JWKS test issuance
- authorization matrices
- HTTP assertions
- OpenAPI checks
- concurrency barriers
- eventual-consistency polling
- deterministic fault injection
- OpenAPI breaking-change detection

### Architecture tests

Central tests enforce:

```text
no cross-service Python imports
frontend uses Gateway only
one Alembic history per service
no root monolithic Alembic history
production templates do not regress to plaintext external protocols
```

### Contract tests

Includes:

- common error schema
- common event schema
- pagination schema
- live service health/OpenAPI checks
- Gateway internal namespace protection
- request/correlation header checks
- OpenAPI snapshot/candidate diff tooling

### Authorization matrix

A minimum cross-platform role matrix covers:

```text
anonymous
Student
Teacher
Admin
```

The merge process must reconcile any route whose exact Sprint 1–18 contract
differs from the generated baseline.

### Service scenario catalog

`tests/SERVICE_TEST_SCENARIOS.yaml` records the critical behavioral coverage for
all ten services.

It explicitly includes race/rollback/RBAC/idempotency scenarios that line
coverage alone cannot prove.

### Migration testing

PowerShell runner checks:

```text
exactly one Alembic head
upgrade head
current
alembic check
```

Codex should preserve each service's existing rollback/round-trip tests.

### PostgreSQL concurrency plan

A dedicated plan covers:

```text
Academic final seat
Attendance duplicate/finalize race
Scheduling room/Teacher/section conflicts
Facility double booking
Assessment attempt limit
distributed idempotency
outbox publisher claiming
```

### Browser E2E

A separate Playwright package is included under:

```text
tests/e2e
```

Baseline tests cover:

- anonymous route protection
- Student/Teacher/Admin login
- cross-role workspace isolation
- browser auth-storage security
- password-recovery privacy UX

Codex must extend it against the actual merged Student, Teacher, and Admin
features.

### Role workflow specifications

Acceptance workflows exist for:

```text
Student
Teacher
Admin
```

They span Identity, Academic, Attendance, Scheduling, Notification, Facility,
Learning, Assessment, Reporting, Platform, and Gateway where relevant.

### CI quality gate

A new `quality.yml` provides baseline CI jobs for:

```text
testkit
architecture tests
frontend checks
manual-dispatch browser E2E
```

The existing per-service and security workflows should be consolidated rather
than duplicated blindly.

### QA report

`qa-report.py` aggregates JUnit XML into:

```text
test-results/qa-summary.json
```

### One-command local orchestration

```powershell
.\scripts\run-sprint19.ps1
```

Optional running-system checks:

```powershell
.\scripts\run-sprint19.ps1 -Live
```

Browser E2E as well:

```powershell
.\scripts\run-sprint19.ps1 -Live -E2E
```
