from __future__ import annotations

import hmac

from fastapi import Header, HTTPException

from app.core.config import settings


def require_internal_token(x_internal_token: str | None = Header(default=None)) -> None:
    expected = settings.INTERNAL_EVENT_TOKEN.encode()
    actual = (x_internal_token or "").encode()
    if not hmac.compare_digest(expected, actual):
        raise HTTPException(status_code=401, detail="Invalid internal service token")
