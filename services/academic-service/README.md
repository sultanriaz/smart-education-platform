# Academic Core Service

Independent FastAPI service owning `academic_db`. Python 3.11+; SQLAlchemy 2,
Pydantic 2, PostgreSQL, and Alembic. Identity owns authentication; Academic owns
academic data and resource authorization.

## Local development

From the repository root, start the academic database:

```powershell
docker compose -f docker-compose.academic.yml up -d academic-db
cd services/academic-service
Copy-Item .env.example .env
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8002
```

API: <http://localhost:8002>; OpenAPI UI: <http://localhost:8002/docs>.
PostgreSQL: localhost:5435, database `academic_db`. `/health` is process liveness;
`/ready` returns 200 only when PostgreSQL is reachable and the database revision
matches the bundled Alembic head, otherwise 503. Startup never creates tables automatically.

Start Identity using its [setup instructions](../identity-service/README.md).
Academic accepts Identity access tokens with `admin` or `teacher` role claims.
It uses only Identity's public JWKS endpoint; no private keys or Identity imports.
`JWT_ISSUER` is the logical issuer and `JWT_JWKS_URL` is the trusted network URL.
For local Python development, both default to Identity at localhost:8001.

## Docker

Start the independent stack:

```powershell
docker compose -f docker-compose.academic.yml up --build -d
```

Compose runs `academic-migrate` before starting the API, mounts a separate academic
database volume, and exposes the service on port 8002. The image runs as a non-root
user. Compose credentials are for development. Compose does not load the service's
local `.env`; application settings are explicit in the Compose file.

The default container JWKS address is `http://identity-service:8000/.well-known/jwks.json`.
After preparing Identity's keys, database, and RBAC using its instructions, run
both services in the same Compose project/network:

```powershell
docker compose -f docker-compose.identity.yml -f docker-compose.academic.yml up --build -d identity-service academic-service
```

If Identity instead runs on the host, configure its reachable address before
starting the independent stack on Docker Desktop:

```powershell
$env:ACADEMIC_JWT_JWKS_URL = "http://host.docker.internal:8001/.well-known/jwks.json"
docker compose -f docker-compose.academic.yml up --build -d
```

Compose also accepts `ACADEMIC_JWT_ISSUER` and `ACADEMIC_JWT_ACCESS_AUDIENCE`.
Database readiness does not depend on Identity availability. Authenticated requests
fail closed with 503 when public key discovery is unavailable without a trusted
cached key. Production uses an HTTPS issuer and trusted transport for JWKS.

## API and domain

See the [Academic API contract](../../docs/api/academic-service.md) for routes,
authorization, identifiers, validation, and status transitions.

```text
app/api/          HTTP routing and dependencies
app/schemas/      Pydantic request/response validation
app/security/     Local JWT contract verification and role dependencies
app/services/     Domain rules, resource access, transactions
app/repositories/SQLAlchemy queries and persistence, without commits
app/domain/      Service-owned models and enums
app/db/          Declarative base and PostgreSQL sessions
migrations/      Versioned academic schema
tests/           API, JWT, domain, health, and PostgreSQL checks
```

All primary keys are UUIDs. Academic profile IDs are distinct from Identity
`external_user_id` UUIDs. External user IDs have no foreign key to Identity.
Section rosters are derived from active enrollments, without duplicate roster
storage. Academic does not store names, email addresses, credentials, or Identity
roles in profiles.

## Validation

```powershell
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
```

Fast tests use SQLite with foreign keys enabled and generated RSA keys. PostgreSQL
tests verify real migrations, constraints, transaction rollback, concurrent final
seat allocation, and concurrent registration in two sections of the same course.
They require a dedicated disposable database named `academic_test_*`; they clear
academic tables and test migration downgrade/upgrade in that database.

```powershell
$env:ACADEMIC_TEST_DATABASE_URL = "postgresql+psycopg://test:test@localhost:5545/academic_test_core"
python -m pytest -q
```

PostgreSQL tests skip when that variable is absent and reject unsafe database
names. CI runs the full suite with PostgreSQL and validates the Docker build.

Migrations remain standalone and frozen; inspect changes before applying:

```powershell
alembic upgrade head
alembic check
alembic upgrade head --sql
```
