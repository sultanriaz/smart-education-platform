from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.notification import PreferenceOut, PreferenceUpdate
from app.security.auth import Principal, get_current_principal
from app.services.preference_service import PreferenceService

router = APIRouter(prefix="/preferences", tags=["Preferences"])


@router.get("/me", response_model=PreferenceOut)
def get_preferences(
    principal: Principal = Depends(get_current_principal), db: Session = Depends(get_db)
):
    return PreferenceService(db).get_or_create(principal.user_id)


@router.patch("/me", response_model=PreferenceOut)
def update_preferences(
    payload: PreferenceUpdate,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    return PreferenceService(db).update(principal.user_id, payload)
