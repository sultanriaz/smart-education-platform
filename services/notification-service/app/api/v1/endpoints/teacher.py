from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_dispatcher, get_target_resolver
from app.clients.academic import AcademicClient
from app.core.errors import DomainError
from app.db.session import get_db
from app.domain.models import NotificationCampaign
from app.queue.dispatcher import TaskDispatcher
from app.schemas.notification import CampaignCreate, CampaignOut, CampaignTarget
from app.security.auth import Principal
from app.security.authorization import require_roles
from app.services.campaign_service import CampaignService
from app.services.target_resolver import TargetResolver

router = APIRouter(prefix="/teacher", tags=["Teacher Announcements"])


class TeacherAnnouncementCreate(BaseModel):
    section_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=10000)
    category: str = Field(
        default="teacher_announcement",
        min_length=1,
        max_length=80,
    )
    priority: Literal["LOW", "NORMAL", "HIGH", "URGENT"] = "NORMAL"
    channels: list[Literal["IN_APP", "EMAIL"]] = ["IN_APP"]
    draft: bool = False
    publish_at: datetime | None = None
    expires_at: datetime | None = None


@router.post("/announcements", response_model=CampaignOut, status_code=201)
def create_announcement(
    payload: TeacherAnnouncementCreate,
    teacher: Principal = Depends(require_roles("teacher")),
    db: Session = Depends(get_db),
    resolver: TargetResolver = Depends(get_target_resolver),
    dispatcher: TaskDispatcher = Depends(get_dispatcher),
):
    academic: AcademicClient = resolver.academic

    try:
        if not academic.validate_teacher_assignment(
            teacher.user_id,
            payload.section_id,
            teacher.raw_token,
        ):
            raise HTTPException(
                status_code=403,
                detail="Teacher is not assigned to this section",
            )

        campaign_payload = CampaignCreate(
            target=CampaignTarget(
                kind="SECTION",
                section_id=payload.section_id,
            ),
            title=payload.title,
            body=payload.body,
            category=payload.category,
            priority=payload.priority,
            channels=payload.channels,
            draft=payload.draft, publish_at=payload.publish_at, expires_at=payload.expires_at,
            data={
                "section_id": str(payload.section_id),
                "teacher_user_id": str(teacher.user_id),
            },
        )

        campaign, pending = CampaignService(db, resolver).create(
            campaign_payload,
            teacher.user_id,
            teacher.raw_token,
        )
        for attempt_id in pending:
            dispatcher.deliver_attempt(attempt_id)
        return campaign
    except DomainError as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 400),
            detail=str(exc),
        ) from exc


@router.get("/announcements", response_model=list[CampaignOut])
def list_my_announcements(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    teacher: Principal = Depends(require_roles("teacher")),
    db: Session = Depends(get_db),
):
    stmt = (
        select(NotificationCampaign)
        .where(
            NotificationCampaign.created_by_user_id == teacher.user_id,
            NotificationCampaign.target_kind == "SECTION",
        )
        .order_by(NotificationCampaign.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


@router.put("/announcements/{campaign_id}", response_model=CampaignOut)
def edit_announcement(
    campaign_id: uuid.UUID, payload: TeacherAnnouncementCreate,
    teacher: Principal = Depends(require_roles("teacher")),
    db: Session = Depends(get_db),
    resolver: TargetResolver = Depends(get_target_resolver),
):
    if not resolver.academic.validate_teacher_assignment(teacher.user_id, payload.section_id, teacher.raw_token):
        raise HTTPException(403, detail="Teacher is not assigned to this section")
    campaign = db.get(NotificationCampaign, campaign_id)
    if not campaign or campaign.created_by_user_id != teacher.user_id or campaign.target_kind != "SECTION":
        raise HTTPException(403, detail="Not your section announcement")
    from app.core.errors import ConflictError
    try:
        return CampaignService(db, resolver).edit_pending(
            campaign_id,
            CampaignCreate(target=CampaignTarget(kind="SECTION", section_id=payload.section_id),
                           title=payload.title, body=payload.body, category=payload.category,
                           priority=payload.priority, channels=payload.channels,
                           draft=payload.draft, publish_at=payload.publish_at,
                           expires_at=payload.expires_at), teacher.user_id,
        )
    except ConflictError as exc:
        raise HTTPException(409, detail=str(exc)) from exc


@router.post("/announcements/{campaign_id}/publish", response_model=CampaignOut)
def publish_announcement(
    campaign_id: uuid.UUID,
    teacher: Principal = Depends(require_roles("teacher")),
    db: Session = Depends(get_db),
    resolver: TargetResolver = Depends(get_target_resolver),
    dispatcher: TaskDispatcher = Depends(get_dispatcher),
):
    campaign = db.get(NotificationCampaign, campaign_id)
    if not campaign or campaign.created_by_user_id != teacher.user_id or campaign.target_kind != "SECTION":
        raise HTTPException(403, detail="Not your section announcement")
    target = CampaignTarget.model_validate(campaign.target_value)
    if not resolver.academic.validate_teacher_assignment(teacher.user_id, target.section_id, teacher.raw_token):
        raise HTTPException(403, detail="Teacher is no longer assigned to this section")
    from app.core.errors import ConflictError
    try:
        campaign, pending = CampaignService(db, resolver).publish_pending(campaign_id, actor_id=teacher.user_id)
    except ConflictError as exc:
        raise HTTPException(409, detail=str(exc)) from exc
    for attempt in pending:
        dispatcher.deliver_attempt(attempt)
    return campaign
