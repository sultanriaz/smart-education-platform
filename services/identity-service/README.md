# Identity Service

Independent FastAPI service for authentication, user identity, refresh sessions and RBAC.

## Local URLs
- API: http://localhost:8001
- Swagger: http://localhost:8001/docs
- Public signing keys: http://localhost:8001/.well-known/jwks.json
- PostgreSQL host port: 5434

## First run
From repository root:

```powershell
docker compose -f docker-compose.identity.yml up -d identity-db
cd services/identity-service
Copy-Item .env.example .env
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
python -m app.scripts.generate_jwt_keys
alembic upgrade head
python -m app.scripts.seed_rbac
uvicorn app.main:app --reload --port 8001
```

Run tests with `pytest -q`.

## Existing installations

Update existing `.env` files using `.env.example`: replace `JWT_ALGORITHM=HS256`
with `JWT_ALGORITHM=RS256`, remove `JWT_SECRET_KEY`, and configure the key file,
key ID, issuer, and audiences. Keep any unrelated local configuration.
Generate keys only if none exist. Previously issued HS256 tokens are rejected;
users must sign in again. No database schema migration is needed for this change.
Do not rerun the historical root `sprint_identity_service.ps1` generator: it
contains the old service implementation and overwrites current files.

## Docker development

After installing dependencies and generating local keys, run from repository root:

```powershell
docker compose -f docker-compose.identity.yml build identity-service
docker compose -f docker-compose.identity.yml up -d identity-db
docker compose -f docker-compose.identity.yml run --rm identity-service alembic upgrade head
docker compose -f docker-compose.identity.yml run --rm identity-service python -m app.scripts.seed_rbac
docker compose -f docker-compose.identity.yml up -d identity-service
```

Configure bootstrap administrator credentials explicitly when needed; Compose
does not read the service's local `.env`. The private key is mounted at runtime
through a Compose secret and excluded from the image. Do not put it in the image
or supply it to another domain service. Local Compose is development configuration.

## Transactions and tests

Application services own transaction commits and rollbacks. Repositories flush
without committing. Registration/login and their audit records are atomic;
failed login attempts intentionally commit their audit before returning 401.
Refresh consumes the subject-owned live token with one conditional UPDATE,
creates a replacement, and writes its audit in the same transaction. A failed
replacement rolls back consumption. Logout is idempotent and atomic with its audit.

```powershell
python -m pytest -q -p no:cacheprovider
# Dedicated disposable database only; tests reject other database names.
$env:IDENTITY_TEST_DATABASE_URL = "postgresql+psycopg://test:test@localhost:5544/identity_test_auth"
python -m pytest -q tests/integration/test_refresh_postgres.py -p no:cacheprovider
```

PostgreSQL tests apply the existing Alembic migration and clear identity tables
in that dedicated test database. They check concurrent rotation and rollback.
The remaining tests use SQLite and temporary RSA keys.

The [authentication contract](../../docs/api/identity-authentication.md) defines
consumer validation, authorization freshness, and signing-key rotation.
