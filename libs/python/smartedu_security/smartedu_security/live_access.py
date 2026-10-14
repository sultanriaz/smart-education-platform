"""Fail-closed identity state validation for all distributed user API requests.

Service JWTs and public routes remain validated by existing application dependencies.
Production ALWAYS enforces the check; local tests opt in with SMARTEDU_LIVE_AUTH_CHECK=1.
"""
from __future__ import annotations
import os
import httpx
import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

class LiveAccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        production = os.getenv("ENVIRONMENT", "development").lower() in {"production", "prod", "staging"}
        enabled = production or os.getenv("SMARTEDU_LIVE_AUTH_CHECK", "0").lower() in {"1", "true", "yes"}
        if not enabled:
            return await call_next(request)
        authorization = request.headers.get("authorization", "")
        if not authorization.startswith("Bearer "):
            return await call_next(request)
        token = authorization.partition(" ")[2]
        try:
            header = jwt.get_unverified_header(token)
        except jwt.PyJWTError:
            return await call_next(request)  # Existing auth dependencies reject malformed tokens.
        if header.get("typ") != "at+jwt":
            return await call_next(request)  # Internal service JWT: existing scoped service-auth handles it.
        jwks_url = os.getenv("JWT_JWKS_URL", "")
        if not jwks_url or not jwks_url.endswith("/.well-known/jwks.json"):
            return JSONResponse({"detail": "Live identity verification is not configured"}, status_code=503)
        url = jwks_url.removesuffix("/.well-known/jwks.json") + "/api/v1/auth/access-status"
        try:
            async with httpx.AsyncClient(timeout=2.5) as client:
                response = await client.get(url, headers={"Authorization": authorization})
            if response.status_code == 401 or response.status_code == 403:
                return JSONResponse({"detail": "Access was revoked"}, status_code=401)
            if response.status_code != 200:
                return JSONResponse({"detail": "Live identity verification unavailable"}, status_code=503)
            body = response.json()
            claims = jwt.decode(token, options={"verify_signature": False, "verify_aud": False})
            if body.get("active") is not True or body.get("user_id") != claims.get("sub") or \
                sorted(body.get("roles", [])) != sorted(str(x).lower() for x in claims.get("roles", [])):
                return JSONResponse({"detail": "Access was revoked"}, status_code=401)
        except (httpx.HTTPError, ValueError, KeyError, TypeError, jwt.PyJWTError):
            return JSONResponse({"detail": "Live identity verification unavailable"}, status_code=503)
        return await call_next(request)
