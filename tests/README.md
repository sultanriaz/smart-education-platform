# Sprint 19 Test Layers

Sprint 19 separates tests by failure scope.

## Unit

Lives with each service or shared package.

Unit tests should not need networked infrastructure unless the unit under test
is specifically an infrastructure adapter.

## Contract

Location:

```text
tests/contracts
```

Covers:

- OpenAPI presence
- Gateway namespace behavior
- common error/event/page shapes
- required service resources
- public-vs-internal route boundaries

## Architecture

Location:

```text
tests/integration
```

Marker:

```text
architecture
```

Covers static invariants such as:

- no cross-service Python imports
- no browser direct service-port calls
- one Alembic history per service
- production config transport expectations

## Integration

Service-level integration tests belong primarily under each service's `tests/`.

They should run with the service's real PostgreSQL database when persistence or
concurrency semantics matter.

## Live system

Marker:

```text
live
```

Requires URLs/tokens for a running platform.

These tests are deliberately skipped when environment variables are absent.

## Browser E2E

Location:

```text
tests/e2e
```

Playwright tests exercise:

- authentication
- role workspace isolation
- browser token-storage rules
- recovery UI

Codex should extend these with the real Student/Teacher/Admin business workflows
once exact UI labels/test IDs are inspected.

## Concurrency

Use real PostgreSQL and independent sessions/transactions.

Do not simulate database races with one SQLite connection.

High-value races include:

- Academic final-seat enrollment
- Attendance duplicate/finalization race
- Scheduling room/Teacher/section conflict
- Facility double booking
- Assessment attempt limit
- idempotency same-key request
- outbox claiming/publishing

## Test accounts

Use dedicated QA accounts.

Never run destructive QA workflows against production.

## Quality gates

See:

```text
tests/QUALITY_GATES.yaml
```

Required gates may only be skipped by an explicit documented release exception.
