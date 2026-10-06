import uuid
from collections.abc import Callable

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.security.jwt import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired access token.", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = decode_token(token)
    except jwt.PyJWTError as exc:
        raise credentials_error from exc
    if payload.get("type") != "access" or not payload.get("sub"):
        raise credentials_error
    try:
        user_id = uuid.UUID(payload["sub"])
    except ValueError as exc:
        raise credentials_error from exc
    user = UserRepository(db).get_by_id(user_id)
    if user is None or not user.is_active:
        raise credentials_error
    return user


def require_roles(*required_roles: str) -> Callable:
    required = {role.lower() for role in required_roles}

    def dependency(user=Depends(get_current_user)):
        actual = {role.name.lower() for role in user.roles}
        if required.isdisjoint(actual):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions.")
        return user

    return dependency
