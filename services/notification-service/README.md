# Sprint 5 — Notification Service

Independent notification and delivery service for the Smart Education Platform.

## Responsibilities

The service owns:

- in-app notifications and unread/read/archive state;
- notification preferences;
- reusable notification templates;
- admin campaigns targeting direct users, roles, or academic sections;
- email delivery attempts and retry records;
- an idempotent inbox for domain events from other services;
- a transactional outbox for notification-domain events;
- background work through Celery + Redis in containerized deployments.

It **does not** own users, roles, student enrollment, sections, courses, schedules, attendance, or facilities. External identities are UUID references only.

## Architecture

```text
React / clients
      |
      v
Notification API (FastAPI :8000 / host :8005)
      |
      +--> notification_db (PostgreSQL)
      |
      +--> Redis --> Celery notification-worker
      |
      +--> Identity Service (role/user resolution + JWKS trust)
      |
      +--> Academic Service (section roster resolution)

Upstream service outbox relay
      |
      v
POST /api/v1/internal/events
      |
      v
inbox_events (idempotency)
      |
      v
notification creation + delivery attempts
```

The HTTP internal-event adapter is intentionally separated from upstream persistence. Notification Service never polls or queries another service's database. A Scheduling/Attendance outbox relay publishes an event envelope to the internal endpoint (or can later publish the same envelope through a message broker adapter).

## Database ownership

`notification_db` owns these tables:

- `notification_templates`
- `notification_preferences`
- `notification_campaigns`
- `notifications`
- `delivery_attempts`
- `inbox_events`
- `outbox_events`
- `alembic_version`

## API

### User notifications

- `GET /api/v1/notifications`
- `GET /api/v1/notifications/unread-count`
- `GET /api/v1/notifications/{notification_id}`
- `POST /api/v1/notifications/{notification_id}/read`
- `POST /api/v1/notifications/read-all`
- `DELETE /api/v1/notifications/{notification_id}` (archive, no destructive delete)

Users can only access notifications whose `recipient_user_id` equals their JWT subject.

### Preferences

- `GET /api/v1/preferences/me`
- `PATCH /api/v1/preferences/me`

Preferences support:

- in-app enable/disable;
- email enable/disable;
- category muting.

Default values are configured using `DEFAULT_IN_APP_ENABLED` and `DEFAULT_EMAIL_ENABLED`.

### Admin templates/campaigns

Admin-only:

- `GET /api/v1/admin/templates`
- `POST /api/v1/admin/templates`
- `PATCH /api/v1/admin/templates/{template_id}`
- `POST /api/v1/admin/campaigns`
- `GET /api/v1/admin/campaigns`
- `GET /api/v1/admin/notifications/{notification_id}/deliveries`

Campaign target kinds:

- `DIRECT`: explicit user UUIDs (and optional email snapshots);
- `ROLE`: `student`, `teacher`, or `admin`, resolved via Identity Service;
- `SECTION`: section UUID, roster resolved via Academic Service.

Example direct campaign:

```json
{
  "target": {
    "kind": "DIRECT",
    "recipients": [
      {"user_id": "11111111-1111-1111-1111-111111111111", "email": "student@example.edu"}
    ]
  },
  "title": "Room changed",
  "body": "Your Software Engineering class is now in Lab 3.",
  "category": "schedule",
  "priority": "HIGH",
  "channels": ["IN_APP", "EMAIL"]
}
```

Template fields use Python-style named placeholders such as `{course}` and `{room}`. Missing values fail the request rather than silently generating broken text.

## Domain-event inbox

Internal route:

- `POST /api/v1/internal/events`

Header:

```text
X-Internal-Token: <INTERNAL_EVENT_TOKEN>
```

Example envelope:

```json
{
  "event_id": "1c29fb16-5e1e-4a73-9f26-8c7712277063",
  "source_service": "scheduling-service",
  "event_type": "schedule.updated",
  "occurred_at": "2026-10-07T04:00:00Z",
  "payload": {
    "section_id": "22222222-2222-2222-2222-222222222222",
    "teacher_user_id": "33333333-3333-3333-3333-333333333333",
    "title": "Schedule updated",
    "message": "Your timetable has changed."
  },
  "targets": {}
}
```

`event_id` is unique. Sending the same event twice is safe: the second request returns the existing inbox record and does not schedule duplicate processing.

Target resolution supports explicit `targets.user_ids` and can infer:

- `payload.student_user_id` for individual events such as low-attendance warnings;
- `payload.teacher_user_id` for schedule events;
- `payload.section_id` for section-wide events.

For section-wide background processing, configure `ACADEMIC_SERVICE_TOKEN`. For role/user email enrichment in background processing, configure `IDENTITY_SERVICE_TOKEN`. In production these should become short-lived service credentials/client-credentials tokens rather than human access tokens.

## Outbox compatibility

The intended upstream pattern is:

```text
Scheduling/Attendance DB transaction
    -> write domain state
    -> write upstream outbox row

upstream relay
    -> POST event envelope to Notification Service

Notification Service transaction
    -> write inbox_events
    -> create notifications/delivery attempts
```

Do not make Notification Service read `scheduling_db`, `attendance_db`, `academic_db`, or `identity_db`.

## Delivery behavior

`Notification` is the canonical recipient message. Channel-specific attempts live in `delivery_attempts`.

### IN_APP

Creating the notification is the delivery. The attempt is stored as `SENT`, or `SKIPPED` when the user disabled in-app notifications or muted the category.

### EMAIL

Email is queued only when:

- the campaign/event requests `EMAIL`;
- the user's email preference is enabled;
- the category is not muted;
- a recipient email snapshot is available.

Otherwise the attempt is retained as `SKIPPED`, preserving an auditable reason.

Email failures are retained as `FAILED`; up to three attempt rows can be created. Celery schedules retries with backoff.

Supported providers:

- `console` — development provider that logs messages;
- `smtp` — standard SMTP provider.

## Authentication

User/admin APIs validate Identity-issued JWTs through JWKS and require:

- valid signature;
- configured issuer;
- configured audience;
- configured algorithm;
- `exp`, `iat`, `sub`;
- `type=access`;
- UUID subject;
- at least one supported role (`admin`, `teacher`, `student`).

JWKS has fresh-cache and stale-cache windows consistent with the other services.

The internal event endpoint uses a separate shared internal token. This is an integration seam; replace it with service identity/mTLS when the platform introduces a dedicated service-auth mechanism.

## Environment variables

Important values:

```text
DATABASE_URL
JWT_JWKS_URL
JWT_ISSUER
JWT_AUDIENCE
JWT_ALGORITHM
JWT_JWKS_CACHE_SECONDS
JWT_JWKS_STALE_SECONDS
IDENTITY_SERVICE_BASE_URL
IDENTITY_SERVICE_TOKEN
ACADEMIC_SERVICE_BASE_URL
ACADEMIC_SERVICE_TOKEN
ACADEMIC_SECTION_ROSTER_PATH_TEMPLATE
INTERNAL_EVENT_TOKEN
TASK_MODE
REDIS_URL
EMAIL_PROVIDER
SMTP_HOST
SMTP_PORT
SMTP_USERNAME
SMTP_PASSWORD
SMTP_FROM_EMAIL
SMTP_USE_TLS
DEFAULT_EMAIL_ENABLED
DEFAULT_IN_APP_ENABLED
```

See `.env.example` for local defaults.

## Local Python setup (Windows PowerShell)

From repository root:

```powershell
cd services\notification-service
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Run only the database + Redis from repository root:

```powershell
cd ..\..
docker compose -f .\docker-compose.notification.yml up -d notification-db notification-redis
cd .\services\notification-service
```

For host execution make sure `.env` uses:

```text
DATABASE_URL=postgresql+psycopg://notification:notification@localhost:5438/notification_db
REDIS_URL=redis://localhost:6380/0
TASK_MODE=inline
```

Then:

```powershell
python -m alembic upgrade head
uvicorn app.main:app --reload --port 8005
```

Docs:

- `http://localhost:8005/docs`
- `http://localhost:8005/redoc`
- `http://localhost:8005/health`
- `http://localhost:8005/ready`

## Full Docker stack

From repository root:

```powershell
docker compose -f .\docker-compose.notification.yml up -d --build
```

Containers:

- `notification-db`
- `notification-redis`
- `notification-migrate`
- `notification-service`
- `notification-worker`

The API is exposed on `localhost:8005`; PostgreSQL on `5438`; Redis on `6380`.

All containers communicate on Docker-internal ports (`notification-db:5432`, `notification-redis:6379`).

## Migrations

```powershell
python -m alembic upgrade head
python -m alembic downgrade base
python -m alembic upgrade head
python -m alembic check
```

## Tests

```powershell
pytest -q
ruff check .
ruff format --check .
```

PostgreSQL race coverage is enabled when `TEST_POSTGRES_URL` is set, for example:

```powershell
$env:TEST_POSTGRES_URL="postgresql+psycopg://notification:notification@localhost:5438/notification_db"
pytest -q tests\test_postgres_idempotency.py
```

Do not run that destructive test against a real development/production notification database; use a disposable test database.

## Integration assumptions to verify during merge

1. Identity Service exposes a JWKS endpoint matching `JWT_JWKS_URL`.
2. Identity's admin user API supports `GET /api/v1/users` and `GET /api/v1/users/{id}`. If the merged Identity API differs, update only `app/clients/identity.py` and configuration.
3. Academic Service exposes a section roster endpoint. The path is configurable using `ACADEMIC_SECTION_ROSTER_PATH_TEMPLATE`; the parser accepts common `student_user_ids`, `students`, `items`, or `roster` shapes.
4. Scheduling occurrence-change events should contain enough target context (`section_id` and preferably `teacher_user_id`) or the relay should populate `targets`.
5. Attendance low-attendance events should contain `student_user_id` or explicit `targets.user_ids`.

These assumptions are deliberately isolated behind adapters/contracts rather than cross-service model imports.
