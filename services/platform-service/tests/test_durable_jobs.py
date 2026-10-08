import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import sessionmaker

from app.schemas.admin import JobCreate
from app.workers.job_runner import process_jobs


def test_worker_completes_a_queued_health_job_once(db, platform):
    job = platform.create_job(JobCreate(job_type="HEALTH_SWEEP"), uuid.uuid4())
    factory = sessionmaker(bind=db.get_bind(), expire_on_commit=False)
    assert process_jobs(factory)
    db.expire_all()
    assert platform.repo.get_job(job.id).status == "COMPLETED"
    assert platform.repo.get_job(job.id).attempts == 1
    assert not process_jobs(factory)


def test_worker_recovers_an_abandoned_job_and_limits_attempts(db, platform):
    job = platform.create_job(JobCreate(job_type="REINDEX"), uuid.uuid4())
    job.status = "RUNNING"
    job.started_at = datetime.now(UTC) - timedelta(minutes=10)
    job.attempts = 3
    db.commit()
    assert process_jobs(sessionmaker(bind=db.get_bind()))
    db.expire_all()
    assert platform.repo.get_job(job.id).status == "FAILED"
    assert "attempt limit" in platform.repo.get_job(job.id).error


def test_unsupported_owner_job_finishes_with_explicit_failure(db, platform):
    job = platform.create_job(
        JobCreate(job_type="EXPORT", target_service="missing", resource_type="students"),
        uuid.uuid4(),
    )
    assert process_jobs(sessionmaker(bind=db.get_bind()))
    db.expire_all()
    assert platform.repo.get_job(job.id).status == "FAILED"
    assert platform.repo.get_job(job.id).completed_at is not None
