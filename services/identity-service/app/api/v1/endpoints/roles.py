from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.db.session import get_db
from app.domain.entities.user import User
from app.repositories.role_repository import RoleRepository
from app.schemas.role import PermissionOut, RoleCreate, RoleOut
from app.security.dependencies import require_roles
from app.services.role_service import RoleService

router = APIRouter(tags=["RBAC"])
Admin = Annotated[User, Depends(require_roles("admin"))]
Database = Annotated[Session, Depends(get_db)]


@router.get("/roles", response_model=list[RoleOut])
def list_roles(_admin: Admin, db: Database):
    return RoleRepository(db).list_roles()


@router.post("/roles", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(payload: RoleCreate, _admin: Admin, db: Database):
    try:
        return RoleService(db).create(payload)
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/permissions", response_model=list[PermissionOut])
def list_permissions(_admin: Admin, db: Database):
    return RoleRepository(db).list_permissions()
