from __future__ import annotations

from fastapi import Depends

from app.clients.academic import AcademicClient, get_academic_client


def academic_client_dependency(
    client: AcademicClient = Depends(get_academic_client),
) -> AcademicClient:
    return client
