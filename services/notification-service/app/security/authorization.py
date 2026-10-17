from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, HTTPException

from app.security.auth import Principal, get_current_principal
from app.core.config import settings
from smartedu_security.live_permissions import live_permission


def require_roles(*roles: str) -> Callable:
    wanted = {r.lower() for r in roles}

    def dependency(principal: Principal = Depends(get_current_principal)) -> Principal:
        if wanted.isdisjoint(principal.roles):
            scope = ("notification.admin.manage" if wanted == {"admin"}
                     else "notification.announcements.manage" if wanted == {"teacher"} else None)
            if not scope or not live_permission(principal, scope, settings.JWT_JWKS_URL):
                raise HTTPException(403, "Insufficient permissions")
        return principal

    return dependency
