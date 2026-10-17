import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select

from app.core.errors import ConflictError
from app.domain.models import Notification, NotificationCampaign
from app.schemas.notification import CampaignCreate, CampaignTarget
from app.services.campaign_service import CampaignService
from app.services.target_resolver import ResolvedRecipient


def request(*, draft=False, publish_at=None, expires_at=None):
    return CampaignCreate(
        target=CampaignTarget(kind="ROLE", role="student"), title="Attention",
        body="Something changed", draft=draft, publish_at=publish_at,
        expires_at=expires_at,
    )


def test_draft_edits_then_publishes_once(db, identities, fake_resolver):
    service = CampaignService(db, fake_resolver)
    fake_resolver.role_users = [ResolvedRecipient(identities["student"])]
    campaign, pending = service.create(request(draft=True), identities["admin"], None)
    assert campaign.status == "DRAFT" and not pending
    assert db.scalar(select(func.count()).select_from(Notification)) == 0
    updated = service.edit_pending(campaign.id, request(draft=True), identities["admin"])
    assert updated.status == "DRAFT"
    published, pending = service.publish_pending(campaign.id, actor_id=identities["admin"])
    assert published.status == "COMPLETED" and published.recipient_count == 1
    assert db.scalar(select(func.count()).select_from(Notification)) == 1
    again, repeat = service.publish_pending(campaign.id, actor_id=identities["admin"])
    assert again.id == campaign.id and repeat == []
    assert db.scalar(select(func.count()).select_from(Notification)) == 1
    with pytest.raises(ConflictError):
        service.edit_pending(campaign.id, request(draft=True), identities["admin"])


def test_scheduled_and_expired_campaigns_never_send_early(db, identities, fake_resolver):
    service = CampaignService(db, fake_resolver)
    fake_resolver.role_users = [ResolvedRecipient(identities["student"])]
    due = datetime.now(UTC) + timedelta(hours=2)
    campaign, pending = service.create(request(publish_at=due), identities["admin"], None)
    assert campaign.status == "SCHEDULED" and not pending
    _, pending = service.publish_pending(campaign.id, only_due=True)
    assert pending == [] and db.scalar(select(func.count()).select_from(Notification)) == 0
    archive = service.archive_campaign(campaign.id, actor_id=identities["admin"])
    assert archive.status == "ARCHIVED"
    with pytest.raises(ConflictError):
        service.publish_pending(campaign.id)
    future = datetime.now(UTC) + timedelta(hours=1)
    expired, _ = service.create(request(draft=True, expires_at=future), identities["admin"], None)
    expired.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    db.commit()
    expired, pending = service.publish_pending(expired.id)
    assert expired.status == "EXPIRED" and not pending


def test_campaign_target_validations():
    from pydantic import ValidationError
    for kind in ("COURSE", "PROGRAM", "DEPARTMENT", "SECTION"):
        with pytest.raises(ValidationError):
            CampaignTarget(kind=kind)
    assert CampaignTarget(kind="PROGRAM", program_id=uuid.uuid4()).kind == "PROGRAM"
    with pytest.raises(ValidationError):
        request(publish_at=datetime(2026, 11, 1))
