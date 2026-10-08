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
    db = SessionLocal()
    try:
        service = PlatformService(db)
        job = service.repo.get_job(uuid.UUID(job_id))
        if not job:
            return {"status": "missing"}

        registry = service.repo.service_registry(job.target_service or "")
        if not registry:
            job.status = "FAILED"
            job.error = "Target service not registered"
            job.completed_at = utcnow()
            db.commit()
            return {"status": "failed"}

        job.status = "RUNNING"
        job.started_at = utcnow()
        job.attempts += 1
        db.commit()

        headers = {"X-Internal-Token": settings.SERVICE_INTERNAL_TOKEN}
        resource = job.resource_type or "default"

        if job.job_type == "EXPORT":
            response = httpx.get(
                f"{registry.base_url}/api/v1/internal/exports/{resource}",
                headers=headers,
                params=job.parameters,
                timeout=registry.timeout_seconds,
            )
        elif job.job_type == "IMPORT":
            response = httpx.post(
                f"{registry.base_url}/api/v1/internal/imports/{resource}",
                headers=headers,
                params=job.parameters,
                json=job.payload,
                timeout=registry.timeout_seconds,
            )
        else:
            raise ValueError(f"Unsupported remote job type: {job.job_type}")

        response.raise_for_status()
        job.result = response.json() if response.content else {}
        job.status = "COMPLETED"
        job.completed_at = utcnow()
        db.commit()
        return {"status": "completed", "job_id": job_id}
    except Exception as exc:
        try:
            job = PlatformService(db).repo.get_job(uuid.UUID(job_id))
            if job:
                job.status = "FAILED"
                job.error = str(exc)
                job.completed_at = utcnow()
                db.commit()
        finally:
            db.close()
        raise
    finally:
        if db.is_active:
            db.close()
