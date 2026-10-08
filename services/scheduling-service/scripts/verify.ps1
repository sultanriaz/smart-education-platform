$ErrorActionPreference = "Stop"

Write-Host "== Scheduling Service verification =="
python -m pytest -q
python -m ruff check .
python -m ruff format --check .
python -m alembic -c .\alembic.ini upgrade head
python -m alembic -c .\alembic.ini check
python -c "from app.main import app; print(app.title)"
Write-Host "Scheduling Service verification complete."
