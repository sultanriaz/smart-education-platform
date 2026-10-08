import os

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Tests must not inherit legacy JWT settings or production mode from a developer's .env.
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_ALGORITHM"] = "RS256"
os.environ["JWT_ISSUER"] = "http://localhost:8001"
os.environ["JWT_KEY_ID"] = "identity-test-1"
os.environ["JWT_PREVIOUS_PUBLIC_KEYS"] = "{}"
os.environ["JWT_ACCESS_AUDIENCE"] = "smart-education-api"
os.environ["JWT_REFRESH_AUDIENCE"] = "identity-service"

from smartedu_security import LoginSecurityGuard
from smartedu_security.lockout import MemoryLockoutStore

from app.api.v1.endpoints.auth import login_guard
from app.core.config import settings  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.session import get_db
from app.domain.entities.role import Role
from app.main import app
from app.security.jwt import get_signing_keys

engine = create_engine(
    "sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
def signing_key(tmp_path_factory):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    path = tmp_path_factory.mktemp("jwt-keys") / "private.pem"
    path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    settings.JWT_PRIVATE_KEY_FILE = path
    get_signing_keys.cache_clear()
    yield key
    get_signing_keys.cache_clear()


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    session.add_all(
        [
            Role(name="student", description="Student"),
            Role(name="teacher", description="Teacher"),
            Role(name="admin", description="Admin"),
        ]
    )
    session.commit()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    guard = LoginSecurityGuard(MemoryLockoutStore())
    app.dependency_overrides[login_guard] = lambda: guard
    # The direct service URL differs from the public Gateway cookie namespace.
    from app.sprint18 import security_settings

    security_settings().refresh_cookie_path = "/api/v1/auth"
    with TestClient(app) as test_client:
        test_client.headers["Origin"] = "http://localhost:5173"
        yield test_client
    app.dependency_overrides.clear()
