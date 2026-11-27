from __future__ import annotations

import uuid
from math import isfinite
from typing import Iterable

import jwt


def decode_service_access_token(
    token: str,
    key: object,
    *,
    issuer: str,
    audience: str,
    algorithms: Iterable[str] = ("RS256",),
    leeway: int = 5,
    require_nbf: bool = False,
) -> dict:
    """Validate an access JWT with pinned asymmetric algorithm, safe typ, and strict claim checks."""
    allowed_algs = [alg for alg in algorithms if alg == "RS256"]
    if not allowed_algs:
        raise jwt.InvalidTokenError("Unsupported JWT algorithm configuration")

    header = jwt.get_unverified_header(token)
    if (
        header.get("alg") not in allowed_algs
        or header.get("typ") not in (None, "at+jwt", "JWT")
        or not isinstance(header.get("kid"), str)
        or not header["kid"]
    ):
        raise jwt.InvalidTokenError("Invalid access token header")

    required_claims = ["sub", "iss", "aud", "iat", "exp", "jti", "type", "roles"]
    if require_nbf:
        required_claims.append("nbf")

    payload = jwt.decode(
        token,
        key,
        algorithms=allowed_algs,
        issuer=issuer,
        audience=audience,
        leeway=leeway,
        options={"require": required_claims},
    )

    if payload.get("type") != "access" or not isinstance(payload.get("sub"), str):
        raise jwt.InvalidTokenError("Invalid token type or subject")
    try:
        uuid.UUID(payload["sub"])
    except ValueError as exc:
        raise jwt.InvalidTokenError("Invalid token subject") from exc

    if not isinstance(payload.get("jti"), str) or not payload["jti"]:
        raise jwt.InvalidTokenError("Invalid token identifier")

    date_fields = ("iat", "nbf", "exp") if "nbf" in payload else ("iat", "exp")
    for field in date_fields:
        value = payload[field]
        if (
            isinstance(value, bool)
            or not isinstance(value, int | float)
            or (isinstance(value, float) and not isfinite(value))
        ):
            raise jwt.InvalidTokenError("Invalid NumericDate claim")
    if payload["exp"] <= payload["iat"] or ("nbf" in payload and payload["exp"] <= payload["nbf"]):
        raise jwt.InvalidTokenError("Invalid token lifetime")

    roles_raw = payload.get("roles", [])
    if not isinstance(roles_raw, list) or any(not isinstance(r, str) or not r for r in roles_raw):
        raise jwt.InvalidTokenError("Invalid roles claim")

    perms_raw = payload.get("permissions", [])
    if not isinstance(perms_raw, list) or any(not isinstance(p, str) or not p for p in perms_raw):
        raise jwt.InvalidTokenError("Invalid permissions claim")

    return payload


decode_service_access_jwt = decode_service_access_token
