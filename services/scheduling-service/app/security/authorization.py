from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException

from app.security.auth import Principal, get_current_principal


def require_roles(*allowed: str) -> Callable:
    allowed_set = {value.lower() for value in allowed}

    def dependency(principal: Principal = Depends(get_current_principal)) -> Principal:
        if allowed_set.isdisjoint(principal.roles):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return principal

    return dependency
