# Attendance Service — Sprint 3

Independent Python 3.12+ FastAPI service owning PostgreSQL `attendance_db`.
It uses SQLAlchemy 2, Alembic, Pydantic 2/settings, PyJWT, HTTPX, pytest, Ruff,
and a non-root Docker image. All Python modules use future annotations and all
generated text files use UTF-8 without BOM.

## Ownership and architecture

```text
app/api/          Versioned HTTP APIs, request dependencies, health checks
app/schemas/      Pydantic request and response contracts
app/security/     Local RS256/JWKS verification; verified caller identity
app/services/     Authorization, policies, statistics, transactions and events
app/repositories/ SQLAlchemy persistence and raw counts; no commits or HTTP
app/domain/       Attendance-owned models and controlled status values
app/clients/      AcademicClient protocol and HTTP implementation
app/db/           Service-owned database sessions and declarative base
migrations/       Standalone, frozen Alembic migration
tests/            API, authorization, adapter, statistics, and PostgreSQL tests
```

API → Service → Repository → SQLAlchemy. External checks use Service →
AcademicClient → HTTP Academic API. Services own commit/rollback. Repositories
never commit, send HTTP requests, or authorize roles.

Attendance does not own students, teachers, courses, enrollments, sections,
rooms, or timetable schedules. It never imports another service's Python
models and never connects to `identity_db` or `academic_db`. All cross-service
references are UUIDs without database foreign keys. The section's course and
semester UUIDs are validated by Academic at session creation and retained as
historical attendance dimensions; their catalog data is not copied.

Tables:

- `attendance_sessions`: external section/course/semester/optional schedule
  occurrence, civil date/times, creator, lifecycle, finalizer, timestamps.
- `attendance_records`: one current mark per session/student, initial marker
  and timestamp, notes, timestamps.
- `attendance_corrections`: prior/new statuses and notes, reason, actor, timestamp.
- `attendance_session_history`: before/after values for time changes,
  finalization, reopen, and cancellation.
- `outbox_events`: transactional event payloads and future worker delivery state.

UUID primary keys, service-owned restrictive foreign keys, indexes, status/time/
reason checks, and uniqueness constraints enforce integrity. A partial unique
index prevents duplicate unscheduled section/date sessions when occurrence is
NULL. Scheduled sessions are unique by section/date/occurrence. Cancelled sessions
retain their logical identity. No attendance deletion endpoints are exposed.

## Configuration

Copy `.env.example` for local execution. Compose supplies configuration explicitly
and does not load this service's `.env`.

| Setting | Default / meaning |
| --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://attendance:attendance@localhost:5436/attendance_db` |
| `ACADEMIC_SERVICE_BASE_URL` | `http://localhost:8002`; origin only, client adds `/api/v1` |
| `ACADEMIC_SERVICE_TIMEOUT_SECONDS` | 5 seconds per HTTP request |
| `ACADEMIC_SERVICE_MAX_PAGES` | 100 pages, 100 items/page; incomplete traversal fails closed |
| `JWT_ISSUER` | Logical Identity issuer, `http://localhost:8001` in development |
| `JWT_ACCESS_AUDIENCE` | `smart-education-api` |
| `JWT_JWKS_URL` | Trusted `http://localhost:8001/.well-known/jwks.json` |
| `JWT_LEEWAY_SECONDS` | 5; maximum 30 |
| `JWT_JWKS_CACHE_SECONDS` | 300; keys expire with the JWKS set |
| `JWT_JWKS_TIMEOUT_SECONDS` | 5 |
| `LOW_ATTENDANCE_THRESHOLD_PERCENT` | 75; inclusive configuration range 0–100 |
| `CORS_ORIGINS` | JSON array, default `["http://localhost:5173"]` |
| `ENVIRONMENT` | `development`; production requires HTTPS issuer |

Dates/times describe an institution-local session on one civil date. Times must
be supplied as a pair, have no UTC offset, and satisfy ends > starts; overnight
classes are not supported in Sprint 3. Audit/mark timestamps are UTC. There is
no timetable integration yet: `schedule_occurrence_id` is an opaque optional
external reference, not a schedule owned or validated by Attendance.

## Authorization and Academic integration

The [Identity contract](../../docs/api/identity-authentication.md) is implemented
locally, following Academic's trust pattern. Only RS256 access tokens are accepted,
with `typ=at+jwt`, nonempty trusted `kid`, matching issuer/audience, `type=access`,
UUID `sub`, valid roles, nonempty `jti`, and required valid `iat`/`nbf`/`exp` claims.
Untrusted JWT key URLs and client role headers do not affect authorization.
JWKS discovery is synchronous in FastAPI's thread pool, cached and bounded.
Missing/invalid credentials return 401 with a Bearer challenge; missing roles or
resource permission return 403. JWKS network failures without a usable trusted
cache return 503. Identity role/account changes follow access-token expiration
semantics; this service does not query Identity's database or refresh tokens.

| Actor | Permission |
| --- | --- |
| Admin | All sessions/reports/history; create/mark/finalize/cancel; audited corrections and reopen |
| Teacher | Create/view/mark/correct/finalize own assigned sections; own section reports/history; cancel open sessions |
| Student | Own detailed attendance and summaries through `/students/me`; no staff APIs or mutations |

The HTTP AcademicClient forwards the verified request's bearer token. Academic's
`GET /api/v1/sections/{id}` enforces active teacher assignment to the caller's JWT
subject. Teacher list/report scope is obtained through the paginated Academic
section list. Enrollment checks use the full paginated section roster and its
`external_user_id` values, never Academic profile IDs or copied enrollment tables.
The adapter validates response schemas, identifiers, roster totals, pagination,
and duplicates. Its caches live for one Attendance request only; assignment
revocation is checked again on the next request.

Academic 404 becomes 404, 401/403 becomes 403, and timeout/network/other HTTP/
malformed or changing roster responses become 503. Redirects are not followed.
All marking/finalization fails closed on roster verification failures. External
checks precede database mutations and are not a distributed transaction; a
roster change during a request cannot be locked across databases.

Academic Sprint 2 denies student tokens. Student self-views therefore read only
Attendance-owned records filtered by the verified `sub`, without calling Academic
or requiring an elevated service credential. This preserves historical student
access after enrollment ends. Administrators can also read/correct historical
Attendance records during an Academic outage. Creating, marking, and finalizing
still require Academic to validate relationships. Teachers always require current
Academic assignment checks.

## Lifecycle, marking, and correction policy

Sessions start `OPEN`. Bulk `PUT` creates marks in an open session only. Every
student is validated before any writes, duplicate payload student IDs return 422,
and a non-enrolled student returns 403. The entire batch and its outbox events
commit or roll back together. Batches contain 1–1,000 records. An identical retry
in an open session succeeds without new rows/events. A previously marked student
with a different status or notes returns 409 for the whole batch; use a correction.

Finalization requires a mark for every current Academic roster member. Existing
marks for students who have since left are retained as historical facts. An empty
roster can finalize an empty sheet. Finalization captures its actor/time and blocks
normal writes for everyone, including admins. PostgreSQL session row locks
serialize bulk writes, corrections, time changes, and lifecycle transitions.

Teacher corrections require an open session, current section assignment, and
current student roster membership. Admin corrections can change existing records
in open or finalized sessions, including former students; they cannot add new
records to finalized sessions. Every actual status or note change requires a
nonempty reason and writes a correction with before/after values, actor, and UTC
time. Initial `marked_by_user_id`/`marked_at` remain unchanged. Exact correction
retries are no-ops. There is no time-based approval window in this sprint.

Only an admin can reopen a finalized session, with a reason. Reopening clears
current finalization metadata and records the prior values in session history.
Open sessions may be cancelled by their assigned teacher/admin; finalized sessions
may be cancelled by admin only. Cancellation is terminal, preserves every record/
correction/history row, and prevents further writes/reopen. Cancelled attendance
is omitted from student views and calculations but remains available through
authorized staff session/record/history endpoints.

Session `PATCH` changes civil times with a required reason, only while open.
Section/date/occurrence/course/semester references are immutable after creation;
cancel a mistaken session instead of silently moving its attendance to another class.

## Attendance calculations

Statistics use records in `FINALIZED` sessions only. Open marks are immediately
visible in student detail views but do not affect official percentages. There is
no inferred absence for unmarked sessions.

```text
considered = PRESENT + ABSENT + LATE
attended = PRESENT + LATE
percentage = 100 × attended / considered
```

`EXCUSED` is reported separately and excluded from the denominator. With no
considered records, percentage is `null` and low-attendance is false. Display
percentages round to two decimals; low-attendance compares the unrounded value
strictly below the configured threshold. Exactly 75% is not low at a 75% threshold.

Student summary returns overall counts, per-section breakdown, and per-course
breakdown across sections. Section summary pools student-session opportunities;
its counts are not counts of distinct class meetings. A student/section summary
and the low-attendance report use one student's marks in one section. Reports
support date, course, and semester filters. Weekly/monthly views use date ranges.
Potentially large response collections are paginated; aggregate queries compute
raw status counts in SQL and apply percentage policy in the service layer.

## Transactional outbox

Session creation, marking, corrections, finalization, reopen, cancellation,
and time changes insert events in the same database transaction as the change.
Finalization and finalized corrections also evaluate section attendance and emit
`attendance.low_attendance_detected` for students currently below threshold.
Repeated evaluations may emit additional detections; consumers should deduplicate
delivery by the outbox event UUID and apply notification policy separately.

Events contain a version, session/section IDs, actor, occurrence timestamp, and
event-specific record/student/status/percentage fields. There is no broker or
background publishing process in Sprint 3.

`OutboxRepository` provides future-worker primitives: `claim` uses PostgreSQL
`FOR UPDATE SKIP LOCKED` and a lease; `acknowledge` checks the current worker/lease;
`release` records an error and retry time. Pass a fresh UUID as the worker/owner ID
for each claim batch; never reuse it across leases, even within one process.
This prevents a slow delivery attempt from acknowledging a later claim.
The worker owns transactions and commits its claim
before external delivery. Delivery is at least once; a crash can replay an event.
Use event UUIDs for downstream idempotency. Published rows retain their payload.
The PostgreSQL tests exercise claims, concurrent exclusion, retry, and acknowledgment.

## APIs

All business APIs are under `/api/v1`. Lists use `limit` (default 50, maximum 100)
and `offset` (default 0). Summary `limit`/`offset` apply separately to each breakdown;
overall totals always cover the complete filtered set.

| Method | Path |
| --- | --- |
| POST, GET | `/sessions` |
| GET, PATCH | `/sessions/{session_id}` |
| POST | `/sessions/{session_id}/finalize` |
| POST | `/sessions/{session_id}/reopen` |
| POST | `/sessions/{session_id}/cancel` |
| GET, PUT | `/sessions/{session_id}/records` |
| PATCH | `/sessions/{session_id}/records/{student_user_id}` |
| GET | `/sessions/{session_id}/history` |
| GET | `/sessions/{session_id}/records/{student_user_id}/history` |
| GET | `/students/me/attendance` |
| GET | `/students/me/attendance/summary` |
| GET | `/sections/{section_id}/attendance` |
| GET | `/sections/{section_id}/summary` |
| GET | `/sections/{section_id}/students/{student_user_id}/summary` |
| GET | `/reports/low-attendance` |
| GET | `/health`, `/ready` |

The two history routes extend the requested API to expose preserved audit records.
Creation returns 201; updates/transitions return 200; validation returns 422;
duplicates/lifecycle conflicts return 409. Error responses use `detail`, `code`,
`request_id`, and optional validation `errors`; `X-Request-ID` correlates responses.
Request input values and SQL/database details are not echoed in errors.

Create a session with an admin or assigned-teacher access token:

```http
POST /api/v1/sessions
Authorization: Bearer <access_token>
Content-Type: application/json

{"section_id":"<academic-section-uuid>","session_date":"2026-10-07","starts_at":"09:00:00","ends_at":"10:00:00"}
```

Mark a sheet using external Identity user UUIDs from the Academic roster:

```http
PUT /api/v1/sessions/<session-uuid>/records
Authorization: Bearer <access_token>
Content-Type: application/json

{"records":[{"student_user_id":"<student-user-uuid>","status":"PRESENT"},{"student_user_id":"<another-user-uuid>","status":"ABSENT"}]}
```

Correction body: `{"status":"EXCUSED","reason":"Approved absence","notes":"Documentation reviewed"}`.
Reopen/cancel body: `{"reason":"Administrative correction"}`. Finalize needs no body.
Interactive OpenAPI schemas and examples: <http://localhost:8003/docs>.

## Run from the repository root

Start the database and install the independent Python 3.12 environment:

```powershell
docker compose -f docker-compose.attendance.yml up -d attendance-db
uv venv --python 3.12 services/attendance-service/.venv
uv pip install --python services/attendance-service/.venv/Scripts/python.exe -r services/attendance-service/requirements-dev.txt
if (-not (Test-Path services/attendance-service/.env)) {
    Copy-Item services/attendance-service/.env.example services/attendance-service/.env
}
Push-Location services/attendance-service
.venv/Scripts/python.exe -m alembic upgrade head
.venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8003
# After stopping the server:
Pop-Location
```

Create `.env` only if it does not already exist; preserve your local settings.
If overriding `ATTENDANCE_DB_PORT`, set the matching host port in `.env`'s
`DATABASE_URL`. Start/configure Identity and Academic using their existing READMEs.
On Linux/macOS use the equivalent `.venv/bin/python` paths.

Docker-only independent stack:

```powershell
docker compose -f docker-compose.attendance.yml up --build -d
```

Host API port is 8003, internal port is 8000. PostgreSQL host port is
`${ATTENDANCE_DB_PORT:-5436}`; the API always uses `attendance-db:5432` internally.
Compose runs the migration job successfully before starting the API. Health/readiness
work independently; authenticated academic workflows need the two external services.

After preparing Identity's signing keys/schema/RBAC according to its README, run
the three services on one Compose network without changing their existing files:

```powershell
docker compose -f docker-compose.identity.yml -f docker-compose.academic.yml -f docker-compose.attendance.yml up --build -d identity-service academic-service attendance-service
```

Docker defaults use `http://academic-service:8000` and
`http://identity-service:8000/.well-known/jwks.json`. Separate deployments can set
`ATTENDANCE_ACADEMIC_SERVICE_BASE_URL`, `ATTENDANCE_ACADEMIC_SERVICE_TIMEOUT_SECONDS`,
`ATTENDANCE_JWT_ISSUER`, `ATTENDANCE_JWT_ACCESS_AUDIENCE`, and `ATTENDANCE_JWT_JWKS_URL`
in the Compose environment. Use network-reachable trusted service URLs. No
Windows-only host alias is required or hard-coded. Development database credentials
in Compose must be replaced by deployment secrets for production.

`/health` checks the process only. `/ready` checks Attendance PostgreSQL connectivity
and that its revision matches the bundled Alembic head; it never checks Academic
or Identity. A ready service can still return dependency 503s for academic workflows.

## Tests and migration checks

From the repository root:

```powershell
Push-Location services/attendance-service
.venv/Scripts/python.exe -m ruff check .
.venv/Scripts/python.exe -m ruff format --check .
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe -m alembic upgrade head
.venv/Scripts/python.exe -m alembic check
Pop-Location
docker build -t smart-education-attendance:dev services/attendance-service
docker compose -f docker-compose.attendance.yml config --quiet
```

Fast tests use SQLite foreign keys, RSA-signed tokens, and an AcademicClient fake;
HTTP adapter tests validate actual wire contracts with HTTPX transports. PostgreSQL
tests are marked `postgres` and skip unless `ATTENDANCE_TEST_DATABASE_URL` points
to a dedicated disposable database whose name starts `attendance_test_`.
They clear attendance tables and downgrade/rebuild its schema; never point them
at a development or production database.

Example disposable database and full verification from the repository root:

```powershell
docker run -d --name attendance-test-db -p 5546:5432 -e POSTGRES_DB=attendance_test_core -e POSTGRES_USER=attendance_test -e POSTGRES_PASSWORD=attendance_test postgres:16
$env:ATTENDANCE_TEST_DATABASE_URL = "postgresql+psycopg://attendance_test:attendance_test@localhost:5546/attendance_test_core"
Push-Location services/attendance-service
.venv/Scripts/python.exe -m pytest -q
# Explicit migration round-trip on that disposable database only:
$env:DATABASE_URL = $env:ATTENDANCE_TEST_DATABASE_URL
.venv/Scripts/python.exe -m alembic upgrade head
.venv/Scripts/python.exe -m alembic downgrade base
.venv/Scripts/python.exe -m alembic upgrade head
.venv/Scripts/python.exe -m alembic check
Remove-Item Env:DATABASE_URL
Pop-Location
docker rm -f -v attendance-test-db
Remove-Item Env:ATTENDANCE_TEST_DATABASE_URL
```

The PostgreSQL suite tests nullable/scheduled session creation races, identical/
conflicting record submissions, invalid roster rollback, mid-bulk storage failure,
finalization winning against a waiting writer, uniqueness/status constraints,
outbox worker leases, and migration round-trip/drift. CI installs dependencies,
runs Ruff/formatting/the full PostgreSQL test suite, validates migrations/Compose,
and builds the image without modifying Identity or Academic CI.

Run the real-service Docker integration check from the repository root:

```powershell
services/attendance-service/.venv/Scripts/python.exe services/attendance-service/scripts/smoke_stack.py
```

It builds Attendance and the existing Academic source, starts two disposable
PostgreSQL databases, runs their own migrations, and provides a public-only test
JWKS server. It provisions Academic fixtures through HTTP APIs and tests actual
teacher assignment/roster verification, marking/finalization, student self-access,
admin corrections/history, health/readiness/OpenAPI, non-root execution, and
Academic outage behavior. Test JWTs use temporary RSA keys; this does not replace
an end-to-end Identity login test. The script removes its uniquely named containers,
volumes, network, and temporary public-key file, leaving development services untouched.

Sprint 3 does not add a broker, scheduler, CSV/PDF exports, performance/load testing,
or an institution-specific approval/time-window policy. Those require their later
implementation and acceptance work; this service provides the attendance APIs,
audit trail, and outbox needed for those integrations.
