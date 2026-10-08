from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_platform_service
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
    return service.upsert_setting(key, payload, principal.user_id)


@router.put("/admin/features/{key}", response_model=FeatureFlagOut)
def upsert_feature(
    key: str,
    payload: FeatureFlagUpsert,
    principal: Principal = Depends(require_roles("admin")),
    service: PlatformService = Depends(get_platform_service),
):
    return service.upsert_feature(key, payload, principal.user_id)
