from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime

import httpx
from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, NotFoundError
from app.domain.entities.models import (
    FeatureFlag,
    JobRecord,
    OutboxEvent,
    PlatformSetting,
    ServiceHealthCheck,
    ServiceRegistry,
    SupportMessage,
    SupportTicket,
)
from app.repositories.platform_repository import PlatformRepository
from app.schemas.admin import FeatureFlagUpsert, JobCreate, ServiceRegistryCreate, SettingUpsert
from app.schemas.support import MessageCreate, TicketCreate, TicketUpdateAdmin


def utcnow() -> datetime:
    return datetime.now(UTC)


class PlatformService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PlatformRepository(db)

    def _outbox(self, event_type: str, aggregate_type: str, aggregate_id: str, payload: dict):
        self.db.add(
            OutboxEvent(
                event_type=event_type,
                aggregate_type=aggregate_type,
                aggregate_id=aggregate_id,
                payload=payload,
            )
        )

    # Search
    def search(
        self,
        query: str,
        roles: set[str],
        document_type: str | None = None,
        source_service: str | None = None,
        limit: int = 50,
    ):
        rows = self.repo.search_documents(query, document_type, source_service, limit)
        return [
            row
            for row in rows
            if not row.audience_roles
            or bool(roles.intersection({str(r).lower() for r in row.audience_roles}))
        ]

    # Support
    def create_ticket(self, payload: TicketCreate, user_id: uuid.UUID):
        ticket = SupportTicket(
            ticket_number=f"TKT-{secrets.token_hex(5).upper()}",
            created_by_user_id=user_id,
            subject=payload.subject,
            description=payload.description,
            category=payload.category.upper(),
            priority=payload.priority.upper(),
            status="OPEN",
        )
        self.db.add(ticket)
        self.db.flush()
        self._outbox(
            "platform.support_ticket_created",
            "support_ticket",
            str(ticket.id),
            {
                "ticket_id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "created_by_user_id": str(user_id),
                "subject": ticket.subject,
                "priority": ticket.priority,
            },
        )
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def list_tickets(self, user_id: uuid.UUID, is_admin: bool):
        return self.repo.list_tickets(None if is_admin else user_id)

    def get_ticket(self, ticket_id: uuid.UUID, user_id: uuid.UUID, is_admin: bool):
        ticket = self.repo.get_ticket(ticket_id)
        if not ticket:
            raise NotFoundError("Ticket not found")
        if not is_admin and ticket.created_by_user_id != user_id:
            raise ForbiddenError("Ticket belongs to another user")
        return ticket

    def add_message(
        self,
        ticket_id: uuid.UUID,
        payload: MessageCreate,
        user_id: uuid.UUID,
        is_admin: bool,
    ):
        ticket = self.get_ticket(ticket_id, user_id, is_admin)
        if payload.is_internal and not is_admin:
            raise ForbiddenError("Only admins may add internal support notes")
        if ticket.status == "CLOSED" and not is_admin:
            raise ForbiddenError("Closed tickets cannot be updated by requester")
        message = SupportMessage(
            ticket_id=ticket.id,
            author_user_id=user_id,
            body=payload.body,
            is_internal=payload.is_internal,
        )
        self.db.add(message)
        self._outbox(
            "platform.support_message_added",
            "support_ticket",
            str(ticket.id),
            {
                "ticket_id": str(ticket.id),
                "author_user_id": str(user_id),
                "internal": payload.is_internal,
            },
        )
        self.db.commit()
        self.db.refresh(message)
        return message

    def update_ticket_admin(self, ticket_id: uuid.UUID, payload: TicketUpdateAdmin):
        ticket = self.repo.get_ticket(ticket_id)
        if not ticket:
            raise NotFoundError("Ticket not found")
        if payload.status is not None:
            ticket.status = payload.status.upper()
            if ticket.status == "CLOSED":
                ticket.closed_at = utcnow()
            elif ticket.closed_at is not None:
                ticket.closed_at = None
        if payload.priority is not None:
            ticket.priority = payload.priority.upper()
        if payload.assigned_to_user_id is not None:
            ticket.assigned_to_user_id = payload.assigned_to_user_id
        self._outbox(
            "platform.support_ticket_updated",
            "support_ticket",
            str(ticket.id),
            {
                "ticket_id": str(ticket.id),
                "status": ticket.status,
                "priority": ticket.priority,
                "assigned_to_user_id": (
                    str(ticket.assigned_to_user_id) if ticket.assigned_to_user_id else None
                ),
            },
        )
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    # Settings
    def upsert_setting(self, key: str, payload: SettingUpsert, actor_id: uuid.UUID):
        row = self.repo.setting(key)
        if row is None:
            row = PlatformSetting(key=key)
            self.db.add(row)
        row.value = payload.value
        row.is_public = payload.is_public
        row.description = payload.description
        row.updated_by_user_id = actor_id
        self.db.commit()
        self.db.refresh(row)
        return row

    def upsert_feature(self, key: str, payload: FeatureFlagUpsert, actor_id: uuid.UUID):
        row = self.repo.feature(key)
        if row is None:
            row = FeatureFlag(key=key)
            self.db.add(row)
        row.enabled = payload.enabled
        row.config = payload.config
        row.description = payload.description
        row.updated_by_user_id = actor_id
        self.db.commit()
        self.db.refresh(row)
        return row

    # Service registry / health
    def upsert_service(self, payload: ServiceRegistryCreate):
        row = self.repo.service_registry(payload.service_name)
        if row is None:
            row = ServiceRegistry(service_name=payload.service_name)
            self.db.add(row)
        row.base_url = payload.base_url.rstrip("/")
        row.health_path = payload.health_path
        row.ready_path = payload.ready_path
        row.enabled = payload.enabled
        row.critical = payload.critical
        row.timeout_seconds = payload.timeout_seconds
        self.db.commit()
        self.db.refresh(row)
        return row

    def check_services(self, http_client=None):
        client = http_client or httpx.Client()
        results = []
        try:
            for service in self.repo.list_services(enabled_only=True):
                started = datetime.now(UTC)
                health_ok = False
                ready_ok = False
                detail = {}
                try:
                    health = client.get(
                        f"{service.base_url}{service.health_path}",
                        timeout=service.timeout_seconds,
                    )
                    health_ok = health.status_code < 400
                    detail["health_status_code"] = health.status_code
                except Exception as exc:
                    detail["health_error"] = str(exc)

                try:
                    ready = client.get(
                        f"{service.base_url}{service.ready_path}",
                        timeout=service.timeout_seconds,
                    )
                    ready_ok = ready.status_code < 400
                    detail["ready_status_code"] = ready.status_code
                except Exception as exc:
                    detail["ready_error"] = str(exc)

                latency = (datetime.now(UTC) - started).total_seconds() * 1000
                status = "HEALTHY" if health_ok and ready_ok else "DEGRADED"
                check = ServiceHealthCheck(
                    service_name=service.service_name,
                    status=status,
                    health_ok=health_ok,
                    ready_ok=ready_ok,
                    latency_ms=latency,
                    detail=detail,
                )
                self.db.add(check)
                results.append(check)
            self.db.commit()
            return results
        finally:
            if http_client is None:
                client.close()

    # Jobs
    def create_job(self, payload: JobCreate, actor_id: uuid.UUID):
        job = JobRecord(
            job_type=payload.job_type,
            target_service=payload.target_service,
            resource_type=payload.resource_type,
            parameters=payload.parameters,
            payload=payload.payload,
            requested_by_user_id=actor_id,
            status="QUEUED",
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job
