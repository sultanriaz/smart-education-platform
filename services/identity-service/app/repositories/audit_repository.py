import uuid

from sqlalchemy.orm import Session

from app.domain.entities.audit import SecurityAuditEvent


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def record(
        self,
        *,
        action: str,
        user_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        details: dict | None = None,
    ) -> None:
        self.db.add(
            SecurityAuditEvent(
                action=action, user_id=user_id, ip_address=ip_address, details=details or {}
            )
        )
        self.db.flush()
