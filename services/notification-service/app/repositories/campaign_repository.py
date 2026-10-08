from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import NotificationCampaign


class CampaignRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_campaign(self, campaign: NotificationCampaign) -> None:
        self.db.add(campaign)

    def get_campaign(self, campaign_id: uuid.UUID) -> NotificationCampaign | None:
        return self.db.get(NotificationCampaign, campaign_id)

    def list_campaigns(self, offset: int, limit: int) -> list[NotificationCampaign]:
        stmt = (
            select(NotificationCampaign)
            .order_by(NotificationCampaign.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
