from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, ConflictError
from app.db.session import get_db
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, TokenPair
from app.schemas.user import UserOut, UserRegister
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


def client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, request: Request, db: Session = Depends(get_db)):
    try:
        return AuthService(db).register(payload, client_ip(request))
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    try:
        return AuthService(db).login(str(payload.email), payload.password, client_ip(request))
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        return AuthService(db).refresh(payload.refresh_token)
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    AuthService(db).logout(payload.refresh_token)
    return None
