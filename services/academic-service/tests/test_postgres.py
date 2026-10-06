"""PostgreSQL constraints, migrations, and races on a disposable academic_test_* database."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

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
from app.core.exceptions import ConflictError
from app.db.base import Base
from app.domain.models import Enrollment, Section, StudentAcademicProfile
from app.repositories.academic import AcademicRepository
from app.schemas.academic import SectionWrite
from app.services.academic import AcademicService
from tests.conftest import seed_academic

pytestmark = pytest.mark.postgres
ROOT = Path(__file__).resolve().parents[1]


def migration_config() -> Config:
    return Config(str(ROOT / "alembic.ini"))


@pytest.fixture(scope="module")
def postgres_engine():
    url = os.getenv("ACADEMIC_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Set ACADEMIC_TEST_DATABASE_URL for PostgreSQL integration tests.")
    parsed = make_url(url)
    if parsed.get_backend_name() != "postgresql" or not (parsed.database or "").startswith(
        "academic_test_"
    ):
        pytest.fail("Use a dedicated PostgreSQL academic_test_* database; tests clear its tables.")
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(get_settings(), "DATABASE_URL", url)
        command.upgrade(migration_config(), "head")
        engine = create_engine(
            url,
            connect_args={
                "options": "-c statement_timeout=10000 -c lock_timeout=5000",
            },
        )
        yield engine
        engine.dispose()


@pytest.fixture
def postgres_academic(postgres_engine):
    with postgres_engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(delete(table))
    with Session(postgres_engine, expire_on_commit=False) as db:
        yield seed_academic(db, capacity=1)


def synchronize_section_locks(monkeypatch):
    barrier = Barrier(2)
    original = AcademicRepository.get

    def get_together(self, model, record_id, *, lock=False):
        if model is Section and lock:
            barrier.wait(timeout=10)
        return original(self, model, record_id, lock=lock)

    monkeypatch.setattr(AcademicRepository, "get", get_together)


def test_concurrent_last_seat_has_one_winner(postgres_engine, postgres_academic, monkeypatch):
    synchronize_section_locks(monkeypatch)

    def enroll(student_id):
        with Session(postgres_engine, expire_on_commit=False) as db:
            try:
                AcademicService(db).enroll(student_id, postgres_academic.section.id)
                return "enrolled"
            except ConflictError:
                return "rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(enroll, student.id) for student in postgres_academic.students[:2]
        ]
        assert sorted(future.result(timeout=20) for future in futures) == ["enrolled", "rejected"]
    with Session(postgres_engine) as db:
        assert db.scalar(select(func.count()).select_from(Enrollment)) == 1


def test_concurrent_sections_for_same_course_have_one_winner(
    postgres_engine,
    postgres_academic,
    monkeypatch,
):
    with Session(postgres_engine, expire_on_commit=False) as db:
        second_section = AcademicService(db).create(
            Section,
            SectionWrite(
                course_id=postgres_academic.course.id,
                semester_id=postgres_academic.semester.id,
                code="B",
                capacity=10,
            ),
        )
    synchronize_section_locks(monkeypatch)

    def enroll(section_id):
        with Session(postgres_engine, expire_on_commit=False) as db:
            try:
                AcademicService(db).enroll(postgres_academic.students[0].id, section_id)
                return "enrolled"
            except ConflictError:
                return "rejected"

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(enroll, section.id)
            for section in (postgres_academic.section, second_section)
        ]
        assert sorted(future.result(timeout=20) for future in futures) == ["enrolled", "rejected"]
    with Session(postgres_engine) as db:
        assert db.scalar(select(func.count()).select_from(Enrollment)) == 1


def test_postgres_failed_commit_rolls_back(postgres_engine, postgres_academic, monkeypatch):
    with Session(postgres_engine, expire_on_commit=False) as db:

        def fail_commit():
            raise RuntimeError("simulated commit failure")

        monkeypatch.setattr(db, "commit", fail_commit)
        with pytest.raises(RuntimeError):
            AcademicService(db).enroll(
                postgres_academic.students[0].id, postgres_academic.section.id
            )
    with Session(postgres_engine) as db:
        assert db.scalar(select(func.count()).select_from(Enrollment)) == 0


def test_postgres_enforces_duplicate_and_foreign_key_constraints(
    postgres_engine, postgres_academic
):
    with Session(postgres_engine, expire_on_commit=False) as db:
        first = AcademicService(db).enroll(
            postgres_academic.students[0].id, postgres_academic.section.id
        )
        db.add(Enrollment(student_profile_id=first.student_profile_id, section_id=first.section_id))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
        db.delete(db.get(StudentAcademicProfile, first.student_profile_id))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


def test_migration_round_trip_and_no_schema_drift(postgres_engine):
    config = migration_config()
    command.downgrade(config, "base")
    assert inspect(postgres_engine).get_table_names() == ["alembic_version"]
    command.upgrade(config, "head")
    with postgres_engine.connect() as connection:
        context = MigrationContext.configure(
            connection,
            opts={
                "compare_type": True,
                "compare_server_default": True,
            },
        )
        assert compare_metadata(context, Base.metadata) == []
        assert connection.dialect.name == "postgresql"
    columns = inspect(postgres_engine).get_columns("student_academic_profiles")
    assert (
        next(column for column in columns if column["name"] == "id")["type"].__class__.__name__
        == "UUID"
    )
    foreign_keys = inspect(postgres_engine).get_foreign_keys("student_academic_profiles")
    assert not any("external_user_id" in key["constrained_columns"] for key in foreign_keys)
