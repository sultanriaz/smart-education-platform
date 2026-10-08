from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.errors import DomainError
from app.db.session import get_db
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryOut
from app.security.auth import Principal, get_principal, require_roles
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(
    _principal: Principal = Depends(get_principal),
    db: Session = Depends(get_db),
):
    return CategoryRepository(db).list_categories()


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    _admin: Principal = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    try:
        return CategoryService(db).create_category(payload)
    except DomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
