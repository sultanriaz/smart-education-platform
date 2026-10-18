from __future__ import annotations

import uuid
from datetime import UTC, datetime

import httpx

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.platform_service import PlatformService
from app.workers.celery_app import celery_app


def utcnow():
    return datetime.now(UTC)


@celery_app.task(name="platform.health_sweep")
def health_sweep(job_id: str | None = None):
    db = SessionLocal()
    try:
        service = PlatformService(db)
        results = service.check_services()
        if job_id:
            job = service.repo.get_job(uuid.UUID(job_id))
            if job:
                job.status = "COMPLETED"
                job.completed_at = utcnow()
                job.result = {
                    "services": [
                        {
                            "service_name": item.service_name,
                            "status": item.status,
                        }
                        for item in results
                    ]
                }
                db.commit()
        return {"checked": len(results)}
    except Exception as exc:
        if job_id:
            job = PlatformService(db).repo.get_job(uuid.UUID(job_id))
            if job:
                job.status = "FAILED"
                job.error = str(exc)
                job.completed_at = utcnow()
                db.commit()
        raise
    finally:
        db.close()


@celery_app.task(name="platform.remote_data_job")
def remote_data_job(job_id: str):
    """Legacy entry point disabled: must not use static X-Internal-Token auth.

    The durable job runner uses service-scoped, audience-bound credentials.
    """
    raise RuntimeError("Legacy remote job task disabled; use platform.event_worker")
