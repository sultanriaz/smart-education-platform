from __future__ import annotations

import time
import uuid

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

from app.core.config import settings
from app.security import auth


def make_keypair():
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private, private.public_key()


def token(private, *, roles=None, token_type="access", audience=None, issuer=None):
    now = int(time.time())
    payload = {
        "sub": str(uuid.uuid4()),
        "roles": roles or ["student"],
        "type": token_type,
        "iss": issuer or settings.JWT_ISSUER,
        "aud": audience or settings.JWT_AUDIENCE,
        "iat": now,
        "jti": str(uuid.uuid4()),
        "exp": now + 300,
    }
    return jwt.encode(payload, private, algorithm="RS256", headers={"kid": "test-key"})


def test_valid_access_token(monkeypatch):
    private, public = make_keypair()
    monkeypatch.setattr(auth.jwks_cache, "get_key", lambda kid: public)
    principal = auth.verify_token(token(private, roles=["teacher"]))
    assert "teacher" in principal.roles


def test_refresh_token_rejected(monkeypatch):
    private, public = make_keypair()
    monkeypatch.setattr(auth.jwks_cache, "get_key", lambda kid: public)
    with pytest.raises(HTTPException) as exc:
        auth.verify_token(token(private, token_type="refresh"))
    assert exc.value.status_code == 401


def test_wrong_audience_rejected(monkeypatch):
    private, public = make_keypair()
    monkeypatch.setattr(auth.jwks_cache, "get_key", lambda kid: public)
    with pytest.raises(HTTPException) as exc:
        auth.verify_token(token(private, audience="wrong-audience"))
    assert exc.value.status_code == 401


def test_unknown_role_rejected(monkeypatch):
    private, public = make_keypair()
    monkeypatch.setattr(auth.jwks_cache, "get_key", lambda kid: public)
    with pytest.raises(HTTPException) as exc:
        auth.verify_token(token(private, roles=["visitor"]))
    assert exc.value.status_code == 403
