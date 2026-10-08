from __future__ import annotations

import os
import uuid

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_dispatcher, get_target_resolver
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.security.auth import Principal, get_current_principal
from app.services.target_resolver import ResolvedRecipient, TargetResolver


class TestDispatcher:
    def __init__(self):
        self.events = []
        self.deliveries = []

    def process_inbox_event(self, inbox_event_id):
        self.events.append(inbox_event_id)

    def deliver_attempt(self, attempt_id):
        self.deliveries.append(attempt_id)


class FakeResolver(TargetResolver):
    def __init__(self):
        self.role_users = []
        self.section_users = []

    def resolve(self, target, forwarded_token=None):
        if target.kind == "DIRECT":
            return [
                ResolvedRecipient(item.user_id, str(item.email) if item.email else None)
                for item in (target.recipients or [])
            ]
        if target.kind == "ROLE":
            return list(self.role_users)
        return list(self.section_users)

    def resolve_event_targets(self, targets, payload):
        values = targets.get("user_ids", [])
        if not values and payload.get("student_user_id"):
            values = [payload["student_user_id"]]
        return [ResolvedRecipient(uuid.UUID(str(value))) for value in values]


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
def identities():
    return {
        "admin": uuid.uuid4(),
        "teacher": uuid.uuid4(),
        "student": uuid.uuid4(),
        "other": uuid.uuid4(),
    }


@pytest.fixture()
def fake_resolver():
    return FakeResolver()


@pytest.fixture()
def dispatcher():
    return TestDispatcher()


@pytest.fixture()
def client(db, identities, fake_resolver, dispatcher):
    current = {
        "principal": Principal(identities["student"], frozenset({"student"}), "student-token")
    }

    def override_db():
        yield db

    def override_principal():
        return current["principal"]

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_principal] = override_principal
    app.dependency_overrides[get_target_resolver] = lambda: fake_resolver
    app.dependency_overrides[get_dispatcher] = lambda: dispatcher

    with TestClient(app) as test_client:
        test_client.set_principal = lambda user_id, roles: current.update(
            {"principal": Principal(user_id, frozenset(roles), "test-token")}
        )
        yield test_client

    app.dependency_overrides.clear()
