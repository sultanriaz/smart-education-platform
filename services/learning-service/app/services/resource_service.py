from __future__ import annotations
import hashlib

import mimetypes
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.clients.academic import AcademicClient
from app.core.config import settings
from app.core.errors import ConflictError, ForbiddenError, NotFoundError, ValidationDomainError
from app.domain.entities.models import (
    FileDeletionTask,
    FileOperationAudit,
    AccessAction,
    LearningResource,
    OutboxEvent,
    ResourceAccessLog,
    ResourceStatus,
    ResourceTarget,
    ResourceType,
    ResourceVersion,
)
from app.repositories.category_repository import CategoryRepository
from app.repositories.resource_repository import ResourceRepository
from app.schemas.resource import ResourceCreate, ResourceUpdate, VersionCreate
from app.security.auth import Principal
from app.security.uploads import validate_file
from app.storage.base import StorageBackend


def utcnow() -> datetime:
    return datetime.now(UTC)


class ResourceService:
    def __init__(self, db: Session, academic: AcademicClient, storage: StorageBackend):
        self.db = db
        self.academic = academic
        self.storage = storage
        self.repo = ResourceRepository(db)
        self.categories = CategoryRepository(db)

    def _is_admin(self, principal: Principal) -> bool:
        return "admin" in principal.roles

    def _is_teacher(self, principal: Principal) -> bool:
        return "teacher" in principal.roles or "learning.resources.manage" in principal.permissions

    def _ensure_manage_targets(self, principal: Principal, targets) -> None:
        if self._is_admin(principal):
            return
        if not self._is_teacher(principal):
            raise ForbiddenError("Only teachers and admins can manage learning resources")
        for target in targets:
            if not self.academic.actor_can_manage_target(
                principal.user_id, "teacher", target.target_type, target.target_id
            ):
                raise ForbiddenError("Teacher is not assigned to one or more selected targets")

    def _ensure_owner_or_admin(self, principal: Principal, resource: LearningResource) -> None:
        if self._is_admin(principal):
            return
        if resource.creator_user_id != principal.user_id:
            raise ForbiddenError("Resource may only be modified by its creator or an admin")

    def _get_or_404(self, resource_id: uuid.UUID, *, for_update: bool = False) -> LearningResource:
        resource = self.repo.get_resource(resource_id, for_update=for_update)
        if resource is None:
            raise NotFoundError("Learning resource not found")
        return resource

    def create_resource(self, principal: Principal, payload: ResourceCreate) -> LearningResource:
        self._ensure_manage_targets(principal, payload.targets)
        if payload.category_id and not self.categories.get_by_id(payload.category_id):
            raise ValidationDomainError("Category does not exist")
        resource = LearningResource(
            title=payload.title.strip(),
            description=payload.description,
            resource_type=payload.resource_type,
            category_id=payload.category_id,
            creator_user_id=principal.user_id,
            tags=sorted({x.strip().lower() for x in payload.tags if x.strip()}),
        )
        resource.targets = [
            ResourceTarget(target_type=t.target_type, target_id=t.target_id)
            for t in payload.targets
        ]
        try:
            self.repo.add_resource(resource)
            self.repo.add_outbox(
                OutboxEvent(
                    event_type="learning.resource_created",
                    aggregate_type="learning_resource",
                    aggregate_id=resource.id,
                    payload={"resource_id": str(resource.id), "title": resource.title},
                )
            )
            self.db.commit()
            return self.repo.get_resource(resource.id)
        except Exception:
            self.db.rollback()
            raise

    def update_resource(
        self, principal: Principal, resource_id: uuid.UUID, payload: ResourceUpdate
    ) -> LearningResource:
        resource = self._get_or_404(resource_id, for_update=True)
        self._ensure_owner_or_admin(principal, resource)
        if resource.status == ResourceStatus.ARCHIVED:
            raise ConflictError("Archived resources cannot be edited")
        if payload.targets is not None:
            self._ensure_manage_targets(principal, payload.targets)
        if payload.category_id is not None and not self.categories.get_by_id(payload.category_id):
            raise ValidationDomainError("Category does not exist")
        if payload.title is not None:
            resource.title = payload.title.strip()
        if payload.description is not None:
            resource.description = payload.description
        if payload.category_id is not None:
            resource.category_id = payload.category_id
        if payload.tags is not None:
            resource.tags = sorted({x.strip().lower() for x in payload.tags if x.strip()})
        if payload.targets is not None:
            resource.targets = [
                ResourceTarget(target_type=t.target_type, target_id=t.target_id)
                for t in payload.targets
            ]
        try:
            self.db.commit()
            return self.repo.get_resource(resource.id)
        except Exception:
            self.db.rollback()
            raise

    def add_content_version(
        self,
        principal: Principal,
        resource_id: uuid.UUID,
        payload: VersionCreate,
    ) -> ResourceVersion:
        resource = self._get_or_404(resource_id, for_update=True)
        self._ensure_owner_or_admin(principal, resource)
        if resource.status == ResourceStatus.ARCHIVED:
            raise ConflictError("Archived resources cannot receive new versions")
        external_url = str(payload.external_url) if payload.external_url else None
        if resource.resource_type == ResourceType.FILE:
            raise ValidationDomainError("FILE resources require the upload endpoint")
        if resource.resource_type == ResourceType.NOTE and not payload.text_content:
            raise ValidationDomainError("NOTE resources require text_content")
        if resource.resource_type in {ResourceType.LINK, ResourceType.VIDEO} and not external_url:
            raise ValidationDomainError("LINK/VIDEO resources require external_url")
        version = ResourceVersion(
            resource_id=resource.id,
            version_number=self.repo.next_version_number(resource.id),
            created_by_user_id=principal.user_id,
            text_content=payload.text_content,
            external_url=external_url,
            change_note=payload.change_note,
        )
        try:
            self.repo.add_version(version)
            self.db.commit()
            self.db.refresh(version)
            return version
        except Exception:
            self.db.rollback()
            raise

    def add_file_version(
        self,
        principal: Principal,
        resource_id: uuid.UUID,
        filename: str,
        mime_type: str,
        data: bytes,
        change_note: str | None = None,
    ) -> ResourceVersion:
        resource = self._get_or_404(resource_id, for_update=True)
        self._ensure_owner_or_admin(principal, resource)
        if resource.resource_type != ResourceType.FILE:
            raise ValidationDomainError("Only FILE resources accept uploads")
        if resource.status == ResourceStatus.ARCHIVED:
            raise ConflictError("Archived resources cannot receive new versions")
        if len(data) > settings.MAX_UPLOAD_BYTES:
            raise ValidationDomainError("Uploaded file exceeds MAX_UPLOAD_BYTES")
        resolved_mime = mime_type or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        if (
            settings.ALLOWED_UPLOAD_MIME_TYPES
            and resolved_mime not in settings.ALLOWED_UPLOAD_MIME_TYPES
        ):
            raise ValidationDomainError("Uploaded file type is not allowed")
        version_no = self.repo.next_version_number(resource.id)
        safe_name = validate_file(filename, resolved_mime, data)
        key = f"resources/{resource.id}/v{version_no}/{uuid.uuid4().hex}-{safe_name}"
        stored = self.storage.put_bytes(key, data, resolved_mime)
        version = ResourceVersion(
            resource_id=resource.id,
            version_number=version_no,
            created_by_user_id=principal.user_id,
            storage_key=stored.key,
            original_filename=safe_name,
            mime_type=stored.mime_type,
            size_bytes=stored.size_bytes,
            checksum_sha256=stored.checksum_sha256,
            change_note=change_note,
        )
        try:
            self.repo.add_version(version)
            self.db.flush()
            self.db.add(FileOperationAudit(resource_id=resource.id, version_id=version.id,
                actor_user_id=principal.user_id, operation="UPLOAD", checksum_sha256=stored.checksum_sha256))
            self.db.commit()
            self.db.refresh(version)
            return version
        except Exception:
            self.db.rollback()
            try:
                self.storage.delete(stored.key)
            except Exception:
                pass
            raise

    def publish(self, principal: Principal, resource_id: uuid.UUID) -> LearningResource:
        resource = self._get_or_404(resource_id, for_update=True)
        self._ensure_owner_or_admin(principal, resource)
        if resource.status == ResourceStatus.ARCHIVED:
            raise ConflictError("Archived resources cannot be published")
        if not resource.targets:
            raise ValidationDomainError("Resource requires at least one academic target")
        if not resource.versions:
            raise ValidationDomainError("Resource requires at least one content version")
        resource.status = ResourceStatus.PUBLISHED
        resource.published_at = utcnow()
        event = OutboxEvent(
            event_type="learning.resource_published",
            aggregate_type="learning_resource",
            aggregate_id=resource.id,
            payload={
                "resource_id": str(resource.id),
                "title": resource.title,
                "targets": [
                    {"type": t.target_type.value, "id": str(t.target_id)} for t in resource.targets
                ],
                "creator_user_id": str(resource.creator_user_id),
            },
        )
        try:
            self.repo.add_outbox(event)
            self.db.commit()
            return self.repo.get_resource(resource.id)
        except Exception:
            self.db.rollback()
            raise

    def archive(self, principal: Principal, resource_id: uuid.UUID) -> LearningResource:
        resource = self._get_or_404(resource_id, for_update=True)
        self._ensure_owner_or_admin(principal, resource)
        resource.status = ResourceStatus.ARCHIVED
        resource.archived_at = utcnow()
        try:
            self.db.commit()
            return self.repo.get_resource(resource.id)
        except Exception:
            self.db.rollback()
            raise

    def _student_allowed(self, principal: Principal, resource: LearningResource) -> bool:
        if resource.status != ResourceStatus.PUBLISHED:
            return False
        return any(
            self.academic.student_can_access_target(principal.user_id, t.target_type, t.target_id)
            for t in resource.targets
        )

    def get_resource_for_actor(
        self, principal: Principal, resource_id: uuid.UUID
    ) -> LearningResource:
        resource = self._get_or_404(resource_id)
        if self._is_admin(principal):
            return resource
        if self._is_teacher(principal) and resource.creator_user_id == principal.user_id:
            return resource
        if "student" in principal.roles and self._student_allowed(principal, resource):
            self.record_access(principal.user_id, resource.id, AccessAction.VIEW)
            return resource
        if self._is_teacher(principal):
            for target in resource.targets:
                if self.academic.actor_can_manage_target(
                    principal.user_id, "teacher", target.target_type, target.target_id
                ):
                    return resource
        raise ForbiddenError("You do not have access to this resource")

    def record_access(
        self, user_id: uuid.UUID, resource_id: uuid.UUID, action: AccessAction
    ) -> None:
        try:
            self.repo.add_access(
                ResourceAccessLog(user_id=user_id, resource_id=resource_id, action=action)
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def download_latest(self, principal: Principal, resource_id: uuid.UUID):
        resource = self.get_resource_for_actor(principal, resource_id)
        if resource.resource_type != ResourceType.FILE:
            raise ValidationDomainError("Resource is not a downloadable file")
        if not resource.versions:
            raise NotFoundError("Resource has no content versions")
        version = max(resource.versions, key=lambda x: x.version_number)
        if not version.storage_key:
            raise NotFoundError("Latest resource version has no stored file")
        data = self.storage.get_bytes(version.storage_key)
        # Never deliver or advertise corrupt storage bytes as a verified download.
        digest = hashlib.sha256(data).hexdigest()
        if not version.checksum_sha256 or not __import__("hmac").compare_digest(
            digest, version.checksum_sha256.lower()
        ):
            raise ConflictError("Stored file failed SHA-256 integrity verification")
        self.db.add(FileOperationAudit(resource_id=resource.id, version_id=version.id,
            actor_user_id=principal.user_id, operation="DOWNLOAD", checksum_sha256=digest))
        self.record_access(principal.user_id, resource.id, AccessAction.DOWNLOAD)
        return version, data

    def list_student_resources(self, principal: Principal, offset: int, limit: int):
        targets = self.academic.get_student_accessible_targets(principal.user_id)
        return self.repo.list_published_for_targets(
            targets.section_ids, targets.course_ids, offset=offset, limit=limit
        )

    def student_history(self, principal: Principal, *, offset: int, limit: int):
        return self.repo.access_history(principal.user_id, offset=offset, limit=limit)

    def recommendations(self, principal: Principal, limit: int = 20):
        targets = self.academic.get_student_accessible_targets(principal.user_id)
        resources = self.repo.list_published_for_targets(
            targets.section_ids, targets.course_ids, offset=0, limit=max(limit * 5, 100)
        )
        accessed = self.repo.accessed_resource_ids(principal.user_id)
        affinity = self.repo.accessed_tag_affinity(principal.user_id)
        cutoff = utcnow() - timedelta(days=settings.RECOMMENDATION_RECENT_DAYS)
        scored = []
        for resource in resources:
            score = 0
            reasons = []
            if resource.id not in accessed:
                score += 100
                reasons.append("not viewed yet")
            published_at = resource.published_at
            if published_at and published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=UTC)
            if published_at and published_at >= cutoff:
                score += 20
                reasons.append("recently published")
            score += min(len(resource.tags), 10)
            matched = sorted(set(resource.tags or []) & set(affinity))
            if matched:
                score += min(sum(affinity[t] for t in matched), 10) * 3
                reasons.append("matches your recently accessed topics: " + ", ".join(matched[:3]))
            elif resource.tags:
                reasons.append("tagged learning material")
            scored.append((score, resource, ", ".join(reasons) or "available for your enrollment"))

        def _ts(resource):
            value = resource.published_at or resource.created_at
            if value.tzinfo is None:
                value = value.replace(tzinfo=UTC)
            return value.timestamp()

        scored.sort(key=lambda item: (-item[0], -_ts(item[1])))
        return scored[:limit]


    def delete_file_version(self, principal: Principal, resource_id: uuid.UUID,
                            version_id: uuid.UUID) -> None:
        """Never erase a published file or remove bytes before durable scheduling."""
        resource = self._get_or_404(resource_id, for_update=True)
        self._ensure_owner_or_admin(principal, resource)
        if resource.resource_type != ResourceType.FILE:
            raise ValidationDomainError("Only FILE resources have stored file versions")
        if resource.status == ResourceStatus.PUBLISHED:
            raise ConflictError("Archive the published resource before deleting files")
        version = next((v for v in resource.versions if v.id == version_id), None)
        if version is None:
            raise NotFoundError("Resource version not found")
        key = version.storage_key
        if not key:
            raise ValidationDomainError("Version has no stored file")
        try:
            # The deletion task and version removal commit atomically.
            self.db.add(FileDeletionTask(storage_key=key, resource_id=resource.id,
                                         actor_user_id=principal.user_id))
            self.db.add(FileOperationAudit(resource_id=resource.id, version_id=version.id,
                actor_user_id=principal.user_id, operation="DELETE_SCHEDULED",
                checksum_sha256=version.checksum_sha256))
            self.db.delete(version)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
