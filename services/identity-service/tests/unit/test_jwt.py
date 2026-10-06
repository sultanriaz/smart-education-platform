import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from pydantic import ValidationError

from app.core.config import Settings, settings
from app.security.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_signing_keys,
)


def test_access_token_can_be_verified_using_only_jwks(client):
    token, _ = create_access_token(uuid.uuid4(), ["student"])
    response = client.get("/.well-known/jwks.json")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "public, max-age=300"
    jwk = response.json()["keys"][0]
    assert not {"d", "p", "q", "dp", "dq", "qi"}.intersection(jwk)
    public_key = jwt.PyJWK.from_dict(jwk).key
    claims = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_ACCESS_AUDIENCE,
    )
    assert claims["roles"] == ["student"]
    assert claims["type"] == "access"
    assert decode_token(token)["jti"] == claims["jti"]


@pytest.mark.parametrize(
    "claim,value",
    [
        ("iss", "https://untrusted.example"),
        ("aud", "another-service"),
        ("exp", 1),
        ("nbf", 9999999999),
        ("sub", "invalid-uuid"),
        ("jti", ""),
        ("type", "refresh"),
        ("roles", "admin"),
    ],
)
def test_invalid_claims_rejected(signing_key, claim, value):
    token, _ = create_access_token(uuid.uuid4(), ["student"])
    claims = jwt.decode(token, options={"verify_signature": False})
    claims[claim] = value
    forged = jwt.encode(
        claims,
        signing_key,
        algorithm="RS256",
        headers={"kid": settings.JWT_KEY_ID, "typ": "at+jwt"},
    )
    with pytest.raises(jwt.PyJWTError):
        decode_token(forged)


@pytest.mark.parametrize(
    "claim", ["exp", "iss", "aud", "sub", "iat", "nbf", "jti", "type", "roles"]
)
def test_required_claims_rejected_when_missing(signing_key, claim):
    token, _ = create_access_token(uuid.uuid4(), ["student"])
    claims = jwt.decode(token, options={"verify_signature": False})
    del claims[claim]
    token = jwt.encode(
        claims,
        signing_key,
        algorithm="RS256",
        headers={"kid": settings.JWT_KEY_ID, "typ": "at+jwt"},
    )
    with pytest.raises(jwt.PyJWTError):
        decode_token(token)


def test_refresh_token_cannot_be_used_as_access_token():
    token, _, _ = create_refresh_token(uuid.uuid4(), ["student"])
    with pytest.raises(jwt.PyJWTError):
        decode_token(token)


@pytest.mark.parametrize(
    "headers",
    [
        {"kid": "unknown", "typ": "at+jwt"},
        {"typ": "at+jwt"},
        {"kid": "identity-test-1", "typ": "JWT"},
    ],
)
def test_invalid_headers_rejected(signing_key, headers):
    token, _ = create_access_token(uuid.uuid4(), ["student"])
    claims = jwt.decode(token, options={"verify_signature": False})
    token = jwt.encode(claims, signing_key, algorithm="RS256", headers=headers)
    with pytest.raises(jwt.PyJWTError):
        decode_token(token)


def test_hmac_token_rejected():
    token = jwt.encode(
        {"sub": str(uuid.uuid4())}, "test-secret-with-at-least-32-bytes", algorithm="HS256"
    )
    with pytest.raises(jwt.PyJWTError):
        decode_token(token)


def test_token_signed_with_untrusted_key_rejected():
    from cryptography.hazmat.primitives.asymmetric import rsa

    token, _ = create_access_token(uuid.uuid4(), ["student"])
    claims = jwt.decode(token, options={"verify_signature": False})
    untrusted_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    token = jwt.encode(
        claims,
        untrusted_key,
        algorithm="RS256",
        headers={"kid": settings.JWT_KEY_ID, "typ": "at+jwt"},
    )
    with pytest.raises(jwt.InvalidSignatureError):
        decode_token(token)


def test_missing_signing_key_fails_startup_configuration(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "JWT_PRIVATE_KEY_FILE", tmp_path / "missing.pem")
    get_signing_keys.cache_clear()
    try:
        with pytest.raises(RuntimeError, match="Invalid JWT key configuration"):
            get_signing_keys()
    finally:
        get_signing_keys.cache_clear()


def test_previous_public_key_remains_available_for_rotation(
    monkeypatch, tmp_path, signing_key, client
):
    from cryptography.hazmat.primitives import serialization

    path = tmp_path / "previous.pem"
    path.write_bytes(
        signing_key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    monkeypatch.setattr(settings, "JWT_PREVIOUS_PUBLIC_KEYS", {"previous-key": path})
    get_signing_keys.cache_clear()
    try:
        now = datetime.now(UTC)
        token = jwt.encode(
            {
                "sub": str(uuid.uuid4()),
                "iss": settings.JWT_ISSUER,
                "aud": settings.JWT_ACCESS_AUDIENCE,
                "exp": now + timedelta(minutes=1),
                "iat": now,
                "nbf": now,
                "jti": uuid.uuid4().hex,
                "type": "access",
                "roles": [],
            },
            signing_key,
            algorithm="RS256",
            headers={"kid": "previous-key", "typ": "at+jwt"},
        )
        assert decode_token(token)["type"] == "access"
        assert {key["kid"] for key in client.get("/.well-known/jwks.json").json()["keys"]} == {
            settings.JWT_KEY_ID,
            "previous-key",
        }
    finally:
        get_signing_keys.cache_clear()


@pytest.mark.parametrize(
    "overrides",
    [
        {"JWT_ALGORITHM": "HS256"},
        {"ENVIRONMENT": "production", "JWT_ISSUER": "http://localhost:8001"},
        {
            "ENVIRONMENT": "production",
            "JWT_ISSUER": "https://identity.example",
            "JWT_KEY_ID": "identity-dev-1",
        },
        {"JWT_ACCESS_AUDIENCE": "same", "JWT_REFRESH_AUDIENCE": "same"},
    ],
)
def test_insecure_configuration_rejected(overrides):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **overrides)
