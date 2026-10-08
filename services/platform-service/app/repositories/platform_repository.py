from __future__ import annotations

import uuid

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.domain.entities.models import (
    AuditEntry,
    FeatureFlag,
    InternalEvent,
    JobRecord,
    PlatformSetting,
    SearchDocument,
    ServiceRegistry,
    SupportTicket,
)


class PlatformRepository:
    def __init__(self, db: Session):
        self.db = db

    def event_by_id(self, event_id: uuid.UUID):
        return self.db.scalar(select(InternalEvent).where(InternalEvent.event_id == event_id))

    def search_document(self, source_service: str, document_type: str, document_id: str):
        return self.db.scalar(
            select(SearchDocument).where(
                SearchDocument.source_service == source_service,
                SearchDocument.document_type == document_type,
                SearchDocument.document_id == document_id,
            )
        )

    def search_documents(
        self,
        query: str,
        document_type: str | None = None,
        source_service: str | None = None,
        limit: int = 50,
    ):
        stmt = select(SearchDocument).where(SearchDocument.is_active.is_(True))
        if query:
            token = f"%{query}%"
            stmt = stmt.where(
                or_(
                    SearchDocument.title.ilike(token),
                    SearchDocument.body.ilike(token),
                )
            )
        if document_type:
            stmt = stmt.where(SearchDocument.document_type == document_type)
        if source_service:
            stmt = stmt.where(SearchDocument.source_service == source_service)
        stmt = stmt.order_by(SearchDocument.updated_at.desc()).limit(limit)
        return list(self.db.scalars(stmt).all())

    def get_ticket(self, ticket_id: uuid.UUID):
        stmt = (
            select(SupportTicket)
            .options(selectinload(SupportTicket.messages))
            .where(SupportTicket.id == ticket_id)
        )
        return self.db.scalar(stmt)

    def list_tickets(self, user_id: uuid.UUID | None = None):
        stmt = select(SupportTicket).order_by(SupportTicket.updated_at.desc())
        if user_id:
            stmt = stmt.where(SupportTicket.created_by_user_id == user_id)
        return list(self.db.scalars(stmt).all())

    def setting(self, key: str):
        return self.db.scalar(select(PlatformSetting).where(PlatformSetting.key == key))

    def list_settings(self, public_only: bool = False):
        stmt = select(PlatformSetting).order_by(PlatformSetting.key)
        if public_only:
            stmt = stmt.where(PlatformSetting.is_public.is_(True))
        return list(self.db.scalars(stmt).all())

    def feature(self, key: str):
        return self.db.scalar(select(FeatureFlag).where(FeatureFlag.key == key))

    def list_features(self):
        return list(self.db.scalars(select(FeatureFlag).order_by(FeatureFlag.key)).all())

    def service_registry(self, service_name: str):
        return self.db.scalar(
            select(ServiceRegistry).where(ServiceRegistry.service_name == service_name)
        )

    def list_services(self, enabled_only: bool = False):
        stmt = select(ServiceRegistry).order_by(ServiceRegistry.service_name)
        if enabled_only:
            stmt = stmt.where(ServiceRegistry.enabled.is_(True))
        return list(self.db.scalars(stmt).all())

    def get_job(self, job_id: uuid.UUID):
        return self.db.get(JobRecord, job_id)

    def list_jobs(self, limit: int = 100):
        return list(
            self.db.scalars(
                select(JobRecord).order_by(JobRecord.created_at.desc()).limit(limit)
            ).all()
        )

    def list_audit(self, limit: int = 100):
        return list(
            self.db.scalars(
                select(AuditEntry).order_by(AuditEntry.occurred_at.desc()).limit(limit)
            ).all()
        )
