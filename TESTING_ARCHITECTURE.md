# Sprint 19 Testing Architecture

Sprint 19 turns the Smart Education Platform into a testable distributed system
with explicit test layers instead of one undifferentiated pytest suite.

## Test pyramid

```text
                    Browser E2E
                 /---------------\
                / Live integration \
               /--------------------\
              / Contract + migration \
             /------------------------\
            / Service integration/race \
           /----------------------------\
          / Unit + pure-domain tests      \
         /--------------------------------\
```

## Principles

1. Test the invariant at the lowest layer that can prove it.
2. Use PostgreSQL for database semantics and concurrency.
3. Use real Redis/RabbitMQ/MinIO where the infrastructure behavior matters.
4. Use mocks/fakes only for focused unit/failure-policy tests.
5. Browser E2E should prove high-value user journeys, not duplicate every API test.
6. Cross-service tests use APIs/events, never direct access to another service DB.
7. Authorization tests exercise backend endpoints directly.
8. Tests must be deterministic, isolated, and runnable in CI.
9. No destructive test may target production.
10. A skipped required release gate must be treated as an explicit release exception.

## Shared testkit

`libs/python/smartedu_testkit` contains reusable helpers for:

```text
stable UUIDs
frozen UTC clocks
Ed25519/JWKS test issuer
authorization matrices
HTTP JSON assertions
OpenAPI contract checks
fault-injection HTTP transport
deterministic concurrency runner
eventual-consistency polling
```

The testkit contains no service ORM models and does not create cross-service
coupling.

## Contract snapshots

The release process should capture service OpenAPI documents from a known-good
staging build:

```powershell
python .\scripts\capture-openapi.py `
    --output .\tests\contracts\snapshots\baseline
```

Capture the candidate build to a second directory and compare:

```powershell
python .\scripts\check-openapi-breaking.py `
    .\tests\contracts\snapshots\baseline `
    .\tests\contracts\snapshots\candidate
```

The included comparator detects public path, operation, and documented-response
removals. Codex should extend it where schema-level compatibility needs stronger
guarantees.

## Race tests

Concurrency tests must use independent DB sessions/connections and a real
PostgreSQL server.

A passing SQLite test does not prove:

```text
SELECT ... FOR UPDATE
advisory locks
transaction isolation
unique-conflict races
connection-pool behavior
```

## Async/event tests

For outbox/event workflows:

```text
domain transaction
    ↓
outbox persisted
    ↓
publisher confirms RabbitMQ
    ↓
consumer inbox/dedup
    ↓
projection/notification side effect
```

Tests should assert both eventual success and duplicate delivery safety.

Avoid arbitrary long sleeps. Poll for the condition with a bounded timeout.

## Browser tests

Playwright tests use dedicated staging QA identities.

The browser suite currently establishes:

```text
anonymous route protection
Student login
Teacher login
Admin login
cross-role workspace isolation
no auth tokens in Web Storage
forgot-password enumeration-resistant UX
```

During merge, Codex must extend these to actual Student/Teacher/Admin business
journeys using stable accessible labels or explicit `data-testid` contracts.

## Quality reports

Service pytest runs emit JUnit XML.

`qa-report.py` aggregates XML into one JSON summary suitable for CI artifacts and
the FYP verification record.

## Coverage

Target:

```text
>=80% line coverage for service/shared Python code
```

Coverage percentage alone is not a release criterion. A service can have high
coverage and still miss critical:

```text
RBAC
concurrency
transaction rollback
failure/retry
migration
event idempotency
```

The scenario catalog therefore remains a separate required review.
