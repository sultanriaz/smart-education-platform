from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.clients.academic import AcademicSection, get_academic_client
from app.clients.facility import get_facility_client
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.security.auth import Principal, get_current_principal

ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TEACHER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
OTHER_TEACHER_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
STUDENT_ID = uuid.UUID("00000000-0000-0000-0000-000000000004")
SECTION_ID = uuid.UUID("10000000-0000-0000-0000-000000000001")
SECTION_2_ID = uuid.UUID("10000000-0000-0000-0000-000000000002")
COURSE_ID = uuid.UUID("20000000-0000-0000-0000-000000000001")
SEMESTER_ID = uuid.UUID("30000000-0000-0000-0000-000000000001")
ROOM_ID = uuid.UUID("40000000-0000-0000-0000-000000000001")
ROOM_2_ID = uuid.UUID("40000000-0000-0000-0000-000000000002")


class FakeAcademicClient:
    def get_section(self, section_id, token):
        if section_id not in {SECTION_ID, SECTION_2_ID}:
            from app.core.errors import NotFoundError

            raise NotFoundError("Academic resource not found")
        return AcademicSection(id=section_id, course_id=COURSE_ID, semester_id=SEMESTER_ID)

    def validate_teacher_assignment(self, teacher_user_id, section_id, token):
        return teacher_user_id == TEACHER_ID and section_id in {SECTION_ID, SECTION_2_ID}

    def validate_student_enrollment(self, student_user_id, section_id, token):
        return student_user_id == STUDENT_ID and section_id == SECTION_ID

    def list_student_section_ids(self, student_user_id, token):
        return [SECTION_ID] if student_user_id == STUDENT_ID else []


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def principal_state():
    return {"principal": Principal(ADMIN_ID, frozenset({"admin"}), "test-token")}


class FakeFacilityClient:
    def __init__(self):
        self.reservations = {}
        self.fail = False
        self.calls = []

    def replace_schedule(self, schedule_id, occurrences):
        from app.core.errors import ConflictError, DependencyUnavailableError
        if self.fail:
            raise DependencyUnavailableError("Facility is unavailable")
        # Simulate the Facility Service authoritative conflict check.
        for o in occurrences:
            for other_id, other_occurrences in self.reservations.items():
                if other_id == str(schedule_id):
                    continue
                for other in other_occurrences:
                    if (o["facility_id"] == other["facility_id"] and
                            o["starts_at"] < other["ends_at"] and other["starts_at"] < o["ends_at"]):
                        raise ConflictError("Classroom is occupied")
        self.reservations[str(schedule_id)] = [dict(o) for o in occurrences]
        self.calls.append((str(schedule_id), [dict(o) for o in occurrences]))


@pytest.fixture()
def fake_facility():
    return FakeFacilityClient()


@pytest.fixture()
def client(db, principal_state, fake_facility):
    def override_db():
        yield db

    def override_principal():
        return principal_state["principal"]

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_principal] = override_principal
    app.dependency_overrides[get_academic_client] = lambda: FakeAcademicClient()
    app.dependency_overrides[get_facility_client] = lambda: fake_facility
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def set_role(principal_state):
    def setter(role: str, user_id: uuid.UUID):
        principal_state["principal"] = Principal(user_id, frozenset({role}), "test-token")

    return setter


@pytest.fixture()
def schedule_payload():
    return {
        "section_id": str(SECTION_ID),
        "teacher_user_id": str(TEACHER_ID),
        "room_id": str(ROOM_ID),
        "weekday": 0,
        "starts_at": "09:00:00",
        "ends_at": "10:00:00",
        "effective_from": "2026-10-05",
        "effective_to": "2026-12-28",
        "timezone_name": "Asia/Karachi",
    }
