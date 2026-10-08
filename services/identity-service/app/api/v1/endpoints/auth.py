from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from smartedu_security import LoginSecurityGuard, PasswordPolicyError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.core.exceptions import AuthenticationError, ConflictError
from app.db.session import get_db
from app.schemas.auth import LoginRequest
from app.schemas.user import UserOut, UserRegister
from app.services.auth_service import AuthService
from app.sprint18 import login_lockout_store, security_settings
from app.sprint18_security.cookie_auth import (
    clear_browser_refresh_cookie,
    public_access_token_payload,
    refresh_token_from_cookie,
    set_browser_refresh_cookie,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def login_guard():
    return LoginSecurityGuard(login_lockout_store())


def browser_pair(response, pair):
    set_browser_refresh_cookie(response, pair.refresh_token, security_settings())
    response.headers["Cache-Control"] = "no-store"
    return public_access_token_payload(pair.access_token, expires_in=pair.expires_in)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, request: Request, db: Session = Depends(get_db)):
    try:
        return AuthService(db).register(payload, client_ip(request))
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except PasswordPolicyError as exc:
        raise HTTPException(
            status_code=422, detail={"code": "password_policy_failed", "reasons": exc.reasons}
        ) from exc


@router.post("/login")
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    guard: LoginSecurityGuard = Depends(login_guard),
):
    email = str(payload.email)
    decision = await guard.precheck(email)
    if not decision.allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many failed sign-in attempts. Try again later.",
            headers={"Retry-After": str(decision.retry_after_seconds)},
        )
    try:
        pair = await run_in_threadpool(
            AuthService(db).login, email, payload.password, client_ip(request)
        )
    except AuthenticationError as exc:
        await guard.failed(email)
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    await guard.succeeded(email)
    return browser_pair(response, pair)


@router.post("/refresh")
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    token = refresh_token_from_cookie(request, security_settings())
    try:
        return browser_pair(response, AuthService(db).refresh(token))
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = refresh_token_from_cookie(request, security_settings())
    AuthService(db).logout(token)
    clear_browser_refresh_cookie(response, security_settings())
    response.headers["Cache-Control"] = "no-store"
