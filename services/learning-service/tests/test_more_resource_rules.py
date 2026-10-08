from __future__ import annotations

import uuid

import pytest

from app.core.errors import ConflictError, ForbiddenError, ValidationDomainError
from app.domain.entities.models import ResourceStatus, ResourceType, TargetType
from app.schemas.resource import ResourceCreate, ResourceUpdate, TargetInput, VersionCreate
from app.security.auth import Principal
from app.services.resource_service import ResourceService
from tests.conftest import ADMIN_ID, COURSE_ID, OTHER_SECTION_ID, SECTION_ID, STUDENT_ID, TEACHER_ID


def principal(user_id, *roles):
    return Principal(user_id, frozenset(roles), "x")


def create_note(service, actor):
    return service.create_resource(
        actor,
        ResourceCreate(
            title="Notes",
            resource_type=ResourceType.NOTE,
            targets=[TargetInput(target_type=TargetType.SECTION, target_id=SECTION_ID)],
        ),
    )


def test_admin_can_create_without_teacher_assignment(db, academic, storage):
    service = ResourceService(db, academic, storage)
    resource = service.create_resource(
        principal(ADMIN_ID, "admin"),
        ResourceCreate(
            title="Admin material",
            resource_type=ResourceType.NOTE,
            targets=[TargetInput(target_type=TargetType.SECTION, target_id=OTHER_SECTION_ID)],
        ),
    )
    assert resource.creator_user_id == ADMIN_ID


def test_student_cannot_create_resource(db, academic, storage):
    service = ResourceService(db, academic, storage)
    with pytest.raises(ForbiddenError):
        create_note(service, principal(STUDENT_ID, "student"))


def test_non_owner_teacher_cannot_update(db, academic, storage):
    service = ResourceService(db, academic, storage)
    resource = create_note(service, principal(TEACHER_ID, "teacher"))
    other_teacher = principal(uuid.uuid4(), "teacher")
    with pytest.raises(ForbiddenError):
        service.update_resource(other_teacher, resource.id, ResourceUpdate(title="Nope"))


def test_admin_can_update_teacher_resource(db, academic, storage):
    service = ResourceService(db, academic, storage)
    resource = create_note(service, principal(TEACHER_ID, "teacher"))
    updated = service.update_resource(
        principal(ADMIN_ID, "admin"), resource.id, ResourceUpdate(title="Admin updated")
    )
    assert updated.title == "Admin updated"


def test_link_requires_external_url(db, academic, storage):
    service = ResourceService(db, academic, storage)
    actor = principal(TEACHER_ID, "teacher")
    resource = service.create_resource(
        actor,
        ResourceCreate(
            title="Reference",
            resource_type=ResourceType.LINK,
            targets=[TargetInput(target_type=TargetType.COURSE, target_id=COURSE_ID)],
        ),
    )
    with pytest.raises(ValidationDomainError):
        service.add_content_version(actor, resource.id, VersionCreate())


def test_versions_increment(db, academic, storage):
    service = ResourceService(db, academic, storage)
    actor = principal(TEACHER_ID, "teacher")
    resource = create_note(service, actor)
    first = service.add_content_version(actor, resource.id, VersionCreate(text_content="one"))
    second = service.add_content_version(actor, resource.id, VersionCreate(text_content="two"))
    assert (first.version_number, second.version_number) == (1, 2)


def test_archive_blocks_new_versions(db, academic, storage):
    service = ResourceService(db, academic, storage)
    actor = principal(TEACHER_ID, "teacher")
    resource = create_note(service, actor)
    service.add_content_version(actor, resource.id, VersionCreate(text_content="one"))
    archived = service.archive(actor, resource.id)
    assert archived.status == ResourceStatus.ARCHIVED
    with pytest.raises(ConflictError):
        service.add_content_version(actor, resource.id, VersionCreate(text_content="two"))


def test_student_cannot_access_draft(db, academic, storage):
    service = ResourceService(db, academic, storage)
    resource = create_note(service, principal(TEACHER_ID, "teacher"))
    with pytest.raises(ForbiddenError):
        service.get_resource_for_actor(principal(STUDENT_ID, "student"), resource.id)


def test_student_cannot_access_unrelated_target(db, academic, storage):
    service = ResourceService(db, academic, storage)
    admin = principal(ADMIN_ID, "admin")
    resource = service.create_resource(
        admin,
        ResourceCreate(
            title="Other section",
            resource_type=ResourceType.NOTE,
            targets=[TargetInput(target_type=TargetType.SECTION, target_id=OTHER_SECTION_ID)],
        ),
    )
    service.add_content_version(admin, resource.id, VersionCreate(text_content="hidden"))
    service.publish(admin, resource.id)
    with pytest.raises(ForbiddenError):
        service.get_resource_for_actor(principal(STUDENT_ID, "student"), resource.id)


def test_disallowed_mime_type_rejected(db, academic, storage):
    service = ResourceService(db, academic, storage)
    actor = principal(TEACHER_ID, "teacher")
    resource = service.create_resource(
        actor,
        ResourceCreate(
            title="Binary",
            resource_type=ResourceType.FILE,
            targets=[TargetInput(target_type=TargetType.SECTION, target_id=SECTION_ID)],
        ),
    )
    with pytest.raises(ValidationDomainError):
        service.add_file_version(actor, resource.id, "x.exe", "application/x-msdownload", b"MZ")


def test_viewing_resource_reduces_unread_recommendation_bonus(db, academic, storage):
    service = ResourceService(db, academic, storage)
    teacher = principal(TEACHER_ID, "teacher")
    student = principal(STUDENT_ID, "student")
    resource = create_note(service, teacher)
    service.add_content_version(teacher, resource.id, VersionCreate(text_content="read me"))
    service.publish(teacher, resource.id)
    before = service.recommendations(student)[0][0]
    service.get_resource_for_actor(student, resource.id)
    after = service.recommendations(student)[0][0]
    assert before - after >= 100


def test_publish_creates_outbox_event(db, academic, storage):
    from sqlalchemy import select

    from app.domain.entities.models import OutboxEvent

    service = ResourceService(db, academic, storage)
    teacher = principal(TEACHER_ID, "teacher")
    resource = create_note(service, teacher)
    service.add_content_version(teacher, resource.id, VersionCreate(text_content="event"))
    service.publish(teacher, resource.id)
    event_types = list(db.scalars(select(OutboxEvent.event_type)).all())
    assert "learning.resource_created" in event_types
    assert "learning.resource_published" in event_types
