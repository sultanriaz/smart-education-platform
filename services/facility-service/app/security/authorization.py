from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException

from app.security.auth import Principal, get_current_principal


def require_roles(*roles: str) -> Callable:
    def dependency(principal: Principal = Depends(get_current_principal)) -> Principal:
        if not principal.has_role(*roles):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return principal

    return dependency


def require_permission(code: str):
    def dependency(principal: Principal = Depends(get_current_principal)) -> Principal:
        if not principal.has_role("admin") and not principal.has_permission(code):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return principal
    return dependency
