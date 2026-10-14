from __future__ import annotations

import os

# TestClient uses the host "testserver"; production host validation stays enabled.
# Set the test environment before the application and security settings are imported.
os.environ["ENVIRONMENT"] = "test"

from collections.abc import Iterator
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.api.dependencies import get_identity_accounts
from app.db.base import Base
from app.db.session import get_db
from app.domain.models import (
    AcademicYear,
    Course,
    Department,
    Program,
    Section,
    Semester,
    StudentAcademicProfile,
    TeacherAcademicProfile,
)
from app.main import create_app
from app.schemas.academic import (
    AcademicYearWrite,
    CourseWrite,
    DepartmentWrite,
    ProgramWrite,
    SectionWrite,
    SemesterWrite,
    StudentProfileWrite,
    TeacherProfileWrite,
)
from app.security import jwt as jwt_security
from app.services.academic import AcademicService


@pytest.fixture
def db() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
    )

    @event.listens_for(engine, "connect")
    def foreign_keys(connection, record):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as session:
        yield session
    engine.dispose()


@pytest.fixture(scope="session")
def signing_key():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def jwks_client(signing_key, monkeypatch):
    key = jwt.algorithms.RSAAlgorithm.to_jwk(signing_key.public_key(), as_dict=True)
    key.update(kid="test-key", alg="RS256", use="sig")
    client = jwt.PyJWKClient("https://identity.example.test/.well-known/jwks.json")
    monkeypatch.setattr(client, "fetch_data", lambda: {"keys": [key]})
    monkeypatch.setattr(jwt_security, "get_jwks_client", lambda: client)
    return client


@pytest.fixture
def token(signing_key, jwks_client):
    def make_token(*, roles=None, subject=None, claims=None, headers=None, remove=()):
        settings = get_settings()
        now = int(datetime.now(UTC).timestamp())
        payload = {
            "sub": str(subject or uuid4()),
            "roles": ["admin"] if roles is None else roles,
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_ACCESS_AUDIENCE,
            "jti": uuid4().hex,
            "type": "access",
            "iat": now,
            "nbf": now,
            "exp": now + 900,
        }
        payload.update(claims or {})
        for field in remove:
            payload.pop(field)
        return jwt.encode(
            payload,
            signing_key,
            algorithm="RS256",
            headers={
                "typ": "at+jwt",
                "kid": "test-key",
                **(headers or {}),
            },
        )

    return make_token


@pytest.fixture
def client(db, token):
    app = create_app()

    def test_db():
        yield db

    app.dependency_overrides[get_db] = test_db
    # The existing API tests create arbitrary external UUIDs. Keep their
    # academic-only scenarios isolated from Identity; B04-specific tests use
    # a signed HTTP transport and explicit owner-state fixtures below.
    app.dependency_overrides[get_identity_accounts] = lambda: type(
        "EligibleAccounts", (), {"require_eligible": lambda self, user_id, role: None}
    )()
    with TestClient(app) as http:
        http.headers["Authorization"] = f"Bearer {token()}"
        yield http
    app.dependency_overrides.clear()


def seed_academic(db: Session, *, capacity: int = 2) -> SimpleNamespace:
    service = AcademicService(db)
    department = service.create(Department, DepartmentWrite(code="CS", name="Computer Science"))
    program = service.create(
        Program,
        ProgramWrite(
            department_id=department.id,
            code="BSCS",
            name="BS Computer Science",
            duration_semesters=8,
        ),
    )
    year = service.create(
        AcademicYear,
        AcademicYearWrite(
            code="2026-27",
            name="2026/2027",
            starts_on="2026-08-01",
            ends_on="2027-07-31",
        ),
    )
    semester = service.create(
        Semester,
        SemesterWrite(
            academic_year_id=year.id,
            number=1,
            name="Fall 2026",
            starts_on="2026-08-15",
            ends_on="2026-12-31",
        ),
    )
    course = service.create(
        Course,
        CourseWrite(
            program_id=program.id,
            code="CS101",
            title="Computing",
            credits=3,
            semester_number=1,
        ),
    )
    section = service.create(
        Section,
        SectionWrite(
            course_id=course.id,
            semester_id=semester.id,
            code="A",
            capacity=capacity,
        ),
    )
    students = [
        service.create(
            StudentAcademicProfile,
            StudentProfileWrite(
                external_user_id=uuid4(),
                student_number=f"2026-{index:03d}",
                program_id=program.id,
                admission_year_id=year.id,
                current_semester=1,
            ),
        )
        for index in range(1, 4)
    ]
    teacher = service.create(
        TeacherAcademicProfile,
        TeacherProfileWrite(
            external_user_id=uuid4(),
            employee_number="T-001",
            department_id=department.id,
            designation="Lecturer",
        ),
    )
    return SimpleNamespace(
        department=department,
        program=program,
        year=year,
        semester=semester,
        course=course,
        section=section,
        students=students,
        teacher=teacher,
    )


@pytest.fixture
def academic(db):
    return seed_academic(db)
