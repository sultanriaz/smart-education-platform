$ErrorActionPreference = "Stop"
python -m ruff check .
python -m ruff format --check .
python -m pytest -q
python -m alembic upgrade head
python -m alembic downgrade base
python -m alembic upgrade head
python -m alembic check
Write-Host "Notification service verification passed."
