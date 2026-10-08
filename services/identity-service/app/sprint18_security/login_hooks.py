from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, Request, Response, status
from smartedu_security import LoginSecurityGuard, SecuritySettings
from smartedu_security.security_events import (
    LOGIN_FAILED,
    LOGIN_LOCKED,
    LOGIN_SUCCEEDED,
)

from .contracts import SecurityAuditSink
from .cookie_auth import (
    clear_browser_refresh_cookie,
    public_access_token_payload,
    refresh_token_from_cookie,
    set_browser_refresh_cookie,
)


@dataclass(slots=True)
class BrowserTokenPair:
    access_token: str
    refresh_token: str
    access_expires_in: int | None = None


class LoginSecurityHooks:
    """
    Adapter used by the existing Sprint 1 login/refresh/logout endpoints.

    Codex should wire these hooks around the REAL AuthService instead of creating
    a second authentication implementation.
    """

    def __init__(
        self,
        *,
        guard: LoginSecurityGuard,
        audit: SecurityAuditSink,
        settings: SecuritySettings,
    ):
        self.guard = guard
        self.audit = audit
        self.settings = settings

    async def before_password_check(self, email: str) -> None:
        decision = await self.guard.precheck(email)
        if decision.allowed:
            return

        self.audit.record(
            event_type=LOGIN_LOCKED,
            user_id=None,
            metadata={
                "retry_after_seconds": decision.retry_after_seconds,
                "failure_count": decision.failure_count,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed sign-in attempts. Try again later.",
            headers={"Retry-After": str(decision.retry_after_seconds)},
        )

    async def password_failed(self, email: str) -> None:
        decision = await self.guard.failed(email)
        self.audit.record(
            event_type=LOGIN_FAILED,
            user_id=None,
            metadata={
                "failure_count": decision.failure_count,
                "locked": not decision.allowed,
            },
        )

    async def password_succeeded(self, email: str, user_id) -> None:
        await self.guard.succeeded(email)
        self.audit.record(
            event_type=LOGIN_SUCCEEDED,
            user_id=user_id,
            metadata={},
        )

    def browser_login_response(
        self,
        response: Response,
        pair: BrowserTokenPair,
    ) -> dict[str, object]:
        set_browser_refresh_cookie(
            response,
            pair.refresh_token,
            self.settings,
        )
        return public_access_token_payload(
            pair.access_token,
            expires_in=pair.access_expires_in,
        )

    def browser_refresh_token(self, request: Request) -> str:
        return refresh_token_from_cookie(request, self.settings)

    def browser_refresh_response(
        self,
        response: Response,
        pair: BrowserTokenPair,
    ) -> dict[str, object]:
        # Existing Sprint 1 refresh rotation remains authoritative. The rotated
        # token is written back to HttpOnly cookie storage.
        set_browser_refresh_cookie(
            response,
            pair.refresh_token,
            self.settings,
        )
        return public_access_token_payload(
            pair.access_token,
            expires_in=pair.access_expires_in,
        )

    def browser_logout_token(self, request: Request) -> str:
        return refresh_token_from_cookie(request, self.settings)

    def clear_browser_session(self, response: Response) -> None:
        clear_browser_refresh_cookie(response, self.settings)
