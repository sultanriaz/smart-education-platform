# Sprint 7 Integration — Learning Resource Service

## Drop-in contents

- `services/learning-service`
- `docker-compose.learning.yml`
- `.github/workflows/learning-service-ci.yml`

## Required integration checks

1. Confirm Identity's actual JWKS path, issuer, audience and access-token claims. Adapt only the Learning verifier configuration/adapter.
2. Inspect Academic Service's real internal/API contract. Adapt `HttpAcademicClient`; never query `academic_db` directly.
3. Confirm Notification Service's actual `POST /api/v1/internal/events` envelope and internal-token header. Adapt only the outbox relay.
4. Confirm local port allocations do not collide: Learning defaults to API `8007`, DB `5440`, MinIO `9002/9003`.
5. Run migrations on PostgreSQL and `alembic check`.
6. Run Learning tests plus regression suites for existing services.
7. Smoke-test Teacher create/version/publish -> Student library -> download -> access log.
8. Smoke-test object storage restart and persistence.

## Service boundaries

Learning owns learning material metadata, resource versions, file storage keys, access logs and recommendation baseline. Academic owns enrollment/assignment facts. Identity owns principals. Notification owns delivery.
