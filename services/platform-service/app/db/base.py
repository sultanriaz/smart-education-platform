from __future__ import annotations

from app.db.base_class import Base
from app.domain.entities.models import (  # noqa: F401
    AuditEntry,
    FeatureFlag,
    InternalEvent,
    JobRecord,
    OutboxEvent,
    PlatformSetting,
    SearchDocument,
    ServiceHealthCheck,
    ServiceRegistry,
    SupportMessage,
    SupportTicket,
)

__all__ = ["Base"]
