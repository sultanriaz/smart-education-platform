from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_resource_service
from app.core.errors import DomainError
from app.schemas.resource import RecommendationOut, ResourceOut, ResourceAccessOut
from app.security.auth import Principal, require_roles
from app.services.resource_service import ResourceService

router = APIRouter(prefix="/students/me", tags=["Student Learning"])


@router.get("/resources", response_model=list[ResourceOut])
def my_resources(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    principal: Principal = Depends(require_roles("student")),
    service: ResourceService = Depends(get_resource_service),
):
    try:
        return service.list_student_resources(principal, offset, limit)
    except DomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.get("/recommendations", response_model=list[RecommendationOut])
def recommendations(
    limit: int = Query(default=20, ge=1, le=100),
    principal: Principal = Depends(require_roles("student")),
    service: ResourceService = Depends(get_resource_service),
):
    try:
        return [
            RecommendationOut(resource=resource, score=score, reason=reason)
            for score, resource, reason in service.recommendations(principal, limit)
        ]
    except DomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.get("/activity", response_model=list[ResourceAccessOut])
def activity_history(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    principal: Principal = Depends(require_roles("student")),
    service: ResourceService = Depends(get_resource_service),
):
    return service.student_history(principal, offset=offset, limit=limit)
