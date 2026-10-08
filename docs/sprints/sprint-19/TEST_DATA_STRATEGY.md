# Test Data Strategy

## Deterministic IDs

Use stable UUID fixtures where the test controls persistence.

The shared `smartedu_testkit` provides stable IDs for:

```text
Admin
Teacher
Student
other Student
department
program
semester
course
section
room
```

## Database tests

Each service integration suite should isolate data by one of:

```text
transaction rollback
temporary schema/database
per-test UUID namespace
explicit cleanup
```

Do not make tests order-dependent.

## Cross-service tests

Create data through public/internal service contracts rather than inserting into
another service's database.

Example:

```text
Academic enrollment
        ↓ event/API
Attendance authorization test
```

not:

```text
Attendance test inserts into academic_db
```

## Browser E2E accounts

Use long-lived dedicated staging accounts only for authentication identity.

Create disposable domain records during the test and delete/archive them when
the public API supports cleanup.

## Time

Use UTC and explicit timestamps.

Avoid assertions based on local timezone or `sleep()` when an injectable/frozen
clock or polling condition can be used.

## Secrets

QA passwords/tokens live in CI secret storage.

Never hard-code them in:

```text
Playwright files
pytest fixtures
Docker Compose
screenshots
test reports
```
