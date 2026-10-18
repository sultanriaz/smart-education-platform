"""Focused Wave 13/14 security and lifecycle regressions."""
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select

from app.core.errors import ConflictError
from app.domain.entities.models import FeatureFlagRevision, SearchIndexRevision, SettingRevision
from app.schemas.admin import FeatureFlagUpsert, JobCreate, SettingUpsert
from app.schemas.events import InternalEventIn
from app.schemas.support import MessageCreate, TicketCreate, TicketOut, TicketUpdateAdmin
from app.api.v1.endpoints.support import ticket_view
from app.services.governance import feature_enabled, redact
from app.workers.job_runner import execute_job


def test_governance_revisions_and_optimistic_conflict(db, platform):
    actor = uuid.uuid4()
    first = platform.upsert_setting("campus.name", SettingUpsert(value={"name": "A"}, expected_version=0), actor)
    assert first.version == 1
    with pytest.raises(ConflictError):
        platform.upsert_setting("campus.name", SettingUpsert(value={"name": "B"}, expected_version=0), actor)
    second = platform.upsert_setting("campus.name", SettingUpsert(value={"name": "B"}, expected_version=1), actor)
    assert second.version == 2
    third = platform.rollback_setting("campus.name", 1, actor, expected_version=2)
    assert third.version == 3 and third.value == {"name": "A"}
    assert [revision.version for revision in platform.repo.setting_history("campus.name")] == [3, 2, 1]


def test_feature_percent_is_stable_and_revisions_are_immutable(platform, db):
    actor = uuid.uuid4()
    flag = platform.upsert_feature("flag.rollout", FeatureFlagUpsert(enabled=True, config={"percentage": 25}), actor)
    assert flag.version == 1
    assert feature_enabled(flag, actor) == feature_enabled(flag, actor)
    platform.rollback_feature("flag.rollout", 1, actor, expected_version=1)
    assert db.scalar(select(FeatureFlagRevision).where(FeatureFlagRevision.version == 1)).enabled


def test_audit_filtering_and_secret_redaction(ingestion, platform):
    event_id = uuid.uuid4()
    ingestion.ingest(InternalEventIn(event_id=event_id, source_service="identity-service", event_type="audit.user_update", payload={"audit": {"action": "user.update", "outcome": "FAILED", "correlation_id": "corr-99", "metadata": {"nested": {"refresh_token": "danger", "note": "hello\nworld"}}}}))
    rows = platform.repo.list_audit(correlation_id="corr-99", outcome="FAILED")
    assert len(rows) == 1 and rows[0].event_id == event_id
    assert rows[0].metadata_json["nested"]["refresh_token"] == "[REDACTED]"
    assert platform.repo.list_audit(outcome="SUCCEEDED") == []


def test_search_revisions_and_deindex(ingestion, db):
    def publish(t, data):
        ingestion.ingest(InternalEventIn(event_id=uuid.uuid4(), source_service="academic-service", event_type=t, payload=data))
    item = {"document_type": "course", "document_id": "c-1", "title": "Revision course"}
    publish("platform.search.upsert", item)
    assert len(db.scalars(select(SearchIndexRevision)).all()) == 1
    publish("platform.search.upsert", item)
    assert len(db.scalars(select(SearchIndexRevision)).all()) == 1
    publish("platform.search.delete", {"document_type": "course", "document_id": "c-1"})
    assert len(db.scalars(select(SearchIndexRevision)).all()) == 2


def test_internal_notes_not_exposed_to_requester(platform):
    requester, admin = uuid.uuid4(), uuid.uuid4()
    ticket = platform.create_ticket(TicketCreate(subject="Broken schedule", description="I have a problem"), requester)
    platform.add_message(ticket.id, MessageCreate(body="Visible to requester"), requester, False)
    platform.add_message(ticket.id, MessageCreate(body="Internal credentials", is_internal=True), admin, True)
    ticket = platform.get_ticket(ticket.id, requester, False)
    assert [message.body for message in ticket_view(ticket, False).messages] == ["Visible to requester"]
    assert len(ticket_view(ticket, True).messages) == 2


def test_sla_once_and_job_idempotency(db, platform):
    requester = uuid.uuid4()
    ticket = platform.create_ticket(TicketCreate(subject="Schedule issue", description="Something is broken", priority="HIGH"), requester)
    assert ticket.due_at is not None
    assert platform.escalate_due_tickets(now=ticket.due_at + timedelta(seconds=1)) == 1
    assert platform.escalate_due_tickets(now=ticket.due_at + timedelta(seconds=2)) == 0
    job = JobCreate(job_type="IMPORT", target_service="academic-service", resource_type="courses", payload={"items": [{"code": "CS"}]}, idempotency_key="batch-academic-001", dry_run=True)
    first = platform.create_job(job, requester)
    again = platform.create_job(job, requester)
    assert first.id == again.id
    with pytest.raises(ConflictError):
        platform.create_job(job.model_copy(update={"payload": {"items": [{"code": "MATH"}]}}), requester)
    first.payload = {"items": [{"code": "changed"}]}
    with pytest.raises(ValueError, match="changed"):
        execute_job(db, first)
