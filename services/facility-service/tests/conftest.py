from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime, timedelta

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["MIN_BOOKING_NOTICE_MINUTES"] = "0"
os.environ["CANCELLATION_CUTOFF_MINUTES"] = "0"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.security.auth import Principal, get_current_principal

engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

ADMIN_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
TEACHER_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")
STUDENT_ID = uuid.UUID("33333333-3333-3333-3333-333333333333")
OTHER_ID = uuid.UUID("44444444-4444-4444-4444-444444444444")


def principal(user_id: uuid.UUID, *roles: str):
    return Principal(user_id=user_id, roles=frozenset(roles), raw_token="test")


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def as_principal():
    def _set(value: Principal):
        app.dependency_overrides[get_current_principal] = lambda: value

    yield _set
    app.dependency_overrides.pop(get_current_principal, None)


@pytest.fixture()
def client(db):
    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def admin():
    return principal(ADMIN_ID, "admin")


@pytest.fixture()
def teacher():
    return principal(TEACHER_ID, "teacher")


@pytest.fixture()
def student():
    return principal(STUDENT_ID, "student")


@pytest.fixture()
def other_student():
    return principal(OTHER_ID, "student")


@pytest.fixture()
def future_window():
    start = datetime.now(UTC) + timedelta(days=2)
    return start, start + timedelta(hours=2)
