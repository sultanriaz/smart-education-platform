from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.common import MessageOut
from app.schemas.notification import NotificationListOut, NotificationOut, UnreadCountOut
from app.security.auth import Principal, get_current_principal
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=NotificationListOut)
def list_notifications(
    unread_only: bool = False,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1),
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    limit = min(limit, settings.MAX_PAGE_SIZE)
    items, total = NotificationService(db).list_for_user(
        principal.user_id, unread_only, offset, limit
    )
    return NotificationListOut(items=items, total=total, offset=offset, limit=limit)


@router.get("/unread-count", response_model=UnreadCountOut)
def unread_count(
    principal: Principal = Depends(get_current_principal), db: Session = Depends(get_db)
):
    return UnreadCountOut(unread_count=NotificationService(db).unread_count(principal.user_id))


@router.get("/{notification_id}", response_model=NotificationOut)
def get_notification(
    notification_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    return NotificationService(db).get_for_user(notification_id, principal.user_id)


@router.post("/{notification_id}/read", response_model=NotificationOut)
def mark_read(
    notification_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    return NotificationService(db).mark_read(notification_id, principal.user_id)


@router.post("/read-all", response_model=MessageOut)
def read_all(principal: Principal = Depends(get_current_principal), db: Session = Depends(get_db)):
    count = NotificationService(db).mark_all_read(principal.user_id)
    return MessageOut(message=f"Marked {count} notifications as read")


@router.delete("/{notification_id}", response_model=NotificationOut)
def archive_notification(
    notification_id: uuid.UUID,
    principal: Principal = Depends(get_current_principal),
    db: Session = Depends(get_db),
):
    return NotificationService(db).archive(notification_id, principal.user_id)
