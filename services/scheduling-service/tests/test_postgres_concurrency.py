from __future__ import annotations

import os
import threading
import uuid
from datetime import date, time

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.clients.academic import AcademicSection
from app.core.errors import ConflictError
from app.db.base import Base
from app.schemas.schedule import ScheduleCreate
from app.security.auth import Principal
from app.services.scheduling_service import SchedulingService

POSTGRES_TEST_URL = os.getenv("POSTGRES_TEST_URL")
pytestmark = pytest.mark.skipif(
    not POSTGRES_TEST_URL,
    reason="POSTGRES_TEST_URL is required for PostgreSQL concurrency tests",
)

SECTION_ID = uuid.UUID("51000000-0000-0000-0000-000000000001")
COURSE_ID = uuid.UUID("52000000-0000-0000-0000-000000000001")
SEMESTER_ID = uuid.UUID("53000000-0000-0000-0000-000000000001")
TEACHER_ID = uuid.UUID("54000000-0000-0000-0000-000000000001")
ROOM_ID = uuid.UUID("55000000-0000-0000-0000-000000000001")
ADMIN_ID = uuid.UUID("56000000-0000-0000-0000-000000000001")


class AcademicStub:
    def get_section(self, section_id, token):
        return AcademicSection(id=section_id, course_id=COURSE_ID, semester_id=SEMESTER_ID)

    def validate_teacher_assignment(self, teacher_user_id, section_id, token):
        return True


@pytest.fixture()
def pg_session_factory():
    engine = create_engine(POSTGRES_TEST_URL, pool_pre_ping=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    yield factory
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_concurrent_conflicting_schedule_has_single_winner(pg_session_factory):
    payload = ScheduleCreate(
        section_id=SECTION_ID,
        teacher_user_id=TEACHER_ID,
        room_id=ROOM_ID,
        weekday=0,
        starts_at=time(9, 0),
        ends_at=time(10, 0),
        effective_from=date(2026, 10, 5),
        effective_to=date(2026, 12, 28),
        timezone_name="UTC",
    )
    principal = Principal(ADMIN_ID, frozenset({"admin"}), "test-token")
    barrier = threading.Barrier(2)
    outcomes: list[str] = []
    lock = threading.Lock()

    def worker():
        db = pg_session_factory()
        try:
            barrier.wait()
            try:
                SchedulingService(db, AcademicStub()).create_schedule(payload, principal)
                result = "created"
            except ConflictError:
                result = "conflict"
            with lock:
                outcomes.append(result)
        finally:
            db.close()

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert sorted(outcomes) == ["conflict", "created"]
