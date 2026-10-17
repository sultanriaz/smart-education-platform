"""No-cache Identity revalidation for cross-service custom permissions.

A JWT signature alone cannot enforce immediate revocation. Every custom-scope
request is revalidated against the Identity database using the *same* access
JWT. Built-in role gates retain existing behavior; unavailable Identity fails
closed for custom grants. Do not include tokens in errors or logs.
"""
from __future__ import annotations

import os
from urllib.parse import urlsplit

import httpx
from fastapi import HTTPException


def live_permission(principal, code: str, jwks_url: str) -> bool:
    raw = getattr(principal, "permissions", ())
    if code not in raw:
        return False
    token = (
        getattr(principal, "raw_token", None)
        or getattr(principal, "access_token", None)
        or getattr(principal, "token", None)
    )
    if not token:
        raise HTTPException(403, "Custom permissions require live Identity verification")
    # Derive a dedicated trusted service origin, NEVER the incoming Host header.
    origin = os.getenv("IDENTITY_SERVICE_BASE_URL") or (
        (lambda u: f"{u.scheme}://{u.netloc}")(urlsplit(jwks_url))
    )
    u = urlsplit(origin)
    if u.scheme not in ("http", "https") or not u.netloc or u.username or u.password:
        raise HTTPException(503, "Identity authorization endpoint is misconfigured")
    try:
        response = httpx.get(
            origin.rstrip("/") + "/api/v1/auth/access-status",
            headers={"Authorization": "Bearer " + token, "Cache-Control": "no-store"},
            timeout=httpx.Timeout(3.0, connect=1.0),
            follow_redirects=False,
        )
    except httpx.RequestError as exc:
        raise HTTPException(503, "Identity authorization check unavailable") from exc
    if response.status_code in (401, 403):
        raise HTTPException(403, "Custom permission is revoked or stale")
    if response.status_code != 200:
        raise HTTPException(503, "Identity authorization check unavailable")
    try:
        body = response.json()
        same_user = str(body["user_id"]) == str(principal.user_id)
        active = body["active"] is True
    except (ValueError, KeyError, TypeError):
        raise HTTPException(503, "Invalid Identity authorization response") from None
    if not same_user or not active:
        raise HTTPException(403, "Custom permission is revoked or stale")
    return True
