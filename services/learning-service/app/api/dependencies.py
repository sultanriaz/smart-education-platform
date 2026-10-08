from __future__ import annotations

from fastapi import Depends
from sqlalchemy.orm import Session

from app.clients.academic import AcademicClient, get_academic_client
from app.db.session import get_db
from app.services.resource_service import ResourceService
from app.storage.base import StorageBackend
from app.storage.dependencies import get_storage_backend


def get_resource_service(
    db: Session = Depends(get_db),
    academic: AcademicClient = Depends(get_academic_client),
    storage: StorageBackend = Depends(get_storage_backend),
) -> ResourceService:
    return ResourceService(db, academic, storage)
