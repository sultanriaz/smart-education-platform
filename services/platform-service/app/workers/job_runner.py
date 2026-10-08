"""Execute durable Platform-owned jobs; domain data stays behind owner APIs."""

import uuid
from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy import and_, or_, select

from app.domain.entities.models import InternalEvent, JobRecord
from app.schemas.events import InternalEventIn
from app.services.event_ingestion_service import EventIngestionService
from app.services.platform_service import PlatformService
from app.sprint16 import internal_token_signer

LEASE_SECONDS = 300
MAX_ATTEMPTS = 3


def execute_job(db, job, client=None):
    service = PlatformService(db)
    if job.job_type == "HEALTH_SWEEP":
        checks = service.check_services(http_client=client)
        return {
            "services": [{"service_name": row.service_name, "status": row.status} for row in checks]
        }
    if job.job_type == "REINDEX":
        ingestion = EventIngestionService(db)
        count = 0
        offset = 0
        while True:
            rows = db.scalars(
                select(InternalEvent).order_by(InternalEvent.id).offset(offset).limit(100)
            ).all()
            if not rows:
                break
            for row in rows:
                ingestion._project_search(
                    InternalEventIn(
                        event_id=row.event_id,
                        source_service=row.source_service,
                        event_type=row.event_type,
                        occurred_at=row.occurred_at,
                        payload=row.payload,
                    )
                )
                db.flush()
                count += 1
            db.commit()
            offset += len(rows)
        return {"events_examined": count}
    if job.job_type not in {"IMPORT", "EXPORT"}:
        raise ValueError("Unsupported job type")
    registry = service.repo.service_registry(job.target_service or "")
    if not registry or not registry.enabled:
        raise ValueError("Target service is not registered and enabled")
    # Owners explicitly define import/export contracts. No shared DB access or
    # fallback static credential is permitted for these privileged operations.
    resource = job.resource_type or "default"
    if not resource.replace("-", "").replace("_", "").isalnum():
        raise ValueError("Invalid resource type")
    token = internal_token_signer().issue(
        audience=registry.service_name,
        scopes=(f"{registry.service_name.removesuffix('-service')}:data:{job.job_type.lower()}",),
    )
    headers = {"Authorization": f"Bearer {token}", "Idempotency-Key": str(job.id)}
    url = f"{registry.base_url}/api/v1/internal/{job.job_type.lower()}s/{resource}"
    own_client = client is None
    client = client or httpx.Client(follow_redirects=False)
    try:
        response = client.request(
            "GET" if job.job_type == "EXPORT" else "POST",
            url,
            headers=headers,
            params=job.parameters,
            json=job.payload if job.job_type == "IMPORT" else None,
            timeout=min(registry.timeout_seconds, 30),
        )
        response.raise_for_status()
        if len(response.content) > 5 * 1024 * 1024:
            raise ValueError("Export exceeds job result limit; use paginated parameters")
        return response.json() if response.content else {}
    finally:
        if own_client:
            client.close()


def process_jobs(session_factory, client=None):
    now = datetime.now(UTC)
    stale = now - timedelta(seconds=LEASE_SECONDS)
    with session_factory() as db:
        candidate = db.scalar(
            select(JobRecord)
            .where(
                or_(
                    JobRecord.status == "QUEUED",
                    and_(JobRecord.status == "RUNNING", JobRecord.started_at < stale),
                )
            )
            .order_by(JobRecord.created_at)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        if not candidate:
            return False
        if candidate.attempts >= MAX_ATTEMPTS:
            candidate.status, candidate.error, candidate.completed_at = (
                "FAILED",
                "Worker attempt limit reached",
                now,
            )
            db.commit()
            return True
        candidate.status, candidate.started_at = "RUNNING", now
        candidate.attempts += 1
        job_id = candidate.id
        db.commit()
    with session_factory() as db:
        job = db.get(JobRecord, uuid.UUID(str(job_id)))
        try:
            job.result = execute_job(db, job, client)
            job.status, job.error = "COMPLETED", None
        except Exception as exc:
            db.rollback()
            job = db.get(JobRecord, job_id)
            job.status = "FAILED"
            job.error = (
                f"Owner returned HTTP {exc.response.status_code}"
                if isinstance(exc, httpx.HTTPStatusError)
                else type(exc).__name__
            )
        job.completed_at = datetime.now(UTC)
        db.commit()
    return True
