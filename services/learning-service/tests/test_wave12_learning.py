from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.core.errors import ConflictError, ValidationDomainError
from app.domain.entities.models import AccessAction, ResourceType
from app.services.resource_service import ResourceService


class Store:
    def __init__(self, data):
        self.data = data
    def get_bytes(self, key):
        return self.data


def test_download_fails_closed_on_corruption(monkeypatch):
    import hashlib
    data = b"integrity protected bytes"
    version = SimpleNamespace(storage_key="bucket/file", checksum_sha256=hashlib.sha256(data).hexdigest())
    resource = SimpleNamespace(id=uuid4(), resource_type=ResourceType.FILE, versions=[SimpleNamespace(**vars(version), version_number=1, id=uuid4())])
    subject = SimpleNamespace(user_id=uuid4())
    service = ResourceService.__new__(ResourceService)
    service.db = SimpleNamespace(add=lambda *_: None)
    service.storage = Store(b"changed content")
    service.get_resource_for_actor = lambda *_: resource
    recorded = []
    service.record_access = lambda *args: recorded.append(args)
    with pytest.raises(ConflictError):
        service.download_latest(subject, resource.id)
    assert not recorded
    service.storage = Store(data)
    got_version, got_data = service.download_latest(subject, resource.id)
    assert got_data == data and got_version is resource.versions[0]
    assert recorded[-1][-1] == AccessAction.DOWNLOAD


def test_file_deletion_requires_owner_and_defers_physical_erase(db, academic, storage):
    from app.core.errors import ForbiddenError
    from app.domain.entities.models import FileDeletionTask, FileOperationAudit, ResourceStatus, TargetType
    from app.schemas.resource import ResourceCreate, TargetInput
    from app.security.auth import Principal
    from sqlalchemy import select
    from tests.conftest import SECTION_ID, TEACHER_ID, STUDENT_ID

    service = ResourceService(db, academic, storage)
    owner = Principal(TEACHER_ID, frozenset({"teacher"}), "x")
    stranger = Principal(STUDENT_ID, frozenset({"student"}), "x")
    resource = service.create_resource(owner, ResourceCreate(
        title="Draft PDF", resource_type=ResourceType.FILE,
        targets=[TargetInput(target_type=TargetType.SECTION, target_id=SECTION_ID)],
    ))
    version = service.add_file_version(owner, resource.id, "example.pdf", "application/pdf", b"%PDF-ok")
    key = version.storage_key
    with pytest.raises(ForbiddenError):
        service.delete_file_version(stranger, resource.id, version.id)
    assert storage.get_bytes(key) == b"%PDF-ok"
    service.delete_file_version(owner, resource.id, version.id)
    assert db.scalar(select(FileDeletionTask).where(FileDeletionTask.storage_key == key))
    assert db.scalar(select(FileOperationAudit).where(FileOperationAudit.operation == "DELETE_SCHEDULED"))
    assert storage.get_bytes(key) == b"%PDF-ok", "Storage must only be removed by owned worker"
    assert not service._get_or_404(resource.id).versions


def test_published_file_version_deletion_is_denied(db, academic, storage):
    from app.schemas.resource import ResourceCreate, TargetInput
    from app.domain.entities.models import TargetType
    from app.security.auth import Principal
    from tests.conftest import SECTION_ID, TEACHER_ID
    owner = Principal(TEACHER_ID, frozenset({"teacher"}), "x")
    service = ResourceService(db, academic, storage)
    resource = service.create_resource(owner, ResourceCreate(
        title="Published PDF", resource_type=ResourceType.FILE,
        targets=[TargetInput(target_type=TargetType.SECTION, target_id=SECTION_ID)],
    ))
    version = service.add_file_version(owner, resource.id, "example.pdf", "application/pdf", b"%PDF-ok")
    service.publish(owner, resource.id)
    with pytest.raises(ConflictError):
        service.delete_file_version(owner, resource.id, version.id)


def test_deletion_worker_erases_queued_file_once(db, academic, storage, monkeypatch):
    from app.domain.entities.models import FileDeletionTask, FileOperationAudit, TargetType
    from app.schemas.resource import ResourceCreate, TargetInput
    from app.security.auth import Principal
    from sqlalchemy import select
    from sqlalchemy.orm import sessionmaker
    from tests.conftest import SECTION_ID, TEACHER_ID
    from app.services.file_cleanup import run_file_cleanup
    from app.services import file_cleanup
    owner = Principal(TEACHER_ID, frozenset({"teacher"}), "x")
    service = ResourceService(db, academic, storage)
    resource = service.create_resource(owner, ResourceCreate(title="Cleanup PDF", resource_type=ResourceType.FILE,
        targets=[TargetInput(target_type=TargetType.SECTION, target_id=SECTION_ID)]))
    version = service.add_file_version(owner, resource.id, "cleanup.pdf", "application/pdf", b"%PDF-example")
    service.delete_file_version(owner, resource.id, version.id)
    factory = sessionmaker(bind=db.get_bind(), expire_on_commit=False)
    monkeypatch.setattr(file_cleanup, "SessionLocal", factory)
    monkeypatch.setattr(file_cleanup, "get_storage_backend", lambda: storage)
    assert run_file_cleanup() == 1
    assert run_file_cleanup() == 0
    with pytest.raises(FileNotFoundError):
        storage.get_bytes(version.storage_key)
    assert db.scalar(select(FileDeletionTask).where(FileDeletionTask.storage_key == version.storage_key)).deleted_at
    assert db.scalar(select(FileOperationAudit).where(FileOperationAudit.operation == "DELETED"))


def test_course_targeted_link_and_video_requires_owner_and_valid_https(db, academic, storage):
    from app.domain.entities.models import TargetType
    from app.schemas.resource import ResourceCreate, TargetInput, VersionCreate
    from app.security.auth import Principal
    from tests.conftest import COURSE_ID, STUDENT_ID, TEACHER_ID
    owner = Principal(TEACHER_ID, frozenset({"teacher"}), "x")
    student = Principal(STUDENT_ID, frozenset({"student"}), "x")
    service = ResourceService(db, academic, storage)
    for resource_type in (ResourceType.LINK, ResourceType.VIDEO):
        resource = service.create_resource(owner, ResourceCreate(
            title=f"Course {resource_type}", resource_type=resource_type,
            targets=[TargetInput(target_type=TargetType.COURSE, target_id=COURSE_ID)],
        ))
        with pytest.raises(ValidationDomainError):
            service.add_content_version(owner, resource.id, VersionCreate())
        service.add_content_version(owner, resource.id, VersionCreate(external_url="https://example.org/video"))
        service.publish(owner, resource.id)
        assert service.get_resource_for_actor(student, resource.id).id == resource.id
