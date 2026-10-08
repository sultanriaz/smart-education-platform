# Sprint 17 Verification

The generated Sprint 17 package was verified in the packaging environment.

## Shared `smartedu-infra` package

```text
pytest -q
14 passed
```

Coverage includes:

- ten-service database/user ownership map
- bounded connection-pool settings
- SQLite engine compatibility for tests
- safe S3 object keys
- path traversal rejection
- RabbitMQ queue/retry/DLQ naming
- event binding de-duplication
- retention cutoff handling
- domain-neutral outbox publisher behavior

## Wheel build

Built successfully with:

```text
python -m pip wheel . --no-deps --no-build-isolation
```

Generated:

```text
smartedu_infra-0.1.0-py3-none-any.whl
```

The wheel itself is not stored in the Sprint ZIP. Reproducible package source and
PowerShell build/install scripts are included.

## Python syntax

All Python files in Sprint 17 compile successfully.

## Infrastructure configuration parsing

All YAML and JSON configuration files parse successfully.

The local infrastructure Compose contains:

```text
infra-postgres
redis-cache
redis-durable
rabbitmq
minio
minio-bootstrap
```

## Shell syntax

Both infrastructure shell scripts passed `sh -n`:

```text
infra/postgres/init/01-create-service-databases.sh
infra/minio/bootstrap.sh
```

## Service bridge coverage

Sprint 17 includes `app/sprint17.py` for all ten services:

```text
identity-service
academic-service
attendance-service
scheduling-service
notification-service
facility-service
learning-service
assessment-service
reporting-service
platform-service
```

## Database ownership map

Verified:

- ten unique database names
- ten unique service logins
- no shared application DB user in the canonical mapping

## Encoding

UTF-8 BOM scan:

```text
0 BOM files
```

## Not claimed as verified here

Docker is not installed in the packaging runtime, and the user's complete merged
Sprints 1–16 repository is not available here.

Therefore these remain repository integration checks:

- `docker compose up` of the infrastructure stack
- actual PostgreSQL initialization in Docker
- real Redis connectivity
- RabbitMQ publish/consume/retry/DLQ against a live broker
- MinIO bucket bootstrap and upload/download
- existing service engine migration to `smartedu-infra`
- all real Alembic histories and schema drift checks
- real service outbox/inbox migration to RabbitMQ transport
- worker container/process wiring
- durable Redis idempotency across multiple service replicas
- Learning Service live S3 migration
- Reporting/Platform export storage migration where applicable
- PostgreSQL backup and restore drills
- object-storage backup/restore drills
- service-specific retention jobs
- service-specific index changes after actual query-plan review
- all ten service regression suites
- Gateway/frontend regression
- Student/Teacher/Admin E2E

These checks are explicitly required in `SPRINT_17_INTEGRATION.md` and
`CODEX_MERGE_PROMPT.md`.
