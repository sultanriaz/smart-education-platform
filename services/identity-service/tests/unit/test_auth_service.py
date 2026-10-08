import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select

from app.core.exceptions import AuthenticationError, ConflictError
from app.domain.entities.audit import SecurityAuditEvent
from app.domain.entities.refresh_token import RefreshToken
from app.domain.entities.user import User
from app.schemas.user import UserRegister
from app.security.jwt import decode_token
from app.services.auth_service import AuthService


def register_and_login(db):
    service = AuthService(db)
    user = service.register(
        UserRegister(
            email="atomic@example.edu",
            full_name="Atomic Student",
            password="StrongPass123!",  # secret-scan: test-fixture
        )
    )
    pair = service.login(user.email, "StrongPass123!")
    return service, user, pair


def fail_audit(**kwargs):
    raise RuntimeError("Audit storage failed")


def test_registration_rolls_back_if_audit_fails(db, monkeypatch):
    service = AuthService(db)
    monkeypatch.setattr(service.audit, "record", fail_audit)
    with pytest.raises(RuntimeError, match="Audit storage failed"):
        service.register(
            UserRegister(
                email="rollback@example.edu",
                full_name="Rollback Student",
                password="StrongPass123!",  # secret-scan: test-fixture
            )
        )
    assert db.scalar(select(func.count()).select_from(User)) == 0


def test_login_rolls_back_session_if_audit_fails(db, monkeypatch):
    service, user, _ = register_and_login(db)
    before = db.scalar(select(func.count()).select_from(RefreshToken))
    monkeypatch.setattr(service.audit, "record", fail_audit)
    with pytest.raises(RuntimeError):
        service.login(user.email, "StrongPass123!")
    assert db.scalar(select(func.count()).select_from(RefreshToken)) == before


def test_failed_login_is_audited(db):
    with pytest.raises(AuthenticationError):
        AuthService(db).login("missing@example.edu", "incorrect")
    event = db.scalar(select(SecurityAuditEvent))
    assert event.action == "auth.login_failed"


def test_refresh_failure_restores_original_token(db, monkeypatch):
    service, _, pair = register_and_login(db)
    original_jti = decode_token(pair.refresh_token, token_type="refresh")["jti"]
    original_audit = service.audit.record
    monkeypatch.setattr(service.audit, "record", fail_audit)
    with pytest.raises(RuntimeError):
        service.refresh(pair.refresh_token)
    old = db.scalar(select(RefreshToken).where(RefreshToken.jti == original_jti))
    assert old.revoked_at is None
    assert db.scalar(select(func.count()).select_from(RefreshToken)) == 1
    monkeypatch.setattr(service.audit, "record", original_audit)
    replacement = service.refresh(pair.refresh_token)
    assert replacement.refresh_token != pair.refresh_token


def test_refresh_replay_rejected_and_replacement_remains_usable(db):
    service, _, pair = register_and_login(db)
    replacement = service.refresh(pair.refresh_token)
    with pytest.raises(AuthenticationError):
        service.refresh(pair.refresh_token)
    assert service.refresh(replacement.refresh_token)


def test_refresh_subject_must_match_stored_owner(db):
    service, _, pair = register_and_login(db)
    jti = decode_token(pair.refresh_token, token_type="refresh")["jti"]
    stored = db.scalar(select(RefreshToken).where(RefreshToken.jti == jti))
    stored.user_id = uuid.uuid4()
    db.commit()
    with pytest.raises(AuthenticationError):
        service.refresh(pair.refresh_token)


def test_database_expired_refresh_token_rejected(db):
    service, _, pair = register_and_login(db)
    stored = db.scalar(select(RefreshToken))
    stored.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    db.commit()
    with pytest.raises(AuthenticationError):
        service.refresh(pair.refresh_token)


def test_logout_revocation_rolls_back_when_audit_fails(db, monkeypatch):
    service, _, pair = register_and_login(db)
    original_audit = service.audit.record
    monkeypatch.setattr(service.audit, "record", fail_audit)
    with pytest.raises(RuntimeError):
        service.logout(pair.refresh_token)
    monkeypatch.setattr(service.audit, "record", original_audit)
    assert service.refresh(pair.refresh_token)


def test_unique_registration_race_maps_to_conflict(db, monkeypatch):
    service, _, _ = register_and_login(db)
    monkeypatch.setattr(service.users, "get_by_email", lambda email: None)
    with pytest.raises(ConflictError):
        service.register(
            UserRegister(
                email="atomic@example.edu",
                full_name="Duplicate Student",
                password="StrongPass123!",  # secret-scan: test-fixture
            )
        )
    assert db.scalar(select(func.count()).select_from(User)) == 1
