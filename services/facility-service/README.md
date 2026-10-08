# Smart Education Platform — Facility Service (Sprint 6)

Independent FastAPI service for campus facilities, equipment, availability, booking approvals,
administrative blocks, scheduling reservations, booking history and notification-ready outbox events.

## Ownership boundary

Facility Service owns `facility_db` and the following concepts:

- facilities / rooms / labs / halls
- facility equipment inventory metadata
- bookable capacity and active/bookable state
- user booking requests and approval lifecycle
- administrative unavailability blocks
- external reservations created by peer services such as Scheduling
- booking history/audit entries
- facility-domain outbox events

It does **not** own Identity users, courses, sections, timetables, attendance, or notifications.
No foreign keys point to another service database.

## Local ports

- API: `http://localhost:8006`
- Swagger: `http://localhost:8006/docs`
- PostgreSQL host port: `5439` by default

## Roles

- `student`: browse facilities, check availability, create/view/cancel own bookings.
- `teacher`: same booking capabilities as students.
- `admin`: manage facilities/equipment, see all bookings, approve/reject/cancel bookings,
  create/cancel administrative blocks.

JWTs are verified locally through Identity Service JWKS using issuer, audience, algorithm,
expiration, token type, subject UUID, and role claims.

## Booking lifecycle

`PENDING -> APPROVED | REJECTED | CANCELLED`

`APPROVED -> CANCELLED`

Pending bookings reserve the slot by default (`PENDING_BOOKINGS_RESERVE_SLOT=true`). This makes
availability deterministic and prevents multiple users receiving competing soft reservations.
Rejecting or cancelling releases the slot.

A booking is rejected if:

- facility is inactive or not bookable
- attendee count exceeds facility capacity
- interval is invalid, in the past, or exceeds configured duration
- it overlaps a blocking booking, admin block, or active external reservation

PostgreSQL advisory transaction locks serialize mutations per facility before overlap checks.

## Scheduling integration

Scheduling must not write `facility_db` directly. Facility Service exposes an authenticated internal
reservation contract:

- `POST /api/v1/internal/reservations`
- `DELETE /api/v1/internal/reservations/{source_service}/{source_reference_id}`

Use `X-Internal-Token` with `INTERNAL_SERVICE_TOKEN`.

A Scheduling occurrence can reserve a facility using a stable source pair such as:

```json
{
  "facility_id": "<uuid>",
  "source_service": "scheduling-service",
  "source_reference_id": "occurrence:<uuid>:2026-10-12T09:00:00Z",
  "starts_at": "2026-10-12T09:00:00Z",
  "ends_at": "2026-10-12T10:30:00Z",
  "metadata": {"section_id": "<uuid>"}
}
```

The create operation is idempotent for the exact same active reservation.

## Notification integration

Facility Service writes transactional outbox events. It does not call Notification Service inside
the booking transaction. A later relay should publish these to Sprint 5's internal event endpoint.

Events include:

- `facility.created`
- `facility.updated`
- `facility.booking_requested`
- `facility.booking_approved`
- `facility.booking_rejected`
- `facility.booking_cancelled`
- `facility.block_created`
- `facility.external_reservation_created`

Booking events include notification target user IDs where appropriate.

An optional outbox relay is included at `app.workers.outbox_relay`. It posts unpublished events to Sprint 5's `POST /api/v1/internal/events` contract and marks them published only after a successful response. The Compose relay is behind the `integration` profile so standalone Facility startup does not require Notification Service.

## Main API

### Facilities

- `GET /api/v1/facilities`
- `POST /api/v1/facilities` (admin)
- `GET /api/v1/facilities/{facility_id}`
- `PATCH /api/v1/facilities/{facility_id}` (admin)
- `GET /api/v1/facilities/{facility_id}/availability?starts_at=...&ends_at=...`
- `PUT /api/v1/facilities/{facility_id}/equipment` (admin)

### Equipment

- `GET /api/v1/equipment`
- `POST /api/v1/equipment` (admin)

### Bookings

- `POST /api/v1/bookings`
- `GET /api/v1/bookings`
- `GET /api/v1/bookings/{booking_id}`
- `POST /api/v1/bookings/{booking_id}/approve` (admin)
- `POST /api/v1/bookings/{booking_id}/reject` (admin)
- `POST /api/v1/bookings/{booking_id}/cancel`
- `GET /api/v1/bookings/{booking_id}/history`

Non-admin collection access is automatically scoped to the authenticated user.

### Administrative blocks

- `GET /api/v1/blocks` (admin)
- `POST /api/v1/blocks` (admin)
- `POST /api/v1/blocks/{block_id}/cancel` (admin)

### Internal reservations

- `POST /api/v1/internal/reservations`
- `DELETE /api/v1/internal/reservations/{source_service}/{source_reference_id}`

### Health

- `GET /health` — process health only
- `GET /ready` — verifies Facility PostgreSQL connectivity

## Local Python setup

```powershell
cd services\facility-service
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -m alembic upgrade head
uvicorn app.main:app --reload --port 8006
```

## Docker

From repository root:

```powershell
docker compose -f .\docker-compose.facility.yml up -d --build
```

Then visit `http://localhost:8006/docs`.

## Database migrations

```powershell
cd services\facility-service
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

For real PostgreSQL concurrency verification set a disposable database URL:

```powershell
$env:FACILITY_TEST_POSTGRES_URL = "postgresql+psycopg://facility:facility@localhost:5439/facility_db"
pytest -q tests\test_postgres_concurrency.py
```

Do not run the concurrency test against a database containing valuable data because it creates and
drops Facility Service tables.

## Important integration note

Sprint 4 Scheduling currently may have local room conflict logic. During repository integration,
Codex should adapt Scheduling so room/facility existence and authoritative reservation ownership move
toward Facility Service's internal contract without removing Scheduling's teacher/section conflict checks.
This Sprint package does not directly rewrite Sprint 4 because the integration step must inspect the
actual merged repository first.
