from __future__ import annotations

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.entities.models import AuditEntry, InternalEvent, SearchDocument
from app.repositories.platform_repository import PlatformRepository
from app.schemas.events import InternalEventIn


_SENSITIVE_FIELDS = {"password", "password_hash", "token", "access_token", "refresh_token", "secret", "api_key", "authorization", "cookie", "private_key", "credential", "credentials"}

def redact_audit_metadata(value, *, depth: int = 0):
    """Fail-closed bounded redaction before persisting central audit metadata."""
    if depth > 12:
        return "[REDACTED: nested data]"
    if isinstance(value, dict):
        return {str(k): ("[REDACTED]" if any(part in str(k).lower() for part in _SENSITIVE_FIELDS)
            else redact_audit_metadata(v, depth=depth + 1)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_audit_metadata(v, depth=depth + 1) for v in value[:500]]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return "[REDACTED: unsupported type]"


class EventIngestionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PlatformRepository(db)

    def ingest(self, payload: InternalEventIn) -> str:
        if self.repo.event_by_id(payload.event_id):
            return "duplicate"

        event = InternalEvent(
            event_id=payload.event_id,
            source_service=payload.source_service,
            event_type=payload.event_type,
            payload=redact_audit_metadata(payload.payload),
            occurred_at=payload.effective_occurred_at(),
        )
        self.db.add(event)

        self._project_audit(payload)
        self._project_search(payload)

        try:
            self.db.commit()
            return "processed"
        except IntegrityError:
            self.db.rollback()
            if self.repo.event_by_id(payload.event_id):
                return "duplicate"
            raise

    def _project_audit(self, event: InternalEventIn) -> None:
        data = event.payload.get("audit")
        if not isinstance(data, dict):
            if not event.event_type.startswith("audit."):
                return
            data = event.payload

        actor = data.get("actor_user_id")
        actor_id = uuid.UUID(str(actor)) if actor else None

        self.db.add(
            AuditEntry(
                source_service=event.source_service,
                actor_user_id=actor_id,
                action=str(data.get("action") or event.event_type),
                entity_type=data.get("entity_type"),
                entity_id=str(data["entity_id"]) if data.get("entity_id") is not None else None,
                correlation_id=data.get("correlation_id"),
                metadata_json=redact_audit_metadata(data.get("metadata", {})),
                occurred_at=event.effective_occurred_at(),
            )
        )

    def _project_search(self, event: InternalEventIn) -> None:
        data = event.payload.get("search_document")

        if event.event_type == "platform.search.delete":
            data = data or event.payload
            if not isinstance(data, dict):
                return
            document_type = str(data.get("document_type") or "")
            document_id = str(data.get("document_id") or "")
            if not document_type or not document_id:
                return
            row = self.repo.search_document(event.source_service, document_type, document_id)
            if row:
                row.is_active = False
            return

        if event.event_type != "platform.search.upsert" and not isinstance(data, dict):
            return

        data = data or event.payload
        document_type = str(data.get("document_type") or "")
        document_id = str(data.get("document_id") or "")
        title = str(data.get("title") or "")

        if not document_type or not document_id or not title:
            return

        row = self.repo.search_document(event.source_service, document_type, document_id)
        values = {
            "title": title,
            "body": str(data.get("body") or ""),
            "url_path": data.get("url_path"),
            "metadata_json": redact_audit_metadata(data.get("metadata", {})),
            "audience_roles": data.get("audience_roles") or (["student", "teacher", "admin"] if document_type == "announcement" and not data.get("metadata") else ["admin"]),
            "is_active": bool(data.get("is_active", True)),
        }

        if row is None:
            row = SearchDocument(
                source_service=event.source_service,
                document_type=document_type,
                document_id=document_id,
                **values,
            )
            self.db.add(row)
        else:
            for key, value in values.items():
                setattr(row, key, value)
