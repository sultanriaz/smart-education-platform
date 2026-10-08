# Sprint 4 Integration Package

This archive is designed to be extracted at the root of `smart-education-platform`.

It adds:

```text
services/scheduling-service/
docker-compose.scheduling.yml
.github/workflows/scheduling-service-ci.yml
SPRINT_04_INTEGRATION.md
```

It does not overwrite Identity, Academic, Attendance, or frontend files.

## Suggested merge sequence

```powershell
# from repository root
Expand-Archive .\sprint_04_scheduling.zip -DestinationPath . -Force

cd services\scheduling-service
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env

cd ..\..
docker compose -f .\docker-compose.scheduling.yml up -d scheduling-db

cd services\scheduling-service
python -m alembic -c .\alembic.ini upgrade head
pytest -q
ruff check .
ruff format --check .
uvicorn app.main:app --reload --port 8004
```

Then have Codex inspect the actual Sprint 2 Academic API and adjust only the configurable Academic client contract if route/response names differ.

## Expected public development endpoint

```text
http://localhost:8004/docs
```

## Important architecture rule

Scheduling owns schedule/timetable state only. It must never read another service's database.
