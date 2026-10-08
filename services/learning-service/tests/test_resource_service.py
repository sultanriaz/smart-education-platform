from __future__ import annotations

import pytest

from app.core.errors import ForbiddenError, ValidationDomainError
from app.domain.entities.models import ResourceStatus, ResourceType, TargetType
from app.schemas.resource import ResourceCreate, TargetInput, VersionCreate
from app.security.auth import Principal
from app.services.resource_service import ResourceService
from tests.conftest import ADMIN_ID, OTHER_SECTION_ID, SECTION_ID, STUDENT_ID, TEACHER_ID


def teacher():
    return Principal(TEACHER_ID, frozenset({"teacher"}), "x")


def student():
    return Principal(STUDENT_ID, frozenset({"student"}), "x")


def admin():
    return Principal(ADMIN_ID, frozenset({"admin"}), "x")


def note_payload(target_id=SECTION_ID):
    return ResourceCreate(
        title="Week 1 Notes",
        description="Intro",
        resource_type=ResourceType.NOTE,
        targets=[TargetInput(target_type=TargetType.SECTION, target_id=target_id)],
        tags=["Python", "python", "intro"],
    )


def test_teacher_can_create_for_assigned_section(db, academic, storage):
    service = ResourceService(db, academic, storage)
    resource = service.create_resource(teacher(), note_payload())
    assert resource.creator_user_id == TEACHER_ID
    assert resource.status == ResourceStatus.DRAFT
    assert resource.tags == ["intro", "python"]


def test_teacher_cannot_create_for_unassigned_section(db, academic, storage):
    service = ResourceService(db, academic, storage)
    with pytest.raises(ForbiddenError):
        service.create_resource(teacher(), note_payload(OTHER_SECTION_ID))


def test_note_requires_content(db, academic, storage):
    service = ResourceService(db, academic, storage)
    resource = service.create_resource(teacher(), note_payload())
    with pytest.raises(ValidationDomainError):
        service.add_content_version(teacher(), resource.id, VersionCreate())


def test_publish_requires_version(db, academic, storage):
    service = ResourceService(db, academic, storage)
    resource = service.create_resource(teacher(), note_payload())
    with pytest.raises(ValidationDomainError):
        service.publish(teacher(), resource.id)


def test_publish_and_student_access(db, academic, storage):
    service = ResourceService(db, academic, storage)
    resource = service.create_resource(teacher(), note_payload())
    service.add_content_version(
        teacher(), resource.id, VersionCreate(text_content="Hello learners")
    )
    resource = service.publish(teacher(), resource.id)
    assert resource.status == ResourceStatus.PUBLISHED
    visible = service.get_resource_for_actor(student(), resource.id)
    assert visible.id == resource.id


def test_student_recommendations_prioritize_unread(db, academic, storage):
    service = ResourceService(db, academic, storage)
    resource = service.create_resource(teacher(), note_payload())
    service.add_content_version(
        teacher(), resource.id, VersionCreate(text_content="Hello learners")
    )
    service.publish(teacher(), resource.id)
    recs = service.recommendations(student())
    assert recs[0][0] >= 100
    assert "not viewed yet" in recs[0][2]


def test_file_upload_and_download(db, academic, storage):
    service = ResourceService(db, academic, storage)
    payload = ResourceCreate(
        title="Slides",
        resource_type=ResourceType.FILE,
        targets=[TargetInput(target_type=TargetType.SECTION, target_id=SECTION_ID)],
    )
    resource = service.create_resource(teacher(), payload)
    version = service.add_file_version(
        teacher(), resource.id, "slides.pdf", "application/pdf", b"%PDF-demo"
    )
    assert version.size_bytes == len(b"%PDF-demo")
    service.publish(teacher(), resource.id)
    version2, data = service.download_latest(student(), resource.id)
    assert data == b"%PDF-demo"
    assert version2.original_filename == "slides.pdf"
