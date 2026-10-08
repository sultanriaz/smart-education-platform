# Learning Resource Service — Sprint 7

Independent FastAPI service for course/section learning materials and the deterministic foundation for personalized learning.

## Ownership

This service owns `learning_db` and the object-storage keys for uploaded learning files. It does **not** own users, students, teachers, courses, sections, enrollments, attendance, schedules, bookings, quizzes, or notifications.

External academic references are UUID values only. Authorization against sections/courses is delegated to Academic Service through `AcademicClient`.

## Capabilities

- Admin-managed resource categories
- Teacher/admin resource authoring
- SECTION and COURSE targeting
- DRAFT / PUBLISHED / ARCHIVED lifecycle
- Immutable content versions
- FILE, LINK, VIDEO and NOTE resources
- S3-compatible object storage or local storage
- SHA-256 file integrity metadata
- Student resource library filtered through Academic Service enrollment access
- VIEW / DOWNLOAD access history
- Deterministic recommendations using enrollment scope, unread state and recency
- Transactional outbox events for Notification/Reporting integration
- JWT/JWKS authorization consistent with the platform trust model
- Health and readiness probes

## Local ports

- API: `http://localhost:8007`
- Swagger: `http://localhost:8007/docs`
- PostgreSQL: `localhost:5440`
- MinIO S3 API: `localhost:9002`
- MinIO console: `localhost:9003`

## Core API

- `GET/POST /api/v1/categories`
- `GET/POST /api/v1/resources`
- `GET/PATCH /api/v1/resources/{resource_id}`
- `POST /api/v1/resources/{resource_id}/versions`
- `GET /api/v1/resources/{resource_id}/versions`
- `POST /api/v1/resources/{resource_id}/upload`
- `POST /api/v1/resources/{resource_id}/publish`
- `POST /api/v1/resources/{resource_id}/archive`
- `GET /api/v1/resources/{resource_id}/download`
- `GET /api/v1/students/me/resources`
- `GET /api/v1/students/me/recommendations`
- `GET /health`
- `GET /ready`

## Authorization

- `admin`: all resource/category administration
- `teacher`: can create and modify only their own resources, and only for course/section targets Academic Service confirms they manage
- `student`: read/download only PUBLISHED resources for targets Academic Service confirms they can access

## Recommendation rule

Sprint 7 intentionally uses a deterministic, explainable baseline rather than ML:

- +100 points when the student has never viewed/downloaded the resource
- +20 points when published within `RECOMMENDATION_RECENT_DAYS`
- up to +10 points for tagged resources

The API returns the score and human-readable reason. A later personalization sprint may replace or augment this scoring without changing resource ownership.

## Storage

`STORAGE_BACKEND=local` stores objects below `LOCAL_STORAGE_PATH`.

`STORAGE_BACKEND=s3` uses any S3-compatible service. Docker Compose configures MinIO and bucket `learning-resources` automatically.

Files are downloaded through Learning Service so private object-store addresses are never exposed to the browser.

## Academic Service contract

The included HTTP adapter expects internal access-check endpoints for teacher and student course/section access. During repository integration, adapt the adapter to the actual Sprint 2 contract rather than adding database access.

Dependency outages map to HTTP 503.

## Notification integration

Publishing a resource writes `learning.resource_published` to the same database transaction as the resource state change. `app/workers/outbox_relay.py` can relay unpublished events to Notification Service's internal event endpoint.

## Setup without Docker

```powershell
Copy-Item .env.example .env
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
python -m alembic -c .\alembic.ini upgrade head
uvicorn app.main:app --reload --port 8007
```

## Tests

```powershell
pytest -q
ruff check .
ruff format --check .
```

For PostgreSQL-specific tests:

```powershell
$env:TEST_POSTGRES_URL="postgresql+psycopg://learning:learning@localhost:5440/learning_db"
pytest -q
```

## Docker

From repository root:

```powershell
docker compose -f .\docker-compose.learning.yml up -d --build
```

Then open `http://localhost:8007/docs`.
