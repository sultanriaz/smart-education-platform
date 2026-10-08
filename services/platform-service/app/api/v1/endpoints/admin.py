from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_platform_service
from app.schemas.admin import JobCreate, JobOut, ServiceRegistryCreate, ServiceRegistryOut
from app.security.auth import Principal, require_roles
from app.services.platform_service import PlatformService

router = APIRouter(prefix="/admin", tags=["Platform Administration"])


@router.get("/audit")
def audit(
    limit: int = 100,
    _admin=Depends(require_roles("admin")),
    service: PlatformService = Depends(get_platform_service),
):
    rows = service.repo.list_audit(min(max(limit, 1), 500))
    return [
        {
            "id": str(row.id),
            "source_service": row.source_service,
            "actor_user_id": str(row.actor_user_id) if row.actor_user_id else None,
            "action": row.action,
            "entity_type": row.entity_type,
            "entity_id": row.entity_id,
            "correlation_id": row.correlation_id,
            "metadata": row.metadata_json,
            "occurred_at": row.occurred_at,
        }
        for row in rows
    ]


@router.get("/services", response_model=list[ServiceRegistryOut])
def services(
    _admin=Depends(require_roles("admin")),
    service: PlatformService = Depends(get_platform_service),
):
    return service.repo.list_services()


@router.put("/services/{service_name}", response_model=ServiceRegistryOut)
def upsert_service(
    service_name: str,
    payload: ServiceRegistryCreate,
    _admin=Depends(require_roles("admin")),
    service: PlatformService = Depends(get_platform_service),
):
    if payload.service_name != service_name:
        payload = payload.model_copy(update={"service_name": service_name})
    return service.upsert_service(payload)


@router.post("/services/health")
def health_sweep(
    _admin=Depends(require_roles("admin")),
    service: PlatformService = Depends(get_platform_service),
):
    results = service.check_services()
    return [
        {
            "service_name": row.service_name,
            "status": row.status,
            "health_ok": row.health_ok,
            "ready_ok": row.ready_ok,
            "latency_ms": row.latency_ms,
            "detail": row.detail,
        }
        for row in results
    ]


@router.post("/jobs", response_model=JobOut)
def create_job(
    payload: JobCreate,
    principal: Principal = Depends(require_roles("admin")),
    service: PlatformService = Depends(get_platform_service),
):
    return service.create_job(payload, principal.user_id)


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(
    _admin=Depends(require_roles("admin")),
    service: PlatformService = Depends(get_platform_service),
):
    return service.repo.list_jobs()
