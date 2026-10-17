from __future__ import annotations
from datetime import UTC, datetime

import uuid

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ConflictError, ForbiddenError, NotFoundError, TemplateRenderError
from app.domain.models import (
    DeliveryAttempt,
    Notification,
    NotificationCampaign,
    NotificationPreference,
    OutboxEvent,
)
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.delivery_repository import DeliveryRepository
from app.repositories.notification_repository import NotificationRepository
from app.repositories.outbox_repository import OutboxRepository
from app.repositories.preference_repository import PreferenceRepository
from app.repositories.template_repository import TemplateRepository
from app.schemas.notification import CampaignCreate, CampaignTarget
from app.services.target_resolver import ResolvedRecipient, TargetResolver
from app.services.template_renderer import render_template


class CampaignService:
    def __init__(self, db: Session, resolver: TargetResolver | None = None):
        self.db = db
        self.resolver = resolver or TargetResolver()
        self.campaigns = CampaignRepository(db)
        self.notifications = NotificationRepository(db)
        self.preferences = PreferenceRepository(db)
        self.templates = TemplateRepository(db)
        self.deliveries = DeliveryRepository(db)
        self.outbox = OutboxRepository(db)

    def create(
        self, payload: CampaignCreate, actor_user_id: uuid.UUID, forwarded_token: str | None
    ) -> tuple[NotificationCampaign, list[uuid.UUID]]:
        title, body, category, channels = self._content(payload)
        # Drafts and future campaigns must not resolve or deliver early.
        if payload.draft or (payload.publish_at and payload.publish_at > datetime.now(UTC)):
            campaign = NotificationCampaign(
                created_by_user_id=actor_user_id,
                target_kind=payload.target.kind,
                target_value=payload.target.model_dump(mode="json", exclude_none=True),
                template_code=payload.template_code, title=title, body=body,
                category=category, channels=channels, priority=payload.priority,
                data=payload.data, scheduled_for=payload.publish_at,
                expires_at=payload.expires_at,
                status="DRAFT" if payload.draft else "SCHEDULED",
                recipient_count=0,
            )
            self.campaigns.add_campaign(campaign)
            self.db.commit()
            self.db.refresh(campaign)
            return campaign, []
        recipients = self.resolver.resolve(payload.target, forwarded_token)
        campaign = NotificationCampaign(
            created_by_user_id=actor_user_id,
            target_kind=payload.target.kind,
            target_value=payload.target.model_dump(mode="json", exclude_none=True),
            template_code=payload.template_code,
            title=title,
            body=body,
            category=category,
            channels=channels,
            recipient_count=len(recipients),
            status="COMPLETED",
            priority=payload.priority, data=payload.data,
            scheduled_for=payload.publish_at, expires_at=payload.expires_at,
        )
        self.campaigns.add_campaign(campaign)
        self.db.flush()
        pending = self._create_notifications(
            recipients=recipients,
            campaign=campaign,
            title=title,
            body=body,
            category=category,
            priority=payload.priority,
            channels=channels,
            data=payload.data,
        )
        self.outbox.add_event(
            OutboxEvent(
                event_type="notification.campaign_created",
                aggregate_type="campaign",
                aggregate_id=campaign.id,
                payload={"recipient_count": len(recipients), "category": category},
            )
        )
        self.db.commit()
        self.db.refresh(campaign)
        return campaign, pending

    def edit_pending(self, campaign_id: uuid.UUID, payload: CampaignCreate,
                     actor_id: uuid.UUID, *, is_admin: bool = False):
        campaign = self.db.get(NotificationCampaign, campaign_id, with_for_update=True)
        if campaign is None:
            raise NotFoundError("Campaign not found")
        if not is_admin and campaign.created_by_user_id != actor_id:
            raise ForbiddenError("Not the campaign owner")
        if campaign.status not in {"DRAFT", "SCHEDULED"}:
            raise ConflictError("Sent or archived campaigns cannot be edited")
        title, body, category, channels = self._content(payload)
        campaign.target_kind = payload.target.kind
        campaign.target_value = payload.target.model_dump(mode="json", exclude_none=True)
        campaign.template_code = payload.template_code
        campaign.title, campaign.body, campaign.category = title, body, category
        campaign.channels, campaign.priority, campaign.data = channels, payload.priority, payload.data
        campaign.scheduled_for, campaign.expires_at = payload.publish_at, payload.expires_at
        campaign.status = "DRAFT" if payload.draft else "SCHEDULED"
        if campaign.status == "SCHEDULED" and not payload.publish_at:
            raise ConflictError("Scheduled campaigns require publish_at")
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def publish_pending(self, campaign_id: uuid.UUID, *, actor_id: uuid.UUID | None = None,
                        is_admin: bool = False, only_due: bool = False):
        from sqlalchemy import select
        campaign = self.db.scalar(select(NotificationCampaign).where(
            NotificationCampaign.id == campaign_id).with_for_update())
        if campaign is None:
            raise NotFoundError("Campaign not found")
        if actor_id is not None and not is_admin and campaign.created_by_user_id != actor_id:
            raise ForbiddenError("Not the campaign owner")
        if campaign.status == "COMPLETED":
            return campaign, []  # idempotent, never send twice
        if campaign.status not in {"DRAFT", "SCHEDULED"}:
            raise ConflictError("Campaign cannot be published from this state")
        now = datetime.now(UTC)
        if only_due and (campaign.status != "SCHEDULED" or
                         not campaign.scheduled_for or
                         (campaign.scheduled_for if campaign.scheduled_for.tzinfo else
                          campaign.scheduled_for.replace(tzinfo=UTC)) > now):
            return campaign, []
        if campaign.expires_at and (campaign.expires_at if campaign.expires_at.tzinfo else
                                    campaign.expires_at.replace(tzinfo=UTC)) <= now:
            campaign.status = "EXPIRED"
            self.db.commit()
            return campaign, []
        target = CampaignTarget.model_validate(campaign.target_value)
        recipients = self.resolver.resolve(target, None)  # signed internal service tokens
        pending = self._create_notifications(
            recipients=recipients, campaign=campaign,
            title=campaign.title, body=campaign.body, category=campaign.category,
            priority=campaign.priority, channels=campaign.channels, data=campaign.data,
        )
        campaign.recipient_count = len(recipients)
        campaign.status = "COMPLETED"
        self.outbox.add_event(OutboxEvent(
            event_type="notification.campaign_created", aggregate_type="campaign",
            aggregate_id=campaign.id, payload={"recipient_count": len(recipients),
                                               "category": campaign.category},
        ))
        self.db.commit()
        self.db.refresh(campaign)
        return campaign, pending

    def archive_campaign(self, campaign_id: uuid.UUID, *, actor_id: uuid.UUID,
                         is_admin: bool = False):
        campaign = self.db.get(NotificationCampaign, campaign_id, with_for_update=True)
        if campaign is None:
            raise NotFoundError("Campaign not found")
        if not is_admin and campaign.created_by_user_id != actor_id:
            raise ForbiddenError("Not the campaign owner")
        if campaign.status not in {"ARCHIVED", "COMPLETED", "DRAFT", "SCHEDULED"}:
            raise ConflictError("Campaign cannot be archived")
        # Delivered notices remain in recipient history; no new future publication.
        campaign.status = "ARCHIVED"
        self.db.commit()
        return campaign

    def create_from_event(
        self,
        *,
        recipients: list[ResolvedRecipient],
        source_service: str,
        source_event_id: str,
        event_type: str,
        payload: dict,
    ) -> list[uuid.UUID]:
        template = self.templates.get_by_code(event_type)
        context = payload
        if template and template.enabled:
            title = render_template(template.title_template, context)
            body = render_template(template.body_template, context)
            category = template.category
            channels = list(template.default_channels)
        else:
            title = str(payload.get("title") or event_type.replace(".", " ").title())[:255]
            body = str(
                payload.get("message") or payload.get("reason") or "A campus update is available."
            )
            category = str(payload.get("category") or source_service)[:80]
            channels = ["IN_APP"]
        pending = self._create_notifications(
            recipients=recipients,
            campaign=None,
            title=title,
            body=body,
            category=category,
            priority=str(payload.get("priority") or "NORMAL").upper(),
            channels=channels,
            data=payload,
            source_service=source_service,
            source_event_id=source_event_id,
        )
        return pending

    def _content(self, payload: CampaignCreate) -> tuple[str, str, str, list[str]]:
        if payload.template_code:
            template = self.templates.get_by_code(payload.template_code)
            if template is None or not template.enabled:
                raise NotFoundError("Notification template not found or disabled")
            title = render_template(template.title_template, payload.template_data)
            body = render_template(template.body_template, payload.template_data)
            category = payload.category if payload.category != "general" else template.category
            channels = list(payload.channels or template.default_channels)
            return title, body, category, channels
        if not payload.title or not payload.body:
            raise TemplateRenderError("Campaign title and body are required")
        return payload.title, payload.body, payload.category, list(payload.channels or ["IN_APP"])

    def _create_notifications(
        self,
        *,
        recipients: list[ResolvedRecipient],
        campaign: NotificationCampaign | None,
        title: str,
        body: str,
        category: str,
        priority: str,
        channels: list[str],
        data: dict,
        source_service: str | None = None,
        source_event_id: str | None = None,
    ) -> list[uuid.UUID]:
        pending: list[uuid.UUID] = []
        for recipient in recipients:
            preference = self.preferences.get_by_user_id(recipient.user_id)
            if preference is None:
                preference = NotificationPreference(
                    user_id=recipient.user_id,
                    in_app_enabled=settings.DEFAULT_IN_APP_ENABLED,
                    email_enabled=settings.DEFAULT_EMAIL_ENABLED,
                    muted_categories=[],
                )
                self.preferences.add_preference(preference)
                self.db.flush()
            muted = category in set(preference.muted_categories or [])
            in_app_visible = "IN_APP" in channels and preference.in_app_enabled and not muted
            notification = Notification(
                recipient_user_id=recipient.user_id,
                expires_at=campaign.expires_at if campaign else None,
                recipient_email=recipient.email,
                campaign_id=campaign.id if campaign else None,
                category=category,
                priority=priority if priority in {"LOW", "NORMAL", "HIGH", "URGENT"} else "NORMAL",
                title=title,
                body=body,
                data=data,
                source_service=source_service,
                source_event_id=source_event_id,
                in_app_visible=in_app_visible,
            )
            self.notifications.add_notification(notification)
            self.db.flush()
            for channel in sorted(set(channels)):
                if channel == "IN_APP":
                    status = "SENT" if in_app_visible else "SKIPPED"
                    error = (
                        None
                        if in_app_visible
                        else "In-app notifications disabled or category muted"
                    )
                elif channel == "EMAIL":
                    can_email = preference.email_enabled and not muted and bool(recipient.email)
                    status = "PENDING" if can_email else "SKIPPED"
                    error = None if can_email else "Email disabled, muted, or address unavailable"
                else:
                    status, error = "SKIPPED", "Unsupported channel"
                attempt = DeliveryAttempt(
                    notification_id=notification.id,
                    channel=channel,
                    status=status,
                    attempt_number=1,
                    last_error=error,
                )
                self.deliveries.add_attempt(attempt)
                self.db.flush()
                if status == "PENDING":
                    pending.append(attempt.id)
        return pending
