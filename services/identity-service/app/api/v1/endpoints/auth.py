import os

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from smartedu_security import LoginSecurityGuard, PasswordPolicyError, require_trusted_origin
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.core.exceptions import AuthenticationError, ConflictError
from app.db.session import SessionLocal, get_db
from app.repositories.user_repository import UserRepository
from app.security.dependencies import get_current_user
from app.schemas.auth import LoginRequest
from app.schemas.user import UserOut, UserRegister
from app.services.auth_service import AuthService
from app.sprint18 import identity_rate_limiter, login_lockout_store, security_settings
from app.sprint18_security.cookie_auth import (
    clear_browser_refresh_cookie,
    public_access_token_payload,
    refresh_token_from_cookie,
    set_browser_refresh_cookie,
)
from app.sprint18_security.throttle_store import DatabaseFixedWindowLimiter, DatabaseLockoutStore

router = APIRouter(prefix="/auth", tags=["Authentication"])


def client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _redis_configured() -> bool:
    return bool(
        os.environ.get("REDIS_URL")
        or os.environ.get("REDIS_CACHE_URL")
        or os.environ.get("AUTH_SECURITY_REDIS_URL")
    )


def login_guard():
    if _redis_configured():
        try:
            return LoginSecurityGuard(login_lockout_store())
        except Exception:
            pass
    cfg = security_settings()
    return LoginSecurityGuard(
        DatabaseLockoutStore(
            SessionLocal,
            max_failures=cfg.login_max_failures,
            failure_window_seconds=cfg.login_failure_window_seconds,
            lock_seconds=cfg.login_lock_seconds,
        )
    )


async def _throttle_register(request: Request, db: Session) -> None:
    ip = client_ip(request) or "unknown"
    key = f"register:{ip}"
    if _redis_configured():
        try:
            decision = await identity_rate_limiter().hit(key, limit=20, window_seconds=900)
        except Exception:
            decision = DatabaseFixedWindowLimiter(SessionLocal).hit_sync(db, key, limit=20, window_seconds=900)
    else:
        decision = DatabaseFixedWindowLimiter(SessionLocal).hit_sync(db, key, limit=20, window_seconds=900)
    if not decision.allowed:
        raise HTTPException(
            status_code=429,
            detail="Too many registration attempts. Try again later.",
            headers={"Retry-After": str(decision.retry_after_seconds)},
        )


def browser_pair(response, pair):
    set_browser_refresh_cookie(response, pair.refresh_token, security_settings())
    response.headers["Cache-Control"] = "no-store"
    return public_access_token_payload(pair.access_token, expires_in=pair.expires_in)


@router.get("/register")
@router.get("/register/")
async def register_get_help():
    return {"message": "Please send a POST request with {'email': '...', 'full_name': '...', 'password': '...'} to register."}


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
@router.post("/register/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegister, request: Request, db: Session = Depends(get_db)):
    await _throttle_register(request, db)
    try:
        return await run_in_threadpool(AuthService(db).register, payload, client_ip(request))
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except PasswordPolicyError as exc:
        raise HTTPException(
            status_code=422, detail={"code": "password_policy_failed", "reasons": exc.reasons}
        ) from exc


@router.get("/login")
@router.get("/login/")
async def login_get_help():
    return {"message": "Please send a POST request with {'email': '...', 'password': '...'} to authenticate."}


@router.post("/login")
@router.post("/login/")
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    guard: LoginSecurityGuard = Depends(login_guard),
):
    identifier = str(payload.email).strip().casefold()
    matched = await run_in_threadpool(UserRepository(db).get_by_identifier, identifier)
    subjects = [identifier]
    if matched is not None:
        subjects.append(f"user:{matched.id}")

    for subject in subjects:
        decision = await guard.precheck(subject)
        if not decision.allowed:
            raise HTTPException(
                status_code=429,
                detail="Too many failed sign-in attempts. Try again later.",
                headers={"Retry-After": str(decision.retry_after_seconds)},
            )
    try:
        pair = await run_in_threadpool(
            AuthService(db).login, identifier, payload.password, client_ip(request)
        )
    except AuthenticationError as exc:
        for subject in subjects:
            await guard.failed(subject)
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    for subject in subjects:
        await guard.succeeded(subject)
    return browser_pair(response, pair)


@router.get("/refresh")
@router.get("/refresh/")
async def refresh_get_help():
    return {"message": "Please send a POST request with authentication cookies to refresh your session."}


@router.post("/refresh")
@router.post("/refresh/")
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    token = refresh_token_from_cookie(request, security_settings())
    try:
        return browser_pair(response, AuthService(db).refresh(token))
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.get("/logout")
@router.get("/logout/")
async def logout_get_help():
    return {"message": "Please send a POST request to logout."}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@router.post("/logout/", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    sec = security_settings()
    require_trusted_origin(request, sec.frontend_origins)
    refresh_token = request.cookies.get(sec.refresh_cookie_name)
    auth_header = request.headers.get("authorization", "")
    access_token = auth_header[7:].strip() if auth_header.lower().startswith("bearer ") else None
    AuthService(db).logout(refresh_token, access_token=access_token)
    clear_browser_refresh_cookie(response, sec)
    response.headers["Cache-Control"] = "no-store"


@router.get("/access-status")
def access_status(user=Depends(get_current_user)):
    """Authoritative non-cacheable access status for sibling services."""
    return {"active": True, "user_id": str(user.id),
            "roles": sorted(role.name.lower() for role in user.roles)}
