"""Executes migration against pre-existing SQLite state; does not prove PG upgrade."""
from pathlib import Path
from sqlalchemy import create_engine,text
from alembic.runtime.migration import MigrationContext
from alembic.operations import Operations
import importlib.util

def test_draft_migration_preserves_existing_rows_and_blocks_unsafe_downgrade():
    path=Path(__file__).resolve().parents[2]/'services/scheduling-service/migrations/versions/0004_schedule_draft_state.py'
    spec=importlib.util.spec_from_file_location('draft_migration_smoke',path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    engine=create_engine('sqlite+pysqlite:///:memory:')
    with engine.begin() as db:
        db.execute(text("CREATE TABLE schedule_entries (id INTEGER PRIMARY KEY, status TEXT CONSTRAINT ck_schedule_status CHECK (status IN ('ACTIVE','CANCELLED')) NOT NULL)"))
        db.execute(text("INSERT INTO schedule_entries VALUES (1,'ACTIVE'),(2,'CANCELLED')"))
        ctx=MigrationContext.configure(db)
        with Operations.context(ctx):module.upgrade()
        db.execute(text("INSERT INTO schedule_entries VALUES (3,'DRAFT')"))
        assert db.execute(text('SELECT status FROM schedule_entries ORDER BY id')).scalars().all()==['ACTIVE','CANCELLED','DRAFT']
        try:
            with Operations.context(ctx):module.downgrade()
        except RuntimeError as error:
            assert 'DRAFT' in str(error)
        else:
            raise AssertionError('Unsafe downgrade was not blocked')
