from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.exceptions import PyJWKClientConnectionError

from app.security.jwt import verify_access_token


def test_valid_access_token(token):
    user_id = uuid4()
    principal = verify_access_token(token(subject=user_id, roles=["teacher"]))
    assert principal.user_id == user_id
    assert principal.roles == frozenset({"teacher"})
    assert not principal.is_admin


@pytest.mark.parametrize(
    "claims",
    [
        {"iss": "https://untrusted.test"},
        {"aud": "identity-service"},
        {"type": "refresh"},
        {"sub": "invalid-uuid"},
        {"sub": 42},
        {"roles": "admin"},
        {"roles": [42]},
        {"roles": [""]},
        {"jti": ""},
        {"exp": 1},
        {"iat": "tomorrow"},
        {"exp": "9999999999"},
        {"nbf": True},
        {"iat": float("nan")},
        {"exp": float("inf")},
        {"nbf": int(datetime.now(UTC).timestamp()) + 100},
    ],
)
def test_reject_invalid_claims(client, token, claims):
    response = client.get(
        "/api/v1/departments",
        headers={
            "Authorization": f"Bearer {token(claims=claims)}",
        },
    )
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "claim", ["sub", "iss", "aud", "iat", "nbf", "exp", "jti", "type", "roles"]
)
def test_reject_missing_required_claim(client, token, claim):
    response = client.get(
        "/api/v1/departments",
        headers={
            "Authorization": f"Bearer {token(remove=[claim])}",
        },
    )
    assert response.status_code == 401


@pytest.mark.parametrize("headers", [{"typ": "rt+jwt"}, {"kid": "unknown"}, {"kid": ""}])
def test_reject_invalid_headers(client, token, headers):
    assert (
        client.get(
            "/api/v1/departments",
            headers={
                "Authorization": f"Bearer {token(headers=headers)}",
            },
        ).status_code
        == 401
    )


def test_reject_hmac_algorithm(client):
    forged = jwt.encode(
        {"roles": ["admin"]},
        "attacker-secret-that-is-at-least-32-bytes",
        algorithm="HS256",
        headers={
            "typ": "at+jwt",
            "kid": "test-key",
        },
    )
    assert (
        client.get(
            "/api/v1/departments",
            headers={
                "Authorization": f"Bearer {forged}",
            },
        ).status_code
        == 401
    )


def test_reject_wrong_signature(client, token):
    payload = jwt.decode(token(), options={"verify_signature": False})
    forged = jwt.encode(
        payload,
        rsa.generate_private_key(public_exponent=65537, key_size=2048),
        algorithm="RS256",
        headers={"typ": "at+jwt", "kid": "test-key"},
    )
    assert (
        client.get(
            "/api/v1/departments",
            headers={
                "Authorization": f"Bearer {forged}",
            },
        ).status_code
        == 401
    )


def test_jwks_outage_fails_closed(client, token, jwks_client, monkeypatch):
    def unavailable(*args, **kwargs):
        raise PyJWKClientConnectionError("unavailable")

    monkeypatch.setattr(jwks_client, "fetch_data", unavailable)
    assert client.get("/api/v1/departments").status_code == 503


def test_missing_or_malformed_bearer_token(client):
    client.headers.pop("Authorization")
    assert client.get("/api/v1/departments").status_code == 401
    assert (
        client.get(
            "/api/v1/departments",
            headers={
                "Authorization": "Bearer malformed",
            },
        ).status_code
        == 401
    )


@pytest.mark.parametrize("roles", [[], ["student"], ["Admin"]])
def test_reject_non_staff_roles(client, token, roles):
    assert (
        client.get(
            "/api/v1/departments",
            headers={
                "Authorization": f"Bearer {token(roles=roles)}",
            },
        ).status_code
        == 403
    )
