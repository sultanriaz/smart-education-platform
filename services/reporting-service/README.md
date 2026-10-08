# Reporting & Analytics Service — Sprint 9

Independent FastAPI service for administrative reporting, cross-service
analytics projections, snapshots, and CSV export.

## Core principle

Reporting Service does **not** query another service's database.

It builds read-optimized projections from service events.

```text
Academic --------Attendance -------Scheduling --------> internal event contract --> Reporting DB --> dashboards/reports
Notification ------/
Facility ---------/
Assessment -------/
```

This is intentionally eventually consistent. Transactional business ownership
remains in the source services.

## Ownership

Reporting Service owns:

- received analytics event inbox
- attendance reporting projection
- assessment reporting projection
- facility booking reporting projection
- notification delivery reporting projection
- schedule activity reporting projection
- enrollment reporting projection
- generated report snapshots
- export audit history

It does not own the operational source records.

## Default ports

- API: `http://localhost:8009`
- Swagger: `http://localhost:8009/docs`
- PostgreSQL: `localhost:5442`

## Internal event ingestion

`POST /api/v1/internal/events`

Header:

`X-Internal-Token: <REPORTING_INTERNAL_EVENT_TOKEN>`

Envelope:

```json
{
  "event_id": "uuid",
  "source_service": "attendance-service",
  "event_type": "attendance.recorded",
  "payload": {},
  "targets": {},
  "occurred_at": "2026-10-07T10:00:00Z"
}
```

Event IDs are idempotent.

## Supported projection families

The package contains mappings for event families such as:

- `academic.enrollment_created`
- `academic.enrollment_activated`
- `academic.enrollment_dropped`
- `attendance.recorded`
- `attendance.updated`
- `assessment.attempt_graded`
- `facility.booking_requested`
- `facility.booking_approved`
- `facility.booking_rejected`
- `facility.booking_cancelled`
- `notification.sent`
- `notification.delivered`
- `notification.failed`
- `schedule.*`

The exact event names/payloads must be reconciled against the merged Sprint 1-8
repository. `CODEX_MERGE_PROMPT.md` describes that work.

## APIs

Admin-only public reporting:

- `GET /api/v1/dashboard/overview`
- `GET /api/v1/metrics/attendance`
- `GET /api/v1/metrics/assessments`
- `GET /api/v1/metrics/facilities`
- `GET /api/v1/metrics/notifications`
- `GET /api/v1/metrics/scheduling`
- `GET /api/v1/metrics/enrollment`
- `POST /api/v1/reports/snapshots`
- `GET /api/v1/reports/snapshots`
- `GET /api/v1/reports/{report_type}.csv`

Platform:

- `POST /api/v1/internal/events`
- `GET /health`
- `GET /ready`

## Current attendance calculation

Attendance percentage considers:

- PRESENT: attended
- LATE: attended
- ABSENT: not attended
- EXCUSED: excluded from denominator

Formula:

`(PRESENT + LATE) / (PRESENT + LATE + ABSENT) * 100`

This must be kept aligned with the Attendance Service's actual documented rule
during integration.

## Local setup

```powershell
cd services\reporting-service
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
pytest -q
uvicorn app.main:app --reload --port 8009
```

## Docker

From repository root:

```powershell
docker compose -f .\docker-compose.reporting.yml up -d --build
```

## Migration verification

```powershell
python -m alembic upgrade head
python -m alembic downgrade base
python -m alembic upgrade head
python -m alembic check
```

## Consistency model

Reports are eventually consistent. Reporting outages must never prevent a source
service from completing its primary transaction. Source services should publish
through their transactional outboxes and retry delivery later.
