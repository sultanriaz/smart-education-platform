# Sprint 4 verification performed during package build

Verified in the build environment:

- application import: PASS (`Smart Education Scheduling Service`, routes loaded)
- pytest: PASS — 27 passed, 1 PostgreSQL-only concurrency test skipped because no PostgreSQL test URL was available
- Python bytecode compilation: PASS
- Alembic upgrade -> downgrade -> upgrade: PASS using SQLite compatibility verification
- Alembic schema drift check: PASS (`No new upgrade operations detected`)

Not executable in the build environment:

- Docker runtime/build: Docker CLI is unavailable here
- Ruff: Ruff is not preinstalled and this environment cannot download packages
- PostgreSQL advisory-lock concurrency test: requires `POSTGRES_TEST_URL`

These checks are included in the package and should be run in the target repository/Windows Docker environment before the sprint is tagged complete.
