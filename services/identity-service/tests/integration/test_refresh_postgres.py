"""Run with IDENTITY_TEST_DATABASE_URL pointing at an isolated identity_test_* database."""

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, delete, func, select
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.db.base import Base
from app.domain.entities.audit import SecurityAuditEvent
from app.domain.entities.refresh_token import RefreshToken
from app.domain.entities.role import Role
from app.repositories.token_repository import TokenRepository
from app.schemas.user import UserRegister
from app.services.auth_service import AuthService


@pytest.fixture(scope="module")
def postgres_engine():
    url = os.getenv("IDENTITY_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set IDENTITY_TEST_DATABASE_URL to run PostgreSQL integration tests.")
    parsed = make_url(url)
    if parsed.get_backend_name() != "postgresql" or not (parsed.database or "").startswith(
        "identity_test_"
    ):
        pytest.fail("Integration tests require a dedicated PostgreSQL identity_test_* database.")
    root = Path(__file__).resolve().parents[2]
    config = Config(str(root / "alembic.ini"))
    config.set_main_option("script_location", str(root / "migrations"))
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(settings, "DATABASE_URL", url)
        command.upgrade(config, "head")
    engine = create_engine(
        url,
        connect_args={
            "options": "-c statement_timeout=10000 -c lock_timeout=5000",
        },
    )
    yield engine
    engine.dispose()


@pytest.fixture()
def refresh_setup(postgres_engine):
    with postgres_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(delete(table))
    with Session(postgres_engine, expire_on_commit=False) as db:
        db.add(Role(name="student"))
        db.commit()
        service = AuthService(db)
        user = service.register(
            UserRegister(
                email="postgres@example.edu",
                full_name="Postgres Student",
                password="StrongPass123!",
            )
        )
        pair = service.login(user.email, "StrongPass123!")
    return pair


def test_concurrent_refresh_only_one_request_succeeds(postgres_engine, refresh_setup, monkeypatch):
    barrier = Barrier(2)
    original_consume = TokenRepository.consume

    def consume_together(self, **kwargs):
        barrier.wait(timeout=10)
        return original_consume(self, **kwargs)

    monkeypatch.setattr(TokenRepository, "consume", consume_together)

    def refresh():
        with Session(postgres_engine, expire_on_commit=False) as db:
            try:
                AuthService(db).refresh(refresh_setup.refresh_token)
                return "success"
            except AuthenticationError:
                return "rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(refresh) for _ in range(2)]
        outcomes = [future.result(timeout=20) for future in futures]
    assert sorted(outcomes) == ["rejected", "success"]
    with Session(postgres_engine) as db:
        assert db.scalar(select(func.count()).select_from(RefreshToken)) == 2
        assert (
            db.scalar(
                select(func.count())
                .select_from(RefreshToken)
                .where(
                    RefreshToken.revoked_at.is_(None),
                )
            )
            == 1
        )
        assert (
            db.scalar(
                select(func.count())
                .select_from(SecurityAuditEvent)
                .where(
                    SecurityAuditEvent.action == "auth.refreshed",
                )
            )
            == 1
        )


def test_postgres_refresh_audit_failure_rolls_back(postgres_engine, refresh_setup, monkeypatch):
    with Session(postgres_engine, expire_on_commit=False) as db:
        service = AuthService(db)

        def fail_audit(**kwargs):
            raise RuntimeError("Audit storage failed")

        monkeypatch.setattr(service.audit, "record", fail_audit)
        with pytest.raises(RuntimeError):
            service.refresh(refresh_setup.refresh_token)
    with Session(postgres_engine, expire_on_commit=False) as db:
        assert db.scalar(select(func.count()).select_from(RefreshToken)) == 1
        assert AuthService(db).refresh(refresh_setup.refresh_token)
