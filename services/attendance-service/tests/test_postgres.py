"""All PostgreSQL tests use a dedicated disposable attendance_test_* database."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import Barrier, Event, local
from uuid import UUID, uuid4

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, delete, func, inspect, select
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import ConflictError, ForbiddenError
from app.db.base import Base
from app.domain.models import AttendanceRecord, AttendanceSession, OutboxEvent
from app.repositories.attendance import AttendanceRepository
from app.repositories.outbox import OutboxRepository
from app.schemas.attendance import BulkMark, SessionCreate
from app.security.jwt import Principal
from app.services.attendance import AttendanceService
from tests.conftest import bulk_payload

pytestmark = pytest.mark.postgres
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def postgres_engine():
    url = os.getenv("ATTENDANCE_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set ATTENDANCE_TEST_DATABASE_URL for actual PostgreSQL tests.")
    parsed = make_url(url)
    if parsed.get_backend_name() != "postgresql" or not (parsed.database or "").startswith(
        "attendance_test_"
    ):
        pytest.fail(
            "Use a disposable PostgreSQL attendance_test_* database; tests clear its tables."
        )
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(get_settings(), "DATABASE_URL", url)
        command.upgrade(Config(str(ROOT / "alembic.ini")), "head")
        engine = create_engine(
            url, connect_args={"options": "-c statement_timeout=10000 -c lock_timeout=5000"}
        )
        yield engine
        engine.dispose()


@pytest.fixture
def postgres_setup(postgres_engine, academic, token):
    with postgres_engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(delete(table))
    actor = Principal(uuid4(), frozenset({"admin"}), token())
    with Session(postgres_engine, expire_on_commit=False) as db:
        session = AttendanceService(db, academic, get_settings()).create_session(
            actor,
            SessionCreate(
                section_id=academic.section.id,
                session_date="2026-10-07",
            ),
        )
    return actor, session


@pytest.mark.parametrize("scheduled", [False, True])
def test_concurrent_session_creation_has_one_winner(
    postgres_engine, postgres_setup, academic, monkeypatch, scheduled
):
    actor, _ = postgres_setup
    barrier = Barrier(2)
    original = AttendanceRepository.add

    def synchronized_add(self, row):
        if isinstance(row, AttendanceSession):
            barrier.wait(timeout=10)
        return original(self, row)

    monkeypatch.setattr(AttendanceRepository, "add", synchronized_add)
    payload = SessionCreate(
        section_id=academic.section.id,
        session_date="2026-10-08",
        schedule_occurrence_id=uuid4() if scheduled else None,
    )

    def create():
        with Session(postgres_engine, expire_on_commit=False) as db:
            try:
                AttendanceService(db, academic, get_settings()).create_session(actor, payload)
                return "created"
            except ConflictError:
                return "rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(create) for _ in range(2)]
        assert sorted(future.result(timeout=20) for future in futures) == ["created", "rejected"]
    with Session(postgres_engine) as db:
        assert db.scalar(select(func.count()).select_from(AttendanceSession)) == 2
        assert db.scalar(select(func.count()).select_from(OutboxEvent)) == 2


@pytest.mark.parametrize("same_payload", [True, False])
def test_concurrent_record_writes_are_deterministic(
    postgres_engine, postgres_setup, academic, monkeypatch, same_payload
):
    actor, session = postgres_setup
    barrier = Barrier(2)
    original = AttendanceRepository.get_session

    def synchronized_get(self, session_id, *, lock=False):
        if lock:
            barrier.wait(timeout=10)
        return original(self, session_id, lock=lock)

    monkeypatch.setattr(AttendanceRepository, "get_session", synchronized_get)

    def mark(status):
        payload = BulkMark(records=[{"student_user_id": academic.students[0], "status": status}])
        with Session(postgres_engine, expire_on_commit=False) as db:
            try:
                AttendanceService(db, academic, get_settings()).bulk_mark(
                    actor, session.id, payload
                )
                return "marked"
            except ConflictError:
                return "rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(mark, "PRESENT"),
            executor.submit(mark, "PRESENT" if same_payload else "ABSENT"),
        ]
        outcomes = sorted(future.result(timeout=20) for future in futures)
        assert outcomes == (["marked", "marked"] if same_payload else ["marked", "rejected"])
    with Session(postgres_engine) as db:
        assert db.scalar(select(func.count()).select_from(AttendanceRecord)) == 1
        assert db.scalar(select(func.count()).select_from(OutboxEvent)) == 2


def test_postgres_invalid_bulk_roster_commits_zero(postgres_engine, postgres_setup, academic):
    actor, session = postgres_setup
    payload = bulk_payload(academic)
    payload["records"][-1]["student_user_id"] = str(uuid4())
    with Session(postgres_engine, expire_on_commit=False) as db:
        with pytest.raises(ForbiddenError):
            AttendanceService(db, academic, get_settings()).bulk_mark(
                actor, session.id, BulkMark(**payload)
            )
    with Session(postgres_engine) as db:
        assert db.scalar(select(func.count()).select_from(AttendanceRecord)) == 0
        assert db.scalar(select(func.count()).select_from(OutboxEvent)) == 1


def test_postgres_mid_bulk_storage_failure_rolls_back_everything(
    postgres_engine, postgres_setup, academic, monkeypatch
):
    actor, session = postgres_setup
    original = AttendanceRepository.add
    count = 0

    def fail_second_record(self, row):
        nonlocal count
        if isinstance(row, AttendanceRecord):
            count += 1
            if count == 2:
                raise IntegrityError("INSERT", {}, Exception("simulated storage failure"))
        return original(self, row)

    monkeypatch.setattr(AttendanceRepository, "add", fail_second_record)
    with Session(postgres_engine, expire_on_commit=False) as db:
        with pytest.raises(ConflictError):
            AttendanceService(db, academic, get_settings()).bulk_mark(
                actor, session.id, BulkMark(**bulk_payload(academic))
            )
    with Session(postgres_engine) as db:
        assert db.scalar(select(func.count()).select_from(AttendanceRecord)) == 0
        assert db.scalar(select(func.count()).select_from(OutboxEvent)) == 1


def test_finalization_wins_against_waiting_normal_writer(
    postgres_engine, postgres_setup, academic, monkeypatch
):
    actor, session = postgres_setup
    payload = BulkMark(**bulk_payload(academic))
    with Session(postgres_engine, expire_on_commit=False) as db:
        AttendanceService(db, academic, get_settings()).bulk_mark(actor, session.id, payload)
    writer_waiting, finalized = Event(), Event()
    context = local()
    original = AttendanceRepository.get_session

    def lock_after_finalization(self, session_id, *, lock=False):
        if lock and getattr(context, "writer", False):
            writer_waiting.set()
            assert finalized.wait(timeout=10)
        return original(self, session_id, lock=lock)

    monkeypatch.setattr(AttendanceRepository, "get_session", lock_after_finalization)

    def mark():
        context.writer = True
        with Session(postgres_engine, expire_on_commit=False) as db:
            with pytest.raises(ConflictError, match="OPEN"):
                AttendanceService(db, academic, get_settings()).bulk_mark(
                    actor, session.id, payload
                )

    def finalize():
        assert writer_waiting.wait(timeout=10)
        with Session(postgres_engine, expire_on_commit=False) as db:
            AttendanceService(db, academic, get_settings()).finalize(actor, session.id)
        finalized.set()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(mark), executor.submit(finalize)]
        for future in futures:
            future.result(timeout=20)
    with Session(postgres_engine) as db:
        assert db.get(AttendanceSession, session.id).status == "FINALIZED"
        assert db.scalar(select(func.count()).select_from(AttendanceRecord)) == 3


def test_database_rejects_duplicate_record_and_invalid_status(
    postgres_engine, postgres_setup, academic
):
    actor, session = postgres_setup
    with Session(postgres_engine, expire_on_commit=False) as db:
        record = AttendanceService(db, academic, get_settings()).bulk_mark(
            actor,
            session.id,
            BulkMark(records=[{"student_user_id": academic.students[0], "status": "PRESENT"}]),
        )[0]
        db.add(
            AttendanceRecord(
                attendance_session_id=session.id,
                student_user_id=record.student_user_id,
                status="PRESENT",
                marked_by_user_id=actor.user_id,
                marked_at=datetime.now(UTC),
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
        db.add(
            AttendanceRecord(
                attendance_session_id=session.id,
                student_user_id=uuid4(),
                status="INVALID",
                marked_by_user_id=actor.user_id,
                marked_at=datetime.now(UTC),
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


def test_outbox_skip_locked_leases_retry_and_acknowledgment(postgres_engine, postgres_setup):
    now = datetime.now(UTC) + timedelta(seconds=1)
    with (
        Session(postgres_engine, expire_on_commit=False) as first,
        Session(postgres_engine) as second,
    ):
        rows = OutboxRepository(first).claim(
            "worker-1", now=now, lease_until=now + timedelta(minutes=1), limit=10
        )
        assert len(rows) == 1
        assert (
            OutboxRepository(second).claim(
                "worker-2", now=now, lease_until=now + timedelta(minutes=1), limit=10
            )
            == []
        )
        first.commit()
        assert not OutboxRepository(second).acknowledge(rows[0].id, "worker-2", now=now)
        assert OutboxRepository(first).release(
            rows[0].id, "worker-1", now=now, retry_at=now + timedelta(seconds=1), error="retry"
        )
        first.commit()
        retry_time = now + timedelta(seconds=2)
        rows = OutboxRepository(second).claim(
            "worker-2", now=retry_time, lease_until=retry_time + timedelta(minutes=1), limit=10
        )
        assert len(rows) == 1 and rows[0].attempts == 2
        second.commit()
        assert OutboxRepository(second).acknowledge(rows[0].id, "worker-2", now=retry_time)
        second.commit()
        assert rows[0].published_at is not None


def test_migration_round_trip_and_no_schema_drift(postgres_engine):
    config = Config(str(ROOT / "alembic.ini"))
    command.downgrade(config, "base")
    assert inspect(postgres_engine).get_table_names() == ["alembic_version"]
    command.upgrade(config, "head")
    command.check(config)
    with postgres_engine.connect() as connection:
        context = MigrationContext.configure(
            connection, opts={"compare_type": True, "compare_server_default": True}
        )
        assert compare_metadata(context, Base.metadata) == []
    for table in Base.metadata.sorted_tables:
        for fk in inspect(postgres_engine).get_foreign_keys(table.name):
            assert fk["referred_table"] in Base.metadata.tables
    external = {
        "section_id",
        "course_id",
        "semester_id",
        "created_by_user_id",
        "schedule_occurrence_id",
    }
    assert not any(
        external.intersection(fk["constrained_columns"])
        for fk in inspect(postgres_engine).get_foreign_keys("attendance_sessions")
    )
    assert (
        inspect(postgres_engine).get_columns("attendance_sessions")[0]["type"].python_type is UUID
    )
