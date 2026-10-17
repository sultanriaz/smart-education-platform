from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dataclass_field
from functools import lru_cache
from math import isfinite
from uuid import UUID

import jwt
from jwt import PyJWKClient
from jwt.exceptions import PyJWKClientConnectionError

from app.core.config import get_settings


class KeyDiscoveryUnavailable(Exception):
    pass


@dataclass(frozen=True)
class Principal:
    user_id: UUID
    roles: frozenset[str]
    access_token: str = dataclass_field(default="", repr=False)
    permissions: frozenset[str] = dataclass_field(default_factory=frozenset)

    @property
    def is_admin(self) -> bool:
        return "admin" in self.roles or "attendance.records.manage" in self.permissions


@lru_cache
def get_jwks_client() -> PyJWKClient:
    settings = get_settings()
    return PyJWKClient(
        settings.JWT_JWKS_URL,
        lifespan=settings.JWT_JWKS_CACHE_SECONDS,
        timeout=settings.JWT_JWKS_TIMEOUT_SECONDS,
        # Cache the JWKS set, not individual keys indefinitely: retired keys must expire.
        cache_keys=False,
    )


def verify_access_token(token: str) -> Principal:
    settings = get_settings()
    header = jwt.get_unverified_header(token)
    if (
        header.get("alg") != "RS256"
        or header.get("typ") != "at+jwt"
        or not isinstance(header.get("kid"), str)
        or not header["kid"]
    ):
        raise jwt.InvalidTokenError("Invalid access token header.")
    try:
        key = get_jwks_client().get_signing_key_from_jwt(token)
    except PyJWKClientConnectionError as exc:
        raise KeyDiscoveryUnavailable from exc
    try:
        claims = jwt.decode(
            token,
            key.key,
            algorithms=["RS256"],
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_ACCESS_AUDIENCE,
            leeway=settings.JWT_LEEWAY_SECONDS,
            options={"require": ["sub", "iss", "aud", "iat", "nbf", "exp", "jti", "type", "roles"]},
        )
    except (ValueError, TypeError, OverflowError) as exc:
        raise jwt.InvalidTokenError("Malformed access token claims.") from exc
    if claims["type"] != "access" or not isinstance(claims["sub"], str):
        raise jwt.InvalidTokenError("Invalid token type or subject.")
    try:
        subject = UUID(claims["sub"])
    except ValueError as exc:
        raise jwt.InvalidTokenError("Invalid subject.") from exc
    if not isinstance(claims["jti"], str) or not claims["jti"]:
        raise jwt.InvalidTokenError("Invalid token identifier.")
    if not isinstance(claims["roles"], list) or any(
        not isinstance(role, str) or not role for role in claims["roles"]
    ):
        raise jwt.InvalidTokenError("Invalid roles.")
    for field in ("iat", "nbf", "exp"):
        if (
            isinstance(claims[field], bool)
            or not isinstance(claims[field], int | float)
            or (isinstance(claims[field], float) and not isfinite(claims[field]))
        ):
            raise jwt.InvalidTokenError("Invalid NumericDate claim.")
    if claims["exp"] <= claims["iat"] or claims["exp"] <= claims["nbf"]:
        raise jwt.InvalidTokenError("Invalid token lifetime.")
    raw = claims.get("permissions", [])
    if not isinstance(raw, list) or any(not isinstance(p, str) or not p for p in raw):
        raise jwt.InvalidTokenError("Invalid permissions claim")
    return Principal(subject, frozenset(claims["roles"]), token, frozenset(raw))
