# Sprint 19 Integration Checklist

## 1. Extract at repository root

Sprint 19 is intentionally additive.

## 2. Install the shared testkit

```powershell
cd .\libs\python\smartedu_testkit
python -m pip install -e ".[dev]"
pytest -q
```

## 3. Inspect all existing tests before editing

The repository already contains proven tests from earlier sprints.

Preserve:

```text
Academic PostgreSQL enrollment races
JWKS outage/cache tests
Attendance atomicity tests
Scheduling conflict tests
Facility booking races
Assessment grading tests
Reporting event-idempotency tests
Security tests
Gateway tests
```

Do not replace a stronger test with a generic Sprint 19 smoke test.

## 4. Reconcile `SERVICE_TEST_SCENARIOS.yaml`

Map every scenario to an actual test.

Add missing tests inside the owning service.

Mark PostgreSQL race tests with:

```text
postgres
concurrency
```

Do not fake them with SQLite.

## 5. Coverage

Add pytest-cov to service CI if not already present.

Recommended gate:

```text
--cov=app --cov-report=term-missing --cov-fail-under=80
```

If a legacy service is below 80%, raise it deliberately; do not exclude business
modules merely to pass the number.

## 6. Architecture tests

Run:

```powershell
python -m pytest -q tests\integration -m architecture
```

Fix actual boundary violations.

Do not whitelist cross-service ORM/DB coupling.

## 7. Migrations

Run:

```powershell
.\scripts\test-migrations.ps1
```

For each service also verify clean-DB migration and any existing
upgrade/downgrade round trip.

## 8. Contract snapshots

Start the complete QA stack.

Configure all service URLs, then:

```powershell
python .\scripts\capture-openapi.py `
    --output .\tests\contracts\snapshots\candidate
```

Compare against the approved baseline.

Review breaking changes instead of automatically regenerating the baseline.

## 9. Authorization matrix

Reconcile exact routes/statuses in:

```text
tests/security/authorization-matrix.yaml
```

Then run against staging with QA access tokens.

Add service-specific ownership tests beyond role-only checks.

## 10. Failure/resilience

Add integration coverage using real dependencies where needed:

```text
Academic down
Identity/JWKS unavailable
RabbitMQ unavailable
Redis unavailable
MinIO unavailable
Notification email provider failure
```

Verify Sprint 16/17 policies:

```text
bounded timeout
safe retry
circuit breaker
transactional outbox
idempotency
503 when required dependency is unavailable
```

## 11. RabbitMQ/event QA

Test:

```text
publish
consumer success
delayed retry
DLQ
replay
duplicate event ID
out-of-order event
consumer restart
publisher restart
```

Reporting and Platform projections must remain idempotent.

## 12. Browser E2E

Install:

```powershell
cd .\tests\e2e
npm install
npx playwright install chromium
```

Configure dedicated staging QA users and run:

```powershell
npm test
```

Then extend specs to actual Student/Teacher/Admin workflows.

Prefer stable accessible labels and deliberate `data-testid` values over brittle
CSS selectors.

## 13. Full role acceptance workflows

Use:

```text
tests/workflows/student.yaml
tests/workflows/teacher.yaml
tests/workflows/admin.yaml
```

Every step must map to automated API/browser checks or an explicitly documented
manual acceptance check.

## 14. Test isolation

Ensure tests can:

```text
run alone
run in random order
run twice
run after a failed test
```

No test may depend on records created by a previous test.

## 15. Test data and secrets

Use `TEST_DATA_STRATEGY.md`.

Never point destructive tests at production.

Keep QA credentials in CI secret storage.

## 16. CI

Merge `quality.yml` with existing workflows.

Avoid duplicate package installs/builds where one reusable workflow or matrix
job can cover services cleanly.

Upload:

```text
JUnit
coverage XML/HTML
Playwright reports
QA summary
```

as CI artifacts without secrets.

## 17. Run the aggregate suite

```powershell
.\scripts\run-sprint19.ps1
```

Then with the QA environment:

```powershell
.\scripts\run-sprint19.ps1 -Live -E2E
```

Finally:

```powershell
python .\scripts\qa-report.py .\test-results\sprint19 `
    --output .\test-results\sprint19\qa-summary.json
```

## 18. Definition of done

Sprint 19 is complete only when:

- all ten service suites pass
- critical scenario catalog is mapped to tests
- PostgreSQL race tests pass
- all service migrations pass
- architecture boundary tests pass
- contract snapshots are reviewed
- authorization matrix passes
- security suite remains green
- Gateway suite passes
- frontend typecheck/lint/unit/build passes
- Student browser workflow passes
- Teacher browser workflow passes
- Admin browser workflow passes
- event retry/DLQ/idempotency tests pass
- no required quality gate is silently skipped
- QA evidence is archived for the FYP record
