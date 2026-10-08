$ErrorActionPreference = "Stop"
python -m compileall app tests
ruff check .
ruff format --check .
pytest -q
python -m alembic -c .\alembic.ini upgrade head
python -m alembic -c .\alembic.ini check
Write-Host "Learning service verification completed."
