# Sprint 7 Verification

Verification performed while building this package:

- Python compilation: **PASS**
- FastAPI import/OpenAPI generation: **PASS** (12 paths)
- pytest: **27 passed, 1 skipped**
- skipped test: PostgreSQL-specific duplicate-target constraint test because `TEST_POSTGRES_URL` was not available in the build environment
- Alembic upgrade on disposable SQLite DB: **PASS**
- Alembic downgrade to base: **PASS**
- Alembic re-upgrade: **PASS**
- Alembic schema drift check: **PASS**
- UTF-8 BOM scan: **PASS**
- Ruff: **NOT RUN** in the build environment because the executable is unavailable here
- Docker/MinIO runtime: **NOT RUN** because Docker is unavailable in the build environment
- Live Identity/Academic/Notification integration: **NOT RUN** because those services are not present in this isolated build environment

Repository integration should therefore run the remaining checks locally.

```powershell
cd services\learning-service
python -m compileall app tests
pytest -q
ruff check .
ruff format --check .
python -m alembic -c .\alembic.ini upgrade head
python -m alembic -c .\alembic.ini downgrade base
python -m alembic -c .\alembic.ini upgrade head
python -m alembic -c .\alembic.ini check
```

From repository root:

```powershell
docker compose -f .\docker-compose.learning.yml build
docker compose -f .\docker-compose.learning.yml up -d
docker compose -f .\docker-compose.learning.yml ps
Invoke-RestMethod http://localhost:8007/health
Invoke-RestMethod http://localhost:8007/ready
```

For the real PostgreSQL-specific test:

```powershell
$env:TEST_POSTGRES_URL="postgresql+psycopg://learning:learning@localhost:5440/learning_db"
cd services\learning-service
pytest -q
```

The merge agent must report exact results rather than marking unsupported checks as passed.
