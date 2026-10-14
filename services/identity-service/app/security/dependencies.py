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
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
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
    if int(payload.get("auth_version", 0)) != user.auth_version:
        raise credentials_error
    if set(str(role).lower() for role in payload.get("roles", [])) != {
        role.name.lower() for role in user.roles
    } or set(payload.get("permissions", [])) != {
        permission.code for role in user.roles for permission in role.permissions
    }:
        raise credentials_error
    return user


def require_roles(*required_roles: str) -> Callable:
    required = {role.lower() for role in required_roles}

    def dependency(user=Depends(get_current_user)):
        actual = {role.name.lower() for role in user.roles}
        if required.isdisjoint(actual):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions."
            )
        return user

    return dependency


def require_permission(code: str) -> Callable:
    """Enforce a concrete permission, allowing the built-in admin role for compatibility.

    Custom roles receive ONLY their explicitly assigned permission codes.
    """
    def dependency(user=Depends(get_current_user)):
        if any(role.name.lower() == "admin" for role in user.roles):
            return user
        granted = {permission.code for role in user.roles for permission in role.permissions}
        if code not in granted:
            raise HTTPException(status_code=403, detail="Insufficient permissions.")
        return user
    return dependency
