from __future__ import annotations

import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_resource_service
from app.core.errors import DomainError
from app.db.session import get_db
from app.repositories.resource_repository import ResourceRepository
from app.schemas.resource import (
    ResourceCreate,
    ResourceOut,
    ResourceUpdate,
    VersionCreate,
    VersionOut,
)
from app.security.auth import Principal, get_principal, require_roles
from app.services.resource_service import ResourceService

router = APIRouter(prefix="/resources", tags=["Learning Resources"])


def map_error(exc: DomainError):
    raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.post("", response_model=ResourceOut, status_code=status.HTTP_201_CREATED)
def create_resource(
    payload: ResourceCreate,
    principal: Principal = Depends(require_roles("teacher", "admin")),
    service: ResourceService = Depends(get_resource_service),
):
    try:
        return service.create_resource(principal, payload)
    except DomainError as exc:
        map_error(exc)


@router.get("", response_model=list[ResourceOut])
def list_resources(
    q: str | None = Query(default=None, max_length=100),
    resource_type: str | None = Query(default=None, pattern="^(NOTE|VIDEO|LINK|FILE)$"),
    status: str | None = Query(default=None, pattern="^(DRAFT|PUBLISHED|ARCHIVED)$"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    principal: Principal = Depends(require_roles("teacher", "admin")),
    db: Session = Depends(get_db),
):
    repo = ResourceRepository(db)
    if "admin" in principal.roles:
        return repo.list_resources(offset, limit, q=q, resource_type=resource_type, status=status)
    return repo.list_creator_resources(principal.user_id, offset, limit,
                                       q=q, resource_type=resource_type, status=status)


@router.get("/{resource_id}", response_model=ResourceOut)
def get_resource(
    resource_id: uuid.UUID,
    principal: Principal = Depends(get_principal),
    service: ResourceService = Depends(get_resource_service),
):
    try:
        return service.get_resource_for_actor(principal, resource_id)
    except DomainError as exc:
        map_error(exc)


@router.patch("/{resource_id}", response_model=ResourceOut)
def update_resource(
    resource_id: uuid.UUID,
    payload: ResourceUpdate,
    principal: Principal = Depends(require_roles("teacher", "admin")),
    service: ResourceService = Depends(get_resource_service),
):
    try:
        return service.update_resource(principal, resource_id, payload)
    except DomainError as exc:
        map_error(exc)


@router.post(
    "/{resource_id}/versions", response_model=VersionOut, status_code=status.HTTP_201_CREATED
)
def create_version(
    resource_id: uuid.UUID,
    payload: VersionCreate,
    principal: Principal = Depends(require_roles("teacher", "admin")),
    service: ResourceService = Depends(get_resource_service),
):
    try:
        return service.add_content_version(principal, resource_id, payload)
    except DomainError as exc:
        map_error(exc)


@router.post(
    "/{resource_id}/upload", response_model=VersionOut, status_code=status.HTTP_201_CREATED
)
async def upload_file(
    resource_id: uuid.UUID,
    file: UploadFile = File(...),
    change_note: str | None = Form(default=None),
    principal: Principal = Depends(require_roles("teacher", "admin")),
    service: ResourceService = Depends(get_resource_service),
):
    # Read a bounded amount. Rejected uploads never allocate their entire body
    # in an API worker and never reach object storage.
    from starlette.concurrency import run_in_threadpool

    from app.core.config import settings

    data = await file.read(settings.MAX_UPLOAD_BYTES + 1)
    try:
        return await run_in_threadpool(
            service.add_file_version,
            principal,
            resource_id,
            file.filename or "upload.bin",
            file.content_type or "application/octet-stream",
            data,
            change_note,
        )
    except DomainError as exc:
        map_error(exc)


@router.delete("/{resource_id}/versions/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file_version(
    resource_id: uuid.UUID,
    version_id: uuid.UUID,
    principal: Principal = Depends(require_roles("teacher", "admin")),
    service: ResourceService = Depends(get_resource_service),
):
    try:
        service.delete_file_version(principal, resource_id, version_id)
        return Response(status_code=204)
    except DomainError as exc:
        map_error(exc)


@router.get("/{resource_id}/versions", response_model=list[VersionOut])
def list_versions(
    resource_id: uuid.UUID,
    principal: Principal = Depends(get_principal),
    service: ResourceService = Depends(get_resource_service),
):
    try:
        return service.get_resource_for_actor(principal, resource_id).versions
    except DomainError as exc:
        map_error(exc)


@router.post("/{resource_id}/publish", response_model=ResourceOut)
def publish_resource(
    resource_id: uuid.UUID,
    principal: Principal = Depends(require_roles("teacher", "admin")),
    service: ResourceService = Depends(get_resource_service),
):
    try:
        return service.publish(principal, resource_id)
    except DomainError as exc:
        map_error(exc)


@router.post("/{resource_id}/archive", response_model=ResourceOut)
def archive_resource(
    resource_id: uuid.UUID,
    principal: Principal = Depends(require_roles("teacher", "admin")),
    service: ResourceService = Depends(get_resource_service),
):
    try:
        return service.archive(principal, resource_id)
    except DomainError as exc:
        map_error(exc)


@router.get("/{resource_id}/download")
def download_resource(
    resource_id: uuid.UUID,
    principal: Principal = Depends(get_principal),
    service: ResourceService = Depends(get_resource_service),
):
    try:
        version, data = service.download_latest(principal, resource_id)
        filename = version.original_filename or "resource.bin"
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Content-SHA256": version.checksum_sha256 or "",
        }
        return Response(
            content=data,
            media_type=version.mime_type or "application/octet-stream",
            headers=headers,
        )
    except DomainError as exc:
        map_error(exc)
