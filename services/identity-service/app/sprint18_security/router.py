from __future__ import annotations

import hashlib
from collections.abc import Callable

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr, Field
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
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=20, max_length=512)
    new_password: str = Field(min_length=1, max_length=1024)


class VerificationRequest(BaseModel):
    email: EmailStr


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
        *,
        purpose: str,
        subject: str,
        limit: int,
        window_seconds: int,
    ) -> None:
        if rate_limiter is None:
            return

        client_ip = request.client.host if request.client else "unknown"
        key = f"{purpose}:{_hash_subject(client_ip)}:{_hash_subject(subject)}"
        decision = await rate_limiter.hit(
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

    @router.post(
        "/password/forgot",
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
            purpose="forgot-password",
            subject=str(body.email),
            limit=5,
            window_seconds=900,
        )
        response.headers.update(no_store_headers())
        await run_in_threadpool(service(db).request_password_reset, str(body.email))
        return GENERIC_ACCEPTED

    @router.post(
        "/password/reset",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def reset_password(
        body: ResetPasswordRequest,
        request: Request,
        db: Session = Depends(get_db),
    ):
        await throttle(
            request,
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

    @router.post(
        "/email/verification/request",
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
            purpose="email-verification",
            subject=str(body.email),
            limit=5,
            window_seconds=900,
        )
        response.headers.update(no_store_headers())
        await run_in_threadpool(service(db).request_email_verification, str(body.email))
        return GENERIC_ACCEPTED

    @router.post(
        "/email/verification/confirm",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    async def confirm_verification(
        body: VerificationConfirmRequest,
        request: Request,
        db: Session = Depends(get_db),
    ):
        await throttle(
            request,
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
