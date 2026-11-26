"""Readiness must verify the schema revision, not only database connectivity."""

from functools import lru_cache
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text


@lru_cache
def migration_head(config_path: str):
    config = Config(config_path)
    # Make revision discovery independent of the caller's working directory.
    config.set_main_option("script_location", str(Path(config_path).parent / "migrations"))
    return ScriptDirectory.from_config(config).get_current_head()


def assert_owned_revision(db, config_path: str):
    actual = db.scalar(text("SELECT version_num FROM alembic_version"))
    if actual != migration_head(config_path):
        raise ValueError("Database migrations are not current")
