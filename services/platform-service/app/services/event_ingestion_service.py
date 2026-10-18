from __future__ import annotations

import uuid

from app.services.governance import digest_json

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.entities.models import AuditEntry, InternalEvent, SearchDocument, SearchIndexRevision, utcnow
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
                event_id=event.event_id,
                outcome=str(data.get("outcome") or "SUCCEEDED")[:32],
                request_id=str(data["request_id"])[:128] if data.get("request_id") else None,
                trace_id=str(data["trace_id"])[:64] if data.get("trace_id") else None,
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
            if row and row.is_active:
                row.is_active = False
                row.deindexed_at = utcnow()
                row.acl_version = (row.acl_version or 0) + 1
                self.db.add(SearchIndexRevision(search_document_id=row.id, acl_version=row.acl_version, audience=[], content_hash=row.content_hash or "", deindexed_at=row.deindexed_at))
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

        hash_value = digest_json(values)
        if row is None:
            row = SearchDocument(
                source_service=event.source_service,
                document_type=document_type,
                document_id=document_id,
                **values,
            )
            row.content_hash = hash_value
            self.db.add(row)
        else:
            if row.content_hash == hash_value and row.is_active == values["is_active"]:
                return
            row.acl_version = (row.acl_version or 0) + 1
            row.content_hash = hash_value
            row.deindexed_at = None if values["is_active"] else utcnow()
            for key, value in values.items():
                setattr(row, key, value)
        self.db.flush()
        self.db.add(SearchIndexRevision(search_document_id=row.id, acl_version=row.acl_version, audience=row.audience_roles, content_hash=hash_value, deindexed_at=row.deindexed_at))
