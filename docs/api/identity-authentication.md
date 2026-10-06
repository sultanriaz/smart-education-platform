# Identity authentication contract, version 1

Identity owns users, credentials, roles, and refresh sessions in its PostgreSQL
database. Other services must not import its ORM models, connect to its database,
or receive its private signing key. APIs exchange identity data; JWTs carry a
signed identity assertion. Domain services own authorization for their resources.

## Endpoints and configuration

- `POST /api/v1/auth/login`: JSON email/password; returns access/refresh tokens.
- `POST /api/v1/auth/refresh`: JSON refresh_token; rotates one refresh session.
- `POST /api/v1/auth/logout`: JSON refresh_token; idempotent refresh revocation.
- `GET /api/v1/users/me`: authenticated current account status and roles.
- `GET /.well-known/jwks.json`: public RSA verification keys, without authentication.

Development issuer: `http://localhost:8001`. Configure `JWT_ISSUER` with the
stable HTTPS Identity URL for production, consistently in Identity and consumers.
The issuer is a logical identifier; the configured JWKS fetch URL may use an
internal service address such as `http://identity-service:8000/.well-known/jwks.json`.
Use HTTPS or trusted infrastructure transport in production. Never derive a
JWKS URL from an untrusted token header. This is a JWT contract, not an OIDC provider.

## Token requirements

Only RS256 is supported. Require `kid` identifying a trusted published key.

| Field | Access token | Refresh token |
| --- | --- | --- |
| Header `typ` | `at+jwt` | `rt+jwt` |
| Claim `type` | `access` | `refresh` |
| `aud` | `smart-education-api` | `identity-service` |
| `iss` | Configured Identity issuer | Same issuer |
| `sub` | Identity user UUID string | Same UUID |
| `roles` | Array of role-name strings | Array of role-name strings |
| `jti` | Unique token identifier | Identifier of a persisted refresh session |
| `iat`, `nbf`, `exp` | Required UTC NumericDate claims | Required UTC NumericDate claims |
| Default lifetime | 15 minutes | 14 days |

Audiences are configurable and must differ. The access audience covers platform
APIs; each API still enforces its own resource permissions. Domain services accept
only access tokens and never refresh tokens. Allow at most the configured small
clock tolerance (default 5 seconds). Reject missing claims, invalid signatures,
untrusted keys, wrong issuer/audience/type, malformed subjects/roles, expired
tokens, or tokens that are not yet valid. Pin algorithms to RS256.

## Consumer example

Install `PyJWT[crypto]`. Create the client once per process. Keep this code local
to the consuming service; it does not import Identity application code.

```python
import uuid

import jwt

ISSUER = "https://identity.example.edu"  # Trusted service configuration
AUDIENCE = "smart-education-api"
jwks = jwt.PyJWKClient(
    f"{ISSUER}/.well-known/jwks.json", lifespan=300, timeout=5,
)


def verify_access_token(token: str) -> dict:
    header = jwt.get_unverified_header(token)
    if (header.get("alg") != "RS256" or header.get("typ") != "at+jwt"
            or not isinstance(header.get("kid"), str)):
        raise jwt.InvalidTokenError("Invalid access token header")
    key = jwks.get_signing_key_from_jwt(token)
    claims = jwt.decode(
        token, key.key, algorithms=["RS256"], issuer=ISSUER, audience=AUDIENCE,
        leeway=5,
        options={"require": ["sub", "iss", "aud", "iat", "nbf", "exp",
                             "jti", "type", "roles"]},
    )
    if claims["type"] != "access" or not isinstance(claims["sub"], str):
        raise jwt.InvalidTokenError("Invalid access token claims")
    try:
        uuid.UUID(claims["sub"])
    except ValueError as exc:
        raise jwt.InvalidTokenError("Invalid subject") from exc
    if not isinstance(claims["jti"], str) or not claims["jti"]:
        raise jwt.InvalidTokenError("Invalid token ID")
    if not isinstance(claims["roles"], list) or any(
        not isinstance(role, str) for role in claims["roles"]
    ):
        raise jwt.InvalidTokenError("Invalid roles")
    return claims
```

Use a synchronous FastAPI dependency or a thread pool for this synchronous
verification client so network fetches do not block an async event loop. Map
invalid credentials to 401 with `WWW-Authenticate: Bearer`, authorization failures
to 403, and unavailable key discovery without a trusted cached key to 503. Fail
closed; never fall back to unverified claims. Keep network waits bounded.

## Session and authorization semantics

Refresh tokens are single use. Concurrent reuse permits at most one successful
rotation. Expired, revoked, or owner-mismatched sessions are rejected. Consumption,
replacement, and audit either commit together or roll back together. A consumed
token's replay returns 401; it does not revoke its replacement or every session
for that user. Automatic token-family compromise detection is not implemented.

Logout revokes the submitted refresh token. Already issued access tokens remain
valid until expiration in services that verify them offline. Role/status changes
can therefore take up to the configured access lifetime plus clock tolerance to
affect those services. Identity's own endpoints read current account status and
roles. Operations requiring immediate freshness must call `/api/v1/users/me`
with the bearer token and enforce current roles, with a bounded timeout and a
defined outage policy. Do not query Identity tables directly.

The platform must separately choose service-to-service machine credentials;
user access tokens do not provide a client-credentials workflow.

## Keys, deployment, and rotation

`JWT_PRIVATE_KEY_FILE` points to an unencrypted RSA private key (minimum 2048 bits)
provided through a secret mount. Identity refuses startup if key loading fails.
The local generator creates a 3072-bit key pair without overwriting existing
files. Restrict file access with deployment permissions or user-only Windows ACLs.
Never commit or bake private keys into an image. Production also requires an
HTTPS issuer and an explicitly chosen key ID rather than the development ID.

`JWT_PREVIOUS_PUBLIC_KEYS` is a JSON object mapping previous key IDs to mounted
public PEM paths. JWKS publishes the active key and those previous public keys;
Identity can verify tokens signed by either. Key material is loaded once per
process, so restart Identity after updating key configuration.

For a single-instance development deployment, change the active key/kid and
retain the old public key. Production rollout must first prepublish the new public
key on all instances using `JWT_PREVIOUS_PUBLIC_KEYS`, wait at least the five-minute
JWKS cache lifetime, then switch signing to the new key and retain the old public
key on all instances. Keep old public keys until the last old refresh token can
expire (configured refresh lifetime plus clock tolerance). Remove retired keys
and restart only after that interval. All instances must expose the same trusted
verification set throughout rollout. Removing a key immediately invalidates its
tokens once consumers refresh their caches.

Implementation references: [PyJWT verification and JWKS usage](https://pyjwt.readthedocs.io/en/stable/usage.html),
[PostgreSQL concurrent UPDATE behavior](https://www.postgresql.org/docs/current/transaction-iso.html).
