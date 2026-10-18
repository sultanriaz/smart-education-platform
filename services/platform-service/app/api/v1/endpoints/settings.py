from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.dependencies import get_platform_service
from app.core.errors import DomainError
from app.schemas.admin import (
    FeatureFlagOut,
    FeatureFlagUpsert,
    SettingOut,
    SettingUpsert,
)
from app.security.auth import Principal, current_principal, require_roles
from app.services.platform_service import PlatformService

router = APIRouter(tags=["Settings"])


@router.get("/settings/public", response_model=list[SettingOut])
def public_settings(
    _principal: Principal = Depends(current_principal),
    service: PlatformService = Depends(get_platform_service),
):
    return service.repo.list_settings(public_only=True)


@router.get("/features", response_model=list[FeatureFlagOut])
def features(
    _principal: Principal = Depends(current_principal),
    service: PlatformService = Depends(get_platform_service),
):
    return service.repo.list_features()


@router.get("/admin/settings", response_model=list[SettingOut])
def admin_settings(
    _admin=Depends(require_roles("admin")),
    service: PlatformService = Depends(get_platform_service),
):
    return service.repo.list_settings()


@router.put("/admin/settings/{key}", response_model=SettingOut)
def upsert_setting(
    key: str,
    payload: SettingUpsert,
    principal: Principal = Depends(require_roles("admin")),
    service: PlatformService = Depends(get_platform_service),
):
    try:
        return service.upsert_setting(key, payload, principal.user_id)
    except DomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.put("/admin/features/{key}", response_model=FeatureFlagOut)
def upsert_feature(
    key: str,
    payload: FeatureFlagUpsert,
    principal: Principal = Depends(require_roles("admin")),
    service: PlatformService = Depends(get_platform_service),
):
    try:
        return service.upsert_feature(key, payload, principal.user_id)
    except DomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


class RollbackRevision(BaseModel):
    expected_version: int | None = Field(default=None, ge=0)


@router.get("/admin/settings/{key}/history")
def setting_history(key: str, limit: int = Query(default=50, ge=1, le=100), _admin=Depends(require_roles("admin")), service: PlatformService = Depends(get_platform_service)):
    return [{"version": r.version, "value": r.value, "is_public": r.is_public, "description": r.description, "changed_by_user_id": str(r.changed_by_user_id), "reason": r.reason, "created_at": r.created_at} for r in service.repo.setting_history(key, limit)]


@router.post("/admin/settings/{key}/restore/{version}", response_model=SettingOut)
def restore_setting(key: str, version: int, payload: RollbackRevision, principal: Principal = Depends(require_roles("admin")), service: PlatformService = Depends(get_platform_service)):
    try:
        return service.rollback_setting(key, version, principal.user_id, payload.expected_version)
    except DomainError as exc:
        raise HTTPException(exc.status_code, str(exc)) from exc


@router.get("/admin/features/{key}/history")
def feature_history(key: str, limit: int = Query(default=50, ge=1, le=100), _admin=Depends(require_roles("admin")), service: PlatformService = Depends(get_platform_service)):
    return [{"version": r.version, "enabled": r.enabled, "config": r.config, "description": r.description, "changed_by_user_id": str(r.changed_by_user_id), "reason": r.reason, "created_at": r.created_at} for r in service.repo.feature_history(key, limit)]


@router.post("/admin/features/{key}/restore/{version}", response_model=FeatureFlagOut)
def restore_feature(key: str, version: int, payload: RollbackRevision, principal: Principal = Depends(require_roles("admin")), service: PlatformService = Depends(get_platform_service)):
    try:
        return service.rollback_feature(key, version, principal.user_id, payload.expected_version)
    except DomainError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.get("/features/{key}/enabled")
def evaluated_feature(key: str, principal: Principal = Depends(current_principal), service: PlatformService = Depends(get_platform_service)):
    return {"key": key, "enabled": service.flag_enabled(key, principal.user_id)}
