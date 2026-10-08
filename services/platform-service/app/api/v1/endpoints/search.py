from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_platform_service
from app.schemas.search import SearchResult
from app.security.auth import Principal, current_principal
from app.services.platform_service import PlatformService

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=list[SearchResult])
def search(
    q: str = Query(default="", max_length=160),
    document_type: str | None = None,
    source_service: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    principal: Principal = Depends(current_principal),
    service: PlatformService = Depends(get_platform_service),
):
    return service.search(
        query=q,
        roles=principal.roles,
        document_type=document_type,
        source_service=source_service,
        limit=limit,
    )
