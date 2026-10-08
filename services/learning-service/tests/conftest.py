from __future__ import annotations

import os
import tempfile
import uuid

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_resource_service
from app.clients.academic import AccessibleTargets
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.security.auth import Principal, get_principal
from app.services.resource_service import ResourceService
from app.storage.local import LocalStorageBackend

ADMIN_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
TEACHER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
STUDENT_ID = uuid.UUID("00000000-0000-0000-0000-000000000003")
SECTION_ID = uuid.UUID("10000000-0000-0000-0000-000000000001")
COURSE_ID = uuid.UUID("20000000-0000-0000-0000-000000000001")
OTHER_SECTION_ID = uuid.UUID("10000000-0000-0000-0000-000000000099")


class FakeAcademicClient:
    def actor_can_manage_target(self, user_id, role, target_type, target_id):
        if role == "admin":
            return True
        return user_id == TEACHER_ID and target_id in {SECTION_ID, COURSE_ID}

    def student_can_access_target(self, user_id, target_type, target_id):
        return user_id == STUDENT_ID and target_id in {SECTION_ID, COURSE_ID}

    def get_student_accessible_targets(self, user_id):
        if user_id != STUDENT_ID:
            return AccessibleTargets(set(), set())
        return AccessibleTargets({SECTION_ID}, {COURSE_ID})


@pytest.fixture()
def db():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def storage():
    with tempfile.TemporaryDirectory() as directory:
        yield LocalStorageBackend(Path(directory))


@pytest.fixture()
def academic():
    return FakeAcademicClient()


@pytest.fixture()
def client(db, storage, academic):
    current = {"principal": Principal(ADMIN_ID, frozenset({"admin"}), "test")}

    def override_db():
        yield db

    def override_principal():
        return current["principal"]

    def override_service():
        return ResourceService(db, academic, storage)

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_principal] = override_principal
    app.dependency_overrides[get_resource_service] = override_service

    # require_roles dependencies capture get_principal at creation time, so tests that
    # need those routes use a dependency override for every matching dependency by
    # injecting Authorization through monkey-free direct service tests where needed.
    with TestClient(app) as test_client:
        test_client._principal_state = current
        yield test_client
    app.dependency_overrides.clear()
