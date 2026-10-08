from __future__ import annotations

import uuid

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.domain.entities.models import (
    LearningResource,
    OutboxEvent,
    ResourceAccessLog,
    ResourceStatus,
    ResourceTarget,
    ResourceVersion,
    TargetType,
)


class ResourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def _base(self):
        return (
            select(LearningResource)
            .execution_options(populate_existing=True)
            .options(
                selectinload(LearningResource.targets),
                selectinload(LearningResource.versions),
                selectinload(LearningResource.category),
            )
        )

    def get_resource(
        self, resource_id: uuid.UUID, *, for_update: bool = False
    ) -> LearningResource | None:
        stmt = self._base().where(LearningResource.id == resource_id)
        if for_update:
            stmt = stmt.with_for_update()
        return self.db.scalar(stmt)

    def list_resources(self, offset: int, limit: int) -> list[LearningResource]:
        stmt = self._base().order_by(LearningResource.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).unique().all())

    def list_creator_resources(
        self, user_id: uuid.UUID, offset: int, limit: int
    ) -> list[LearningResource]:
        stmt = (
            self._base()
            .where(LearningResource.creator_user_id == user_id)
            .order_by(LearningResource.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).unique().all())

    def list_published_for_targets(
        self,
        section_ids: set[uuid.UUID],
        course_ids: set[uuid.UUID],
        offset: int = 0,
        limit: int = 100,
    ) -> list[LearningResource]:
        conditions = []
        if section_ids:
            conditions.append(
                and_(
                    ResourceTarget.target_type == TargetType.SECTION,
                    ResourceTarget.target_id.in_(section_ids),
                )
            )
        if course_ids:
            conditions.append(
                and_(
                    ResourceTarget.target_type == TargetType.COURSE,
                    ResourceTarget.target_id.in_(course_ids),
                )
            )
        if not conditions:
            return []
        stmt = (
            self._base()
            .where(
                LearningResource.status == ResourceStatus.PUBLISHED,
                LearningResource.id.in_(select(ResourceTarget.resource_id).where(or_(*conditions))),
            )
            .order_by(LearningResource.published_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).unique().all())

    def add_resource(self, resource: LearningResource) -> LearningResource:
        self.db.add(resource)
        self.db.flush()
        return resource

    def next_version_number(self, resource_id: uuid.UUID) -> int:
        value = self.db.scalar(
            select(func.max(ResourceVersion.version_number)).where(
                ResourceVersion.resource_id == resource_id
            )
        )
        return int(value or 0) + 1

    def add_version(self, version: ResourceVersion) -> ResourceVersion:
        self.db.add(version)
        self.db.flush()
        return version

    def add_access(self, log: ResourceAccessLog) -> None:
        self.db.add(log)
        self.db.flush()

    def accessed_resource_ids(self, user_id: uuid.UUID) -> set[uuid.UUID]:
        rows = self.db.scalars(
            select(ResourceAccessLog.resource_id).where(ResourceAccessLog.user_id == user_id)
        ).all()
        return set(rows)

    def add_outbox(self, event: OutboxEvent) -> None:
        self.db.add(event)
        self.db.flush()

    def list_unpublished_outbox(self, limit: int) -> list[OutboxEvent]:
        stmt = (
            select(OutboxEvent)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return list(self.db.scalars(stmt).all())
