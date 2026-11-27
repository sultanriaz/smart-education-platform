from __future__ import annotations

import hashlib
from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from smartedu_security import (
    RedisFixedWindowLimiter,
    SecuritySettings,
    no_store_headers,
)
from smartedu_security.passwords import PasswordPolicyError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from .contracts import (
    IdentityAccountAdapter,
    IdentitySecurityNotificationSink,
    SecurityAuditSink,
)
from .service import IdentitySecurityService, InvalidOrExpiredToken


class ForgotPasswordRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20, max_length=512)
    new_password: str = Field(min_length=1, max_length=1024)


class VerificationRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)


class VerificationConfirmRequest(BaseModel):
    token: str = Field(min_length=20, max_length=512)


GENERIC_ACCEPTED = {"message": "If the account is eligible, instructions will be sent."}


def _hash_subject(value: str) -> str:
    return hashlib.sha256(value.strip().casefold().encode()).hexdigest()


def build_identity_security_router(
    *,
    get_db: Callable[..., Session],
    account_adapter_factory: Callable[[Session], IdentityAccountAdapter],
    notification_sink_factory: Callable[[Session], IdentitySecurityNotificationSink],
    audit_sink_factory: Callable[[Session], SecurityAuditSink],
    rate_limiter: RedisFixedWindowLimiter | None = None,
    settings: SecuritySettings | None = None,
) -> APIRouter:
    settings = settings or SecuritySettings()
    router = APIRouter(prefix="/auth", tags=["security"])

    async def throttle(
        request: Request,
        db: Session,
        *,
        purpose: str,
        subject: str,
        limit: int,
        window_seconds: int,
    ) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"{purpose}:{_hash_subject(client_ip)}:{_hash_subject(subject)}"
        if rate_limiter is not None:
            decision = await rate_limiter.hit(
                key,
                limit=limit,
                window_seconds=window_seconds,
            )
        else:
            from .throttle_store import DatabaseFixedWindowLimiter

            decision = DatabaseFixedWindowLimiter().hit_sync(
                db,
                key,
                limit=limit,
                window_seconds=window_seconds,
            )
        if not decision.allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Try again later.",
                headers={"Retry-After": str(decision.retry_after_seconds)},
            )

    def service(db: Session) -> IdentitySecurityService:
        return IdentitySecurityService(
            db=db,
            accounts=account_adapter_factory(db),
            notifications=notification_sink_factory(db),
            audit=audit_sink_factory(db),
            settings=settings,
        )

    @router.get("/password/forgot")
    @router.get("/password/forgot/")
    async def forgot_password_get():
        return {"message": "Please send a POST request with {'email': '...'} to request password reset."}

    @router.post(
        "/password/forgot",
        status_code=status.HTTP_202_ACCEPTED,
    )
    @router.post(
        "/password/forgot/",
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def forgot_password(
        body: ForgotPasswordRequest,
        request: Request,
        response: Response,
        db: Session = Depends(get_db),
    ):
        await throttle(
            request,
            db,
            purpose="forgot-password",
            subject=str(body.email),
            limit=5,
            window_seconds=900,
        )
        response.headers.update(no_store_headers())
        await run_in_threadpool(service(db).request_password_reset, str(body.email))
        return GENERIC_ACCEPTED

    @router.get("/password/reset")
    @router.get("/password/reset/")
    async def reset_password_get():
        return {"message": "Please send a POST request with {'token': '...', 'new_password': '...'} to reset password."}

    @router.post(
        "/password/reset",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    @router.post(
        "/password/reset/",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def reset_password(
        body: ResetPasswordRequest,
        request: Request,
        db: Session = Depends(get_db),
    ):
        await throttle(
            request,
            db,
            purpose="reset-password",
            subject=body.token[:32],
            limit=10,
            window_seconds=900,
        )
        try:
            await run_in_threadpool(
                service(db).reset_password,
                token=body.token,
                new_password=body.new_password,
            )
        except InvalidOrExpiredToken as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password-reset token",
            ) from exc
        except PasswordPolicyError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "password_policy_failed", "reasons": exc.reasons},
            ) from exc
        return Response(status_code=status.HTTP_204_NO_CONTENT, headers=no_store_headers())

    @router.get("/email/verification/request")
    @router.get("/email/verification/request/")
    async def request_verification_get():
        return {"message": "Please send a POST request with {'email': '...'} to request email verification."}

    @router.post(
        "/email/verification/request",
        status_code=status.HTTP_202_ACCEPTED,
    )
    @router.post(
        "/email/verification/request/",
        status_code=status.HTTP_202_ACCEPTED,
    )
    async def request_verification(
        body: VerificationRequest,
        request: Request,
        response: Response,
        db: Session = Depends(get_db),
    ):
        await throttle(
            request,
            db,
            purpose="email-verification",
            subject=str(body.email),
            limit=5,
            window_seconds=900,
        )
        response.headers.update(no_store_headers())
        await run_in_threadpool(service(db).request_email_verification, str(body.email))
        return GENERIC_ACCEPTED

    @router.get("/email/verification/confirm")
    @router.get("/email/verification/confirm/")
    async def confirm_verification_get():
        return {"message": "Please send a POST request with {'token': '...'} to confirm email verification."}

    @router.post(
        "/email/verification/confirm",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    @router.post(
        "/email/verification/confirm/",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def confirm_verification(
        body: VerificationConfirmRequest,
        request: Request,
        db: Session = Depends(get_db),
    ):
        await throttle(
            request,
            db,
            purpose="email-confirm",
            subject=body.token[:32],
            limit=10,
            window_seconds=900,
        )
        try:
            await run_in_threadpool(service(db).confirm_email_verification, body.token)
        except InvalidOrExpiredToken as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token",
            ) from exc
        return Response(status_code=status.HTTP_204_NO_CONTENT, headers=no_store_headers())

    return router


def get_security_router() -> APIRouter:
    import os
    from app.db.session import get_db
    from app.sprint18 import security_settings
    from app.sprint18_security.adapters import (
        AccountAdapter,
        SecurityAuditAdapter,
        SecurityNotificationAdapter,
    )

    limiter = None
    try:
        if os.environ.get("REDIS_URL") or os.environ.get("REDIS_CACHE_URL"):
            from app.sprint18 import identity_rate_limiter
            limiter = identity_rate_limiter()
    except Exception:
        limiter = None

    return build_identity_security_router(
        get_db=get_db,
        account_adapter_factory=AccountAdapter,
        notification_sink_factory=SecurityNotificationAdapter,
        audit_sink_factory=SecurityAuditAdapter,
        rate_limiter=limiter,
        settings=security_settings(),
    )
