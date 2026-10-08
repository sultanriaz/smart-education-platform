"""Notification recipient lookup authenticated with a scoped service JWT."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from smartedu_contracts import internal_auth_dependency
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.domain.entities.role import Role
from app.domain.entities.user import User
from app.schemas.user import UserOut
from app.sprint16 import internal_token_verifier

router = APIRouter(prefix="/internal/users", tags=["internal recipients"])
Internal = Annotated[
    object,
    Depends(
        internal_auth_dependency(
            internal_token_verifier(),
            audience="identity-service",
            required_scopes=("identity:recipients:read",),
        )
    ),
]


@router.get("", response_model=list[UserOut])
def recipients(
    principal: Internal,
    db: Annotated[Session, Depends(get_db)],
    role: str | None = None,
    limit: int = Query(200, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    if principal.service_name != "notification-service":
        raise HTTPException(403, "This recipient contract is reserved for Notification.")
    query = (
        select(User)
        .options(selectinload(User.roles))
        .where(User.is_active.is_(True))
        .order_by(User.id)
    )
    if role:
        query = query.where(User.roles.any(Role.name == role))
    return list(db.scalars(query.limit(limit).offset(offset)))


@router.get("/{user_id}", response_model=UserOut)
def recipient(user_id: UUID, principal: Internal, db: Annotated[Session, Depends(get_db)]):
    if principal.service_name != "notification-service":
        raise HTTPException(403, "This recipient contract is reserved for Notification.")
    user = db.scalar(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == user_id, User.is_active.is_(True))
    )
    if user is None:
        raise HTTPException(404, "Active recipient not found.")
    return user
