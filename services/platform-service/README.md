# Platform Operations Service — Sprint 10

This service provides shared operational capabilities that do not belong inside
the core academic domain services.

It is an **independently deployable service**, not a shared persistence layer.

## Responsibilities

Platform Service owns:

- global operational audit projection
- search index metadata
- user support tickets and messages
- platform configuration/settings
- feature flags
- service registry
- service health aggregation
- asynchronous job records
- import/export orchestration metadata
- internal event inbox
- platform outbox events

It does **not** own academic, attendance, scheduling, notification, facility,
learning, assessment, or identity domain data.

It must never query those service databases directly.

## Default local ports

- API: `http://localhost:8010`
- Swagger: `http://localhost:8010/docs`
- PostgreSQL: `localhost:5443`
- Redis: `localhost:6381`

## Main architecture

```text
Source service outboxes
        |
        v
POST /api/v1/internal/events
        |
        +--> internal_events (idempotency)
        +--> audit_entries
        +--> search_documents

Users
        |
        +--> support tickets
        +--> global search
        +--> public settings/flags

Admin
        |
        +--> audit viewer
        +--> platform settings
        +--> feature flags
        +--> service registry
        +--> health aggregation
        +--> background jobs

Redis
  |
Celery worker
  |
  +--> health sweep
  +--> remote import/export orchestration
```

## Search indexing contract

Services can send:

`platform.search.upsert`

with:

```json
{
  "search_document": {
    "document_type": "course",
    "document_id": "external-id",
    "title": "Software Engineering",
    "body": "Course description",
    "url_path": "/courses/external-id",
    "metadata": {},
    "audience_roles": ["student", "teacher", "admin"]
  }
}
```

Deletion:

`platform.search.delete`

with `document_type` and `document_id`.

Platform Search stores metadata only. The source service remains authoritative.

## Audit event contract

Any internal event can carry:

```json
{
  "audit": {
    "actor_user_id": "uuid",
    "action": "attendance.corrected",
    "entity_type": "attendance_record",
    "entity_id": "uuid-or-string",
    "correlation_id": "request-id",
    "metadata": {}
  }
}
```

The global audit view is an operational projection, not the source service's
authoritative audit trail.

## Support lifecycle

Suggested statuses:

- OPEN
- IN_PROGRESS
- RESOLVED
- CLOSED

Users can:
- create tickets
- list/view their own tickets
- add public messages

Admins can:
- view all tickets
- assign tickets
- change priority/status
- add internal notes

Support mutations emit platform outbox events for Notification integration.

## Settings and feature flags

Public settings are authenticated-readable and admin-managed.

Feature flags are authenticated-readable and admin-managed.

Sensitive secrets must **not** be stored in platform settings. Use deployment
secret management for passwords, signing keys, API tokens, SMTP passwords, etc.

## Service registry / health

Admins can register internal services with:

- service name
- base URL
- `/health`
- `/ready`
- timeout
- critical flag

A health sweep records a point-in-time health check.

Do not expose private infrastructure addresses to ordinary users.

## Async jobs

Job types:

- IMPORT
- EXPORT
- HEALTH_SWEEP
- REINDEX

The supplied worker includes:
- health sweep execution
- generic remote import/export orchestration

Remote import/export expects target services to expose explicit internal
contracts. During repository integration, reconcile those endpoints instead of
granting Platform Service database access.

## API overview

Authenticated:

- `GET /api/v1/search`
- `POST /api/v1/support/tickets`
- `GET /api/v1/support/tickets`
- `GET /api/v1/support/tickets/{id}`
- `POST /api/v1/support/tickets/{id}/messages`
- `GET /api/v1/settings/public`
- `GET /api/v1/features`

Admin:

- `PATCH /api/v1/support/tickets/{id}`
- `GET /api/v1/admin/audit`
- `GET /api/v1/admin/settings`
- `PUT /api/v1/admin/settings/{key}`
- `PUT /api/v1/admin/features/{key}`
- `GET /api/v1/admin/services`
- `PUT /api/v1/admin/services/{service_name}`
- `POST /api/v1/admin/services/health`
- `POST /api/v1/admin/jobs`
- `GET /api/v1/admin/jobs`

Internal:

- `POST /api/v1/internal/events`

Platform:

- `GET /health`
- `GET /ready`

## Local setup

```powershell
cd services\platform-service

py -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements-dev.txt

Copy-Item .env.example .env

python -m alembic upgrade head
pytest -q

uvicorn app.main:app --reload --port 8010
```

## Docker

From repository root:

```powershell
docker compose -f .\docker-compose.platform.yml up -d --build
```

## Worker

```powershell
celery -A app.workers.celery_app.celery_app worker --loglevel=INFO
```

## Security boundaries

- User authentication uses Identity JWKS.
- Internal event ingestion uses `X-Internal-Token`.
- Platform Service never trusts a user-supplied role header.
- Platform settings are not a secret store.
- Cross-service import/export must use explicit internal service contracts.
