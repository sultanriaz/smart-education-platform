# Sprint 6 Verification

Verification performed while building this package:

- FastAPI application import / OpenAPI generation: **PASS**
- OpenAPI paths loaded: **17**
- pytest: **35 passed, 1 skipped**
- skipped test: real PostgreSQL concurrency race test because `FACILITY_TEST_POSTGRES_URL` was not available in the build sandbox
- Python compilation: **PASS**
- Alembic initial upgrade against disposable SQLite DB: **PASS**
- Alembic downgrade to base: **PASS**
- Alembic re-upgrade: **PASS**
- Alembic schema drift check: **PASS** (`No new upgrade operations detected`)
- UTF-8 BOM scan: **PASS**, no BOM-bearing deliverable files found

Not claimed as executed in this build sandbox:

- Ruff lint / format, because Ruff was not preinstalled and the sandbox has no package-network access
- Docker image / Compose runtime, because Docker is unavailable in the build sandbox
- real PostgreSQL advisory-lock race test, because no PostgreSQL test URL was available
- live Identity JWKS integration, because the user's running Identity service is not accessible from this sandbox
- live Scheduling/Notification integration, because the user's merged repository is not mounted here

The CI workflow and local verification scripts execute these checks on the target repository/workstation. The integration pass must inspect the actual Sprint 1-5 contracts before adapting peer services.
