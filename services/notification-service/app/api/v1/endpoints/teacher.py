from __future__ import annotations

import uuid
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
