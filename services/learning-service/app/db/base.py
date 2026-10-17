from __future__ import annotations

from app.db.base_class import Base
from app.domain.entities.models import (  # noqa: F401
    FileDeletionTask,
    FileOperationAudit,
    LearningResource,
    OutboxEvent,
    ResourceAccessLog,
    ResourceCategory,
    ResourceTarget,
    ResourceVersion,
)

__all__ = ["Base"]
