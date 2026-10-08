$ErrorActionPreference = "Stop"
python -m compileall app tests
ruff check .
ruff format --check .
pytest -q
python -m alembic upgrade head
python -m alembic downgrade base
python -m alembic upgrade head
python -m alembic check
