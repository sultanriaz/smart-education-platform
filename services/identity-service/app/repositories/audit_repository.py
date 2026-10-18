import uuid
from datetime import datetime
from sqlalchemy import select

from sqlalchemy.orm import Session

from app.domain.entities.audit import SecurityAuditEvent

SENSITIVE = {"password", "password_hash", "access_token", "refresh_token", "token", "cookie", "secret", "authorization", "reset_token"}

def sanitize_metadata(value, depth=0):
    if depth > 12: return "[REDACTED]"
    if isinstance(value, dict): return {str(k)[:128]: ("[REDACTED]" if any(part in str(k).lower() for part in SENSITIVE) else sanitize_metadata(v, depth+1)) for k,v in list(value.items())[:500]}
    if isinstance(value, list): return [sanitize_metadata(x,depth+1) for x in value[:500]]
    if isinstance(value,str): return value[:2000].replace("\r"," ").replace("\n"," ")
    return value if isinstance(value,(int,float,bool)) or value is None else "[REDACTED]"



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
        outcome: str | None = None,
        request_id: str | None = None,
        correlation_id: str | None = None,
        trace_id: str | None = None,
    ) -> None:
        self.db.add(
            SecurityAuditEvent(
                action=action, user_id=user_id, ip_address=ip_address,
                details=sanitize_metadata(details or {}), outcome=outcome or ("FAILED" if action.endswith("_failed") else "SUCCEEDED"),
                request_id=request_id, correlation_id=correlation_id, trace_id=trace_id,
            )
        )
        self.db.flush()

    def history(self, *, user_id: uuid.UUID | None = None, action: str | None = None, outcome: str | None = None, from_date: datetime | None = None, to_date: datetime | None = None, limit: int = 50, offset: int = 0):
        stmt = select(SecurityAuditEvent)
        if user_id is not None: stmt = stmt.where(SecurityAuditEvent.user_id == user_id)
        if action: stmt = stmt.where(SecurityAuditEvent.action == action)
        if outcome: stmt = stmt.where(SecurityAuditEvent.outcome == outcome)
        if from_date: stmt = stmt.where(SecurityAuditEvent.created_at >= from_date)
        if to_date: stmt = stmt.where(SecurityAuditEvent.created_at <= to_date)
        return list(self.db.scalars(stmt.order_by(SecurityAuditEvent.created_at.desc(), SecurityAuditEvent.id.desc()).limit(min(limit, 100)).offset(offset)).all())
