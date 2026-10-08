from __future__ import annotations

import json
import time
import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

from app.core.config import settings
from app.security.auth import get_current_principal, jwks_cache


@pytest.fixture()
def signing_material(monkeypatch):
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(private_key.public_key()))
    public_jwk["kid"] = "test-key"
    jwks_cache.data = {"keys": [public_jwk]}
    jwks_cache.fetched_at = time.monotonic()
    monkeypatch.setattr(settings, "JWT_ISSUER", "test-issuer")
    monkeypatch.setattr(settings, "JWT_AUDIENCE", "test-audience")
    monkeypatch.setattr(settings, "JWT_ALGORITHM", "RS256")
    monkeypatch.setattr(settings, "JWT_JWKS_CACHE_SECONDS", 3600)
    return private_key


def make_token(
    private_key,
    *,
    roles=None,
    token_type="access",
    audience="test-audience",
    issuer="test-issuer",
    expires_delta=300,
    include_kid=True,
):
    now = datetime.now(UTC)
    payload = {
        "sub": str(uuid.uuid4()),
        "roles": roles or ["student"],
        "type": token_type,
        "iss": issuer,
        "aud": audience,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "exp": now + timedelta(seconds=expires_delta),
    }
    headers = {"kid": "test-key"} if include_kid else {}
    return jwt.encode(payload, private_key, algorithm="RS256", headers=headers)


def test_valid_access_token(signing_material):
    principal = get_current_principal(make_token(signing_material, roles=["teacher"]))
    assert "teacher" in principal.roles


def test_wrong_audience_rejected(signing_material):
    with pytest.raises(HTTPException) as exc:
        get_current_principal(make_token(signing_material, audience="wrong"))
    assert exc.value.status_code == 401


def test_wrong_issuer_rejected(signing_material):
    with pytest.raises(HTTPException) as exc:
        get_current_principal(make_token(signing_material, issuer="wrong"))
    assert exc.value.status_code == 401


def test_refresh_token_rejected(signing_material):
    with pytest.raises(HTTPException) as exc:
        get_current_principal(make_token(signing_material, token_type="refresh"))
    assert exc.value.status_code == 401


def test_expired_token_rejected(signing_material):
    with pytest.raises(HTTPException) as exc:
        get_current_principal(make_token(signing_material, expires_delta=-1))
    assert exc.value.status_code == 401


def test_unknown_role_rejected(signing_material):
    with pytest.raises(HTTPException) as exc:
        get_current_principal(make_token(signing_material, roles=["unknown"]))
    assert exc.value.status_code == 403


def test_missing_kid_rejected(signing_material):
    with pytest.raises(HTTPException) as exc:
        get_current_principal(make_token(signing_material, include_kid=False))
    assert exc.value.status_code == 401
