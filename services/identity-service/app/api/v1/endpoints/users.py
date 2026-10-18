import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from smartedu_security import PasswordPolicyError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.audit_repository import AuditRepository
from app.schemas.security_history import SecurityActivityOut
from app.schemas.user import AdminUserCreate, AdminUserUpdate, UserOut, UserSelfUpdate
from app.security.dependencies import get_current_user, require_permission, require_roles
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserOut)
def me(user=Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UserSelfUpdate, user=Depends(get_current_user), db: Session = Depends(get_db)
):
    return UserService(db).update_self(user, payload)


@router.get("", response_model=list[UserOut])
def list_users(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    _admin=Depends(require_permission("identity.users.read")),
    db: Session = Depends(get_db),
):
    return UserRepository(db).list_users(offset=offset, limit=limit)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: AdminUserCreate, _admin=Depends(require_permission("identity.users.write")), db: Session = Depends(get_db)
):
    try:
        return UserService(db).create_by_admin(payload)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PasswordPolicyError as exc:
        raise HTTPException(
            status_code=422, detail={"code": "password_policy_failed", "reasons": exc.reasons}
        ) from exc


@router.get("/me/security-history", response_model=list[SecurityActivityOut])
def own_security_history(offset: int = Query(default=0, ge=0), limit: int = Query(default=50, ge=1, le=100), user=Depends(get_current_user), db: Session = Depends(get_db)):
    return AuditRepository(db).history(user_id=user.id, offset=offset, limit=limit)


@router.get("/security-history", response_model=list[SecurityActivityOut])
def admin_security_history(user_id: uuid.UUID | None = None, action: str | None = None, outcome: str | None = None, from_date: datetime | None = None, to_date: datetime | None = None, offset: int = Query(default=0, ge=0), limit: int = Query(default=50, ge=1, le=100), _admin=Depends(require_roles("admin")), db: Session = Depends(get_db)):
    if from_date and to_date and from_date > to_date:
        raise HTTPException(422, "from_date exceeds to_date")
    return AuditRepository(db).history(user_id=user_id, action=action, outcome=outcome, from_date=from_date, to_date=to_date, offset=offset, limit=limit)


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: uuid.UUID, _admin=Depends(require_permission("identity.users.read")), db: Session = Depends(get_db)
):
    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: uuid.UUID,
    payload: AdminUserUpdate,
    _admin=Depends(require_permission("identity.users.write")),
    db: Session = Depends(get_db),
):
    try:
        return UserService(db).update_by_admin(user_id, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/{user_id}", response_model=UserOut)
def deactivate_user(
    user_id: uuid.UUID, _admin=Depends(require_permission("identity.users.write")), db: Session = Depends(get_db)
):
    try:
        return UserService(db).deactivate(user_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
