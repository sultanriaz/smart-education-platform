import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Literal

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.core.config import settings

TokenType = Literal["access", "refresh"]


@dataclass(frozen=True)
class SigningKeys:
    private_key: rsa.RSAPrivateKey
    public_keys: dict[str, rsa.RSAPublicKey]


@lru_cache
def get_signing_keys() -> SigningKeys:
    try:
        private_key = serialization.load_pem_private_key(
            settings.JWT_PRIVATE_KEY_FILE.read_bytes(),
            password=None,
        )
        if not isinstance(private_key, rsa.RSAPrivateKey) or private_key.key_size < 2048:
            raise ValueError("The signing key must be an RSA private key of at least 2048 bits.")
        public_keys = {settings.JWT_KEY_ID: private_key.public_key()}
        for kid, path in settings.JWT_PREVIOUS_PUBLIC_KEYS.items():
            key = serialization.load_pem_public_key(path.read_bytes())
            if not isinstance(key, rsa.RSAPublicKey) or key.key_size < 2048:
                raise ValueError("Previous keys must be RSA public keys of at least 2048 bits.")
            public_keys[kid] = key
    except (OSError, ValueError, TypeError) as exc:
        raise RuntimeError(
            "Invalid JWT key configuration. Mount an RSA private key or run "
            "python -m app.scripts.generate_jwt_keys for local development."
        ) from exc
    return SigningKeys(private_key=private_key, public_keys=public_keys)


def public_jwks() -> dict:
    keys = []
    for kid, public_key in get_signing_keys().public_keys.items():
        jwk = jwt.algorithms.RSAAlgorithm.to_jwk(public_key, as_dict=True)
        jwk.update(kid=kid, use="sig", alg="RS256")
        keys.append(jwk)
    return {"keys": keys}


def _create_token(
    user_id: uuid.UUID,
    roles: list[str],
    token_type: TokenType,
    duration: timedelta,
    auth_version: int = 0,
    permissions: list[str] | None = None,
) -> tuple[str, str, datetime]:
    now = datetime.now(UTC)
    expires_at = now + duration
    jti = uuid.uuid4().hex
    audience = (
        settings.JWT_ACCESS_AUDIENCE if token_type == "access" else settings.JWT_REFRESH_AUDIENCE
    )
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "roles": roles,
        "auth_version": auth_version,
        "jti": jti,
        "iss": settings.JWT_ISSUER,
        "aud": audience,
        "iat": now,
        "nbf": now,
        "exp": expires_at,
    }
    if token_type == "access":
        payload["permissions"] = sorted(set(permissions or []))
    token = jwt.encode(
        payload,
        get_signing_keys().private_key,
        algorithm="RS256",
        headers={
            "kid": settings.JWT_KEY_ID,
            "typ": "at+jwt" if token_type == "access" else "rt+jwt",
        },
    )
    return token, jti, expires_at


def create_access_token(
    user_id: uuid.UUID, roles: list[str], auth_version: int = 0,
    permissions: list[str] | None = None,
) -> tuple[str, datetime]:
    token, _, expires_at = _create_token(
        user_id,
        roles,
        "access",
        timedelta(minutes=settings.ACCESS_TOKEN_MINUTES),
        auth_version,
        permissions,
    )
    return token, expires_at


def create_refresh_token(user_id: uuid.UUID, roles: list[str], auth_version: int = 0) -> tuple[str, str, datetime]:
    return _create_token(user_id, roles, "refresh", timedelta(days=settings.REFRESH_TOKEN_DAYS), auth_version)


def decode_token(token: str, *, token_type: TokenType = "access") -> dict:
    header = jwt.get_unverified_header(token)
    expected_typ = "at+jwt" if token_type == "access" else "rt+jwt"
    if header.get("alg") != "RS256" or header.get("typ") != expected_typ:
        raise jwt.InvalidTokenError("Invalid token algorithm or type.")
    kid = header.get("kid")
    if not isinstance(kid, str):
        raise jwt.InvalidTokenError("Missing key ID.")
    key = get_signing_keys().public_keys.get(kid)
    if key is None:
        raise jwt.InvalidTokenError("Unknown key ID.")
    audience = (
        settings.JWT_ACCESS_AUDIENCE if token_type == "access" else settings.JWT_REFRESH_AUDIENCE
    )
    payload = jwt.decode(
        token,
        key,
        algorithms=["RS256"],
        issuer=settings.JWT_ISSUER,
        audience=audience,
        leeway=settings.JWT_LEEWAY_SECONDS,
        options={"require": ["sub", "iss", "aud", "iat", "nbf", "exp", "jti", "type", "roles"]},
    )
    if token_type == "access":
        # Tokens issued before B01 have no permissions claim. Accept their
        # cryptographic identity, but grant no scoped permissions by default.
        # Identity's request guard still checks the live role grants, so an
        # older token cannot bypass permission changes or revocations.
        if "permissions" not in payload:
            payload["permissions"] = []
        elif (
            not isinstance(payload["permissions"], list)
            or any(not isinstance(code, str) for code in payload["permissions"])
            or len(payload["permissions"]) != len(set(payload["permissions"]))
        ):
            raise jwt.InvalidTokenError("Invalid permissions claim.")
    if payload["type"] != token_type or not isinstance(payload["sub"], str):
        raise jwt.InvalidTokenError("Invalid token type or subject.")
    try:
        uuid.UUID(payload["sub"])
    except ValueError as exc:
        raise jwt.InvalidTokenError("Invalid subject.") from exc
    if not isinstance(payload["jti"], str) or not payload["jti"]:
        raise jwt.InvalidTokenError("Invalid token ID.")
    if not isinstance(payload["roles"], list) or any(
        not isinstance(role, str) for role in payload["roles"]
    ):
        raise jwt.InvalidTokenError("Invalid roles.")
    return payload
