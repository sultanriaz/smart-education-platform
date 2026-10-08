# Smart Education Platform — Scheduling & Timetable Service (Sprint 4)

Independent FastAPI service that owns recurring academic schedules, timetable generation, occurrence-level cancellation/rescheduling, conflict prevention, audit history, and scheduling outbox events.

## Ownership boundary

This service **owns**:

- recurring class schedule definitions
- section/teacher/room time allocation
- occurrence-level cancellation/rescheduling overrides
- schedule change audit history
- schedule/timetable read models generated from its own data
- scheduling outbox events

This service **does not own**:

- users or roles (Identity Service)
- departments/programs/courses/semesters/sections/enrollments/teacher assignments (Academic Service)
- attendance records (Attendance Service)
- facility metadata/approval workflows (future Facility Service)

External objects are referenced by UUID only. There are no cross-service database foreign keys.

## Architecture

```text
HTTP API
  ↓
SchedulingService
  ├─→ ScheduleRepository → scheduling_db
  ├─→ OutboxRepository   → scheduling_db
  └─→ AcademicClient     → Academic Service HTTP API

Authentication:
Bearer JWT → local signature/claims verification via cached Identity JWKS
```

Repositories do not commit and do not make HTTP calls. Transaction boundaries are owned by the service layer.

## Database tables

- `schedule_entries`
- `schedule_overrides`
- `schedule_audits`
- `outbox_events`
- `alembic_version`

### Schedule model

A schedule is a recurring weekly allocation with:

- section UUID
- course/semester UUID snapshot from Academic Service
- teacher Identity UUID
- optional room UUID
- weekday (`0=Monday ... 6=Sunday`)
- start/end time
- effective date range
- IANA timezone name
- ACTIVE/CANCELLED state

### Conflict policy

For overlapping effective date ranges on the same weekday, overlapping times are rejected when any of these resources match:

- section
- teacher
- room (when room is present)

PostgreSQL advisory transaction locks serialize conflict checks for the same resource/weekday, preventing two concurrent writers from both claiming the same slot.

Adjacent times do not conflict: `09:00-10:00` and `10:00-11:00` are allowed.

## Occurrence overrides

A recurring occurrence can be overridden by `(schedule_id, occurrence_date)`.

Supported kinds:

- `CANCELLED` — omit this occurrence without destroying schedule/history
- `RESCHEDULED` — change start/end and optionally room for this date only

Occurrence IDs are deterministic UUIDv5 values derived from `schedule_id + occurrence_date`.

## Authorization

Supported JWT roles:

- `admin`
- `teacher`
- `student`

JWT validation checks:

- signature from trusted JWKS
- issuer
- audience
- configured algorithm
- expiration
- `type=access`
- UUID subject
- recognized role

JWKS data is cached. A stale cached key set may be used during a short Identity outage according to `JWT_JWKS_STALE_SECONDS`; after that the service returns 503 rather than accepting unverifiable tokens.

### Admin

Can create/update/cancel schedules, set occurrence overrides, inspect schedules/history, and view all timetable scopes. A teacher assigned to a schedule must still be valid according to Academic Service.

### Teacher

Can mutate only their own schedules and only for Academic sections to which they are assigned. Teachers may view their own timetable and authorized section timetables.

### Student

Cannot mutate schedules. Students use timetable endpoints. `GET /timetable/me` resolves their current section IDs through Academic Service. A section timetable is allowed only when Academic Service confirms enrollment.

## Academic Service dependency

The client is isolated in `app/clients/academic.py`. Raw HTTP calls are not scattered through domain logic.

Required logical operations:

- get section
- validate teacher assignment
- validate student enrollment
- list a student's section IDs

Endpoints are configurable because Sprint 2 route names may differ after repository integration:

```env
ACADEMIC_SERVICE_BASE_URL=http://localhost:8002
ACADEMIC_SECTION_PATH_TEMPLATE=/api/v1/sections/{section_id}
ACADEMIC_TEACHER_ASSIGNMENT_PATH=/api/v1/teacher-assignments/validate
ACADEMIC_STUDENT_ENROLLMENT_PATH=/api/v1/enrollments/validate
ACADEMIC_STUDENT_SECTIONS_PATH_TEMPLATE=/api/v1/students/{student_user_id}/sections
```

Expected validation responses may use `valid`, `assigned` / `is_assigned`, or `enrolled` / `is_enrolled` boolean keys. During integration, align these configurable paths/contracts with the actual Academic Service APIs rather than adding database access.

Dependency behavior:

- network timeout / 5xx → 503
- malformed JSON/contract → 502
- academic 404 → 404
- unexpected auth rejection → 502 (service contract/auth configuration problem)

## Facility boundary

Sprint 4 treats `room_id` as an external UUID and enforces room scheduling conflicts locally. Facility metadata validation is intentionally deferred until the Facility Service sprint. Do not introduce a cross-database FK later; integrate through a Facility client/API.

## API

### Service health

```text
GET /health
GET /ready
```

`/health` checks process liveness only. `/ready` verifies Scheduling PostgreSQL connectivity; it intentionally does not fail because Academic Service is temporarily unavailable.

### Schedule management

```text
POST  /api/v1/schedules
GET   /api/v1/schedules
GET   /api/v1/schedules/{schedule_id}
PATCH /api/v1/schedules/{schedule_id}
POST  /api/v1/schedules/{schedule_id}/cancel
POST  /api/v1/schedules/{schedule_id}/overrides
GET   /api/v1/schedules/{schedule_id}/overrides
GET   /api/v1/schedules/{schedule_id}/history
```

Example create payload:

```json
{
  "section_id": "11111111-1111-1111-1111-111111111111",
  "teacher_user_id": "22222222-2222-2222-2222-222222222222",
  "room_id": "33333333-3333-3333-3333-333333333333",
  "weekday": 0,
  "starts_at": "09:00:00",
  "ends_at": "10:00:00",
  "effective_from": "2026-10-05",
  "effective_to": "2026-12-28",
  "timezone_name": "Asia/Karachi"
}
```

Example occurrence cancellation:

```json
{
  "occurrence_date": "2026-11-09",
  "kind": "CANCELLED",
  "reason": "University holiday"
}
```

Example occurrence reschedule:

```json
{
  "occurrence_date": "2026-11-16",
  "kind": "RESCHEDULED",
  "starts_at": "13:00:00",
  "ends_at": "14:00:00",
  "room_id": "44444444-4444-4444-4444-444444444444",
  "reason": "Room maintenance"
}
```

### Timetable

All timetable endpoints require `start_date` and `end_date` (`YYYY-MM-DD`). Range length is capped by `MAX_TIMETABLE_RANGE_DAYS`.

```text
GET /api/v1/timetable/me
GET /api/v1/timetable/sections/{section_id}
GET /api/v1/timetable/teachers/{teacher_user_id}
GET /api/v1/timetable/rooms/{room_id}
```

## Transactional outbox

Every meaningful scheduling mutation writes an outbox row inside the same database transaction.

Current event types:

- `schedule.created`
- `schedule.updated`
- `schedule.cancelled`
- `schedule.occurrence_changed`

A later Notification/Reporting worker can publish these rows without changing scheduling transactions.

## Environment

Copy:

```powershell
Copy-Item .env.example .env
```

Important variables:

```env
DATABASE_URL=postgresql+psycopg://scheduling:scheduling@localhost:5437/scheduling_db
JWT_JWKS_URL=http://localhost:8001/.well-known/jwks.json
JWT_ISSUER=smart-education-identity
JWT_AUDIENCE=smart-education-api
JWT_ALGORITHM=RS256
ACADEMIC_SERVICE_BASE_URL=http://localhost:8002
DEFAULT_TIMEZONE=UTC
MAX_TIMETABLE_RANGE_DAYS=62
```

For Docker-internal service traffic, use service DNS names, not `localhost`.

## Local setup — Windows PowerShell

From repository root:

```powershell
cd services\scheduling-service
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Start only the database from repository root:

```powershell
cd ..\..
docker compose -f .\docker-compose.scheduling.yml up -d scheduling-db
```

Return to service and migrate:

```powershell
cd services\scheduling-service
.\.venv\Scripts\Activate.ps1
python -m alembic -c .\alembic.ini upgrade head
python -m alembic -c .\alembic.ini current
```

Start the API:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8004
```

Docs:

```text
http://localhost:8004/docs
```

## Docker

From repository root:

```powershell
docker compose -f .\docker-compose.scheduling.yml up -d --build
```

Defaults:

- Scheduling API: `localhost:8004`
- Scheduling PostgreSQL: `localhost:5437`

Override DB port if occupied:

```powershell
$env:SCHEDULING_DB_PORT="5447"
docker compose -f .\docker-compose.scheduling.yml up -d
```

When integrated into a combined platform Compose file, point:

- `JWT_JWKS_URL` at the Identity container DNS name
- `ACADEMIC_SERVICE_BASE_URL` at the Academic container DNS name

## Tests

Default test suite uses isolated SQLite where database-specific behavior is unnecessary:

```powershell
pytest -q
```

PostgreSQL concurrency test:

```powershell
$env:POSTGRES_TEST_URL="postgresql+psycopg://scheduling:scheduling@localhost:5437/scheduling_db"
pytest -q tests\test_postgres_concurrency.py
```

The PostgreSQL test verifies that concurrent attempts to claim the same schedule slot produce exactly one winner.

Quality checks:

```powershell
ruff check .
ruff format --check .
```

Migration verification:

```powershell
python -m alembic -c .\alembic.ini upgrade head
python -m alembic -c .\alembic.ini downgrade base
python -m alembic -c .\alembic.ini upgrade head
python -m alembic -c .\alembic.ini check
```

## Integration checklist

When merging this Sprint 4 pack into the main repository:

1. Confirm host ports do not collide with Identity/Academic/Attendance.
2. Align JWT issuer/audience/algorithm/JWKS URL with the existing Identity contract.
3. Align configurable Academic paths with Sprint 2's actual route names and response shapes.
4. Add Scheduling service to any combined platform Compose/gateway configuration.
5. Do not replace Academic validation with direct DB queries.
6. Run the full repository CI plus Scheduling PostgreSQL concurrency test.
7. When Facility Service arrives, add a Facility client for room existence/metadata without changing Scheduling DB ownership.
