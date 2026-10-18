from __future__ import annotations

from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, Query, HTTPException

from app.api.dependencies import get_platform_service
from app.core.errors import DomainError
from app.schemas.admin import JobCreate, JobOut, ServiceRegistryCreate, ServiceRegistryOut
from app.security.auth import Principal, require_roles
from app.services.platform_service import PlatformService

router = APIRouter(prefix="/admin", tags=["Platform Administration"])


@router.get("/audit")
def audit(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    source_service: str | None = None,
    actor_user_id: uuid.UUID | None = None,
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    outcome: str | None = None,
    request_id: str | None = None,
    correlation_id: str | None = None,
    trace_id: str | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
    _admin=Depends(require_roles("admin")),
    service: PlatformService = Depends(get_platform_service),
):
    if from_date and to_date and from_date > to_date:
        raise HTTPException(422, "from_date must not exceed to_date")
    filters = dict(source_service=source_service, actor_user_id=actor_user_id, action=action, entity_type=entity_type, entity_id=entity_id, outcome=outcome, request_id=request_id, correlation_id=correlation_id, trace_id=trace_id, from_date=from_date, to_date=to_date)
    rows = service.repo.list_audit(limit=limit, offset=offset, **filters)
    from app.services.governance import redact
    return [dict(id=str(row.id), event_id=str(row.event_id) if row.event_id else None, source_service=row.source_service, actor_user_id=str(row.actor_user_id) if row.actor_user_id else None, action=row.action, entity_type=row.entity_type, entity_id=row.entity_id, outcome=row.outcome, request_id=row.request_id, trace_id=row.trace_id, correlation_id=row.correlation_id, metadata=redact(row.metadata_json), occurred_at=row.occurred_at) for row in rows]


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
    try:
        return service.create_job(payload, principal.user_id)
    except DomainError as exc:
        raise HTTPException(exc.status_code, str(exc)) from exc


@router.get("/jobs", response_model=list[JobOut])
def list_jobs(
    _admin=Depends(require_roles("admin")),
    service: PlatformService = Depends(get_platform_service),
):
    return service.repo.list_jobs()
