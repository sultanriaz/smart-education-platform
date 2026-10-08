from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import NotFoundError, TemplateRenderError
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
from app.schemas.notification import CampaignCreate
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
        recipients = self.resolver.resolve(payload.target, forwarded_token)
        title, body, category, channels = self._content(payload)
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
