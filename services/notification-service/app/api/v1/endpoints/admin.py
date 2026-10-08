from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_dispatcher, get_target_resolver
from app.db.session import get_db
from app.queue.dispatcher import TaskDispatcher
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.delivery_repository import DeliveryRepository
from app.repositories.template_repository import TemplateRepository
from app.schemas.notification import (
    CampaignCreate,
    CampaignOut,
    DeliveryAttemptOut,
    TemplateCreate,
    TemplateOut,
    TemplateUpdate,
)
from app.security.auth import Principal
from app.security.authorization import require_roles
from app.services.campaign_service import CampaignService
from app.services.target_resolver import TargetResolver
from app.services.template_service import TemplateService

router = APIRouter(prefix="/admin", tags=["Notification Administration"])


@router.get("/templates", response_model=list[TemplateOut])
def list_templates(
    _admin: Principal = Depends(require_roles("admin")), db: Session = Depends(get_db)
):
    return TemplateRepository(db).list_templates()


@router.post("/templates", response_model=TemplateOut, status_code=201)
def create_template(
    payload: TemplateCreate,
    admin: Principal = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    return TemplateService(db).create(payload, admin.user_id)


@router.patch("/templates/{template_id}", response_model=TemplateOut)
def update_template(
    template_id: uuid.UUID,
    payload: TemplateUpdate,
    _admin: Principal = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    return TemplateService(db).update(template_id, payload)


@router.post("/campaigns", response_model=CampaignOut, status_code=201)
def create_campaign(
    payload: CampaignCreate,
    admin: Principal = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
    resolver: TargetResolver = Depends(get_target_resolver),
    dispatcher: TaskDispatcher = Depends(get_dispatcher),
):
    campaign, pending = CampaignService(db, resolver).create(
        payload, admin.user_id, admin.raw_token
    )
    for attempt_id in pending:
        dispatcher.deliver_attempt(attempt_id)
    return campaign


@router.get("/campaigns", response_model=list[CampaignOut])
def list_campaigns(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    _admin: Principal = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    return CampaignRepository(db).list_campaigns(offset, limit)


@router.get("/notifications/{notification_id}/deliveries", response_model=list[DeliveryAttemptOut])
def list_deliveries(
    notification_id: uuid.UUID,
    _admin: Principal = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
):
    return DeliveryRepository(db).list_attempts_for_notification(notification_id)
