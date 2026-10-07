from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from uuid import UUID, uuid4

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_academic_client
from app.clients.academic import AcademicSection
from app.core.exceptions import ForbiddenError, NotFoundError
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app
from app.security import jwt as jwt_security


class FakeAcademic:
    def __init__(self):
        self.section = AcademicSection(
            id=uuid4(), course_id=uuid4(), semester_id=uuid4(), is_active=True
        )
        self.other_section = AcademicSection(
            id=uuid4(), course_id=uuid4(), semester_id=uuid4(), is_active=True
        )
        self.teacher_id = uuid4()
        self.students = [uuid4(), uuid4(), uuid4()]
        self.calls = 0
        self.failure = None

    def _call(self):
        self.calls += 1
        if self.failure:
            raise self.failure

    def _user(self, token):
        # Fixture tokens only. Production verification never uses this path.
        claims = jwt.decode(token, options={"verify_signature": False})
        return UUID(claims["sub"]), claims["roles"]

    def get_section(self, section_id, token):
        self._call()
        user_id, roles = self._user(token)
        if "admin" not in roles and (user_id != self.teacher_id or section_id != self.section.id):
            raise ForbiddenError()
        if section_id == self.section.id:
            return self.section
        if section_id == self.other_section.id:
            return self.other_section
        raise NotFoundError("Academic section")

    def validate_teacher_assignment(self, section_id, token):
        self.get_section(section_id, token)

    def assigned_sections(self, token):
        self._call()
        user_id, _ = self._user(token)
        return {self.section.id} if user_id == self.teacher_id else set()

    def get_section_roster(self, section_id, token):
        self.get_section(section_id, token)
        return set(self.students) if section_id == self.section.id else set()

    def validate_student_enrollment(self, section_id, student_id, token):
        if student_id not in self.get_section_roster(section_id, token):
            raise ForbiddenError("Student is not enrolled in section.")


@pytest.fixture
def academic():
    return FakeAcademic()


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
        now = int(datetime.now(UTC).timestamp())
        payload = {
            "sub": str(subject or uuid4()),
            "roles": ["admin"] if roles is None else roles,
            "iss": "http://localhost:8001",
            "aud": "smart-education-api",
            "jti": uuid4().hex,
            "type": "access",
            "iat": now,
            "nbf": now,
            "exp": now + 900,
        }
        payload.update(claims or {})
        for claim in remove:
            payload.pop(claim)
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
def client(db, token, academic):
    app = create_app()

    def test_db():
        yield db

    app.dependency_overrides[get_db] = test_db
    app.dependency_overrides[get_academic_client] = lambda: academic
    with TestClient(app) as http:
        http.headers["Authorization"] = f"Bearer {token()}"
        yield http


@pytest.fixture
def session_data(client, academic):
    response = client.post(
        "/api/v1/sessions",
        json={
            "section_id": str(academic.section.id),
            "session_date": "2026-10-07",
            "starts_at": "09:00:00",
            "ends_at": "10:00:00",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def bulk_payload(academic, statuses=None):
    statuses = statuses or ["PRESENT", "ABSENT", "LATE"]
    return {
        "records": [
            {"student_user_id": str(student), "status": status}
            for student, status in zip(academic.students, statuses, strict=True)
        ]
    }
