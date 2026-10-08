from smartedu_infra.database import build_engine, pool_plan
from smartedu_infra.settings import DatabaseSettings


def test_pool_plan_uses_bounded_connections():
    settings = DatabaseSettings(
        DATABASE_URL="sqlite+pysqlite:///:memory:",
        DB_POOL_SIZE=7,
        DB_MAX_OVERFLOW=11,
        DB_POOL_TIMEOUT_SECONDS=12,
        DB_POOL_RECYCLE_SECONDS=900,
        DB_STATEMENT_TIMEOUT_MS=5000,
        DB_APPLICATION_NAME="test-service",
    )
    plan = pool_plan(settings)

    assert plan.pool_size == 7
    assert plan.max_overflow == 11
    assert plan.pool_timeout_seconds == 12
    assert plan.statement_timeout_ms == 5000
    assert plan.application_name == "test-service"


def test_sqlite_engine_can_be_created_without_postgres_pool_arguments():
    settings = DatabaseSettings(
        DATABASE_URL="sqlite+pysqlite:///:memory:",
        DB_APPLICATION_NAME="test",
    )
    engine = build_engine(settings)
    with engine.connect() as connection:
        assert connection.exec_driver_sql("SELECT 1").scalar_one() == 1
    engine.dispose()
