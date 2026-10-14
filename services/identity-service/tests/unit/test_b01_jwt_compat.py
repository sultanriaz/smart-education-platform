"""B01: pre-permission JWT compatibility must not weaken claim validation."""

import uuid

import jwt
import pytest

from app.core.config import settings
from app.security.jwt import create_access_token, decode_token


def _resign_access(signing_key, claims):
    return jwt.encode(
        claims,
        signing_key,
        algorithm="RS256",
        headers={"kid": settings.JWT_KEY_ID, "typ": "at+jwt"},
    )


def test_legacy_signed_access_without_permissions_is_readable_but_unprivileged(signing_key):
    original, _ = create_access_token(uuid.uuid4(), ["student"])
    claims = jwt.decode(original, options={"verify_signature": False})
    claims.pop("permissions")
    legacy_token = _resign_access(signing_key, claims)

    decoded = decode_token(legacy_token)
    assert decoded["type"] == "access"
    assert decoded["sub"] == claims["sub"]
    assert decoded["permissions"] == []


def test_new_access_tokens_contain_explicit_permissions():
    token, _ = create_access_token(uuid.uuid4(), ["student"], permissions=["identity.users.read"])
    assert decode_token(token)["permissions"] == ["identity.users.read"]


@pytest.mark.parametrize(
    "invalid_permissions",
    [None, "identity.users.read", {}, [123], [None], ["identity.users.read", "identity.users.read"]],
)
def test_present_but_invalid_permissions_remain_rejected(signing_key, invalid_permissions):
    original, _ = create_access_token(uuid.uuid4(), ["student"])
    claims = jwt.decode(original, options={"verify_signature": False})
    claims["permissions"] = invalid_permissions
    with pytest.raises(jwt.InvalidTokenError, match="Invalid permissions claim"):
        decode_token(_resign_access(signing_key, claims))
