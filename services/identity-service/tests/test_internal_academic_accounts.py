"""B04: owner lookup reveals no credentials and isolates service callers."""
from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints.internal import academic_account
from app.domain.entities.role import Role
from app.domain.entities.user import User


def test_academic_account_owner_read_includes_inactive_and_roles(db):
    role = db.query(Role).filter_by(name="student").one()
    user = User(email=f"{uuid4()}@example.edu", full_name="Test Account", password_hash="private-secret", is_active=False, auth_version=7, roles=[role])
    db.add(user)
    db.commit()
    result = academic_account(user.id, SimpleNamespace(service_name="academic-service"), db)
    assert result == {"id": str(user.id), "is_active": False, "roles": ["student"], "auth_version": 7}
    assert "password_hash" not in result and "email" not in result


def test_academic_account_denies_wrong_service_and_missing(db):
    with pytest.raises(HTTPException) as denied:
        academic_account(uuid4(), SimpleNamespace(service_name="notification-service"), db)
    assert denied.value.status_code == 403
    with pytest.raises(HTTPException) as missing:
        academic_account(uuid4(), SimpleNamespace(service_name="academic-service"), db)
    assert missing.value.status_code == 404
