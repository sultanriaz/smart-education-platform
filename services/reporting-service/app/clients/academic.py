from __future__ import annotations

import uuid
import httpx
from fastapi import HTTPException
from smartedu_infra.http_pool import shared_http_client
from app.core.config import settings


def require_teacher_section(user_id: uuid.UUID, section_id: uuid.UUID, bearer_token: str) -> None:
    """Always ask the Academic OWNER; never authorize a Teacher by role alone."""
    url = f"{settings.ACADEMIC_SERVICE_BASE_URL.rstrip('/')}/api/v1/teachers/{user_id}/sections/{section_id}/assignment"
    try:
        response = shared_http_client(settings.ACADEMIC_SERVICE_BASE_URL).get(
            url, headers={"Authorization": f"Bearer {bearer_token}"},
            timeout=settings.ACADEMIC_SERVICE_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503, detail="Academic membership validation unavailable") from exc
    if response.status_code in {401, 403, 404}:
        raise HTTPException(status_code=403, detail="Teacher is not assigned to this section")
    if response.status_code >= 500:
        raise HTTPException(status_code=503, detail="Academic membership validation unavailable")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Unexpected Academic response")
    try:
        assigned = response.json().get("assigned") is True
    except (ValueError, AttributeError):
        raise HTTPException(status_code=502, detail="Invalid Academic membership response")
    if not assigned:
        raise HTTPException(status_code=403, detail="Teacher is not assigned to this section")
