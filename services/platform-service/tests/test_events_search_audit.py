from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.schemas.events import InternalEventIn


def event(event_type: str, payload: dict, event_id=None):
    return InternalEventIn(
        event_id=event_id or uuid.uuid4(),
        source_service="academic-service",
        event_type=event_type,
        payload=payload,
        occurred_at=datetime.now(UTC),
    )


def test_event_idempotency(ingestion):
    event_id = uuid.uuid4()
    payload = event("noop", {}, event_id)
    assert ingestion.ingest(payload) == "processed"
    assert ingestion.ingest(payload) == "duplicate"


def test_search_upsert_and_update(ingestion, platform):
    document_id = str(uuid.uuid4())
    ingestion.ingest(
        event(
            "platform.search.upsert",
            {
                "document_type": "course",
                "document_id": document_id,
                "title": "Software Engineering",
                "body": "Requirements architecture testing",
                "url_path": f"/courses/{document_id}",
                "audience_roles": ["student", "teacher", "admin"],
            },
        )
    )
    results = platform.search("Software", {"student"})
    assert len(results) == 1
    assert results[0].title == "Software Engineering"

    ingestion.ingest(
        event(
            "platform.search.upsert",
            {
                "document_type": "course",
                "document_id": document_id,
                "title": "Advanced Software Engineering",
                "body": "Architecture",
                "audience_roles": ["student", "teacher", "admin"],
            },
        )
    )
    results = platform.search("Advanced", {"teacher"})
    assert len(results) == 1
    assert results[0].document_id == document_id


def test_search_role_filtering(ingestion, platform):
    ingestion.ingest(
        event(
            "platform.search.upsert",
            {
                "document_type": "admin-record",
                "document_id": "secret-1",
                "title": "Admin Only",
                "audience_roles": ["admin"],
            },
        )
    )
    assert platform.search("Admin", {"student"}) == []
    assert len(platform.search("Admin", {"admin"})) == 1


def test_search_delete(ingestion, platform):
    ingestion.ingest(
        event(
            "platform.search.upsert",
            {
                "document_type": "announcement",
                "document_id": "a1",
                "title": "Campus Notice",
            },
        )
    )
    assert len(platform.search("Campus", {"student"})) == 1
    ingestion.ingest(
        event(
            "platform.search.delete",
            {"document_type": "announcement", "document_id": "a1"},
        )
    )
    assert platform.search("Campus", {"student"}) == []


def test_audit_projection(ingestion, platform):
    actor = uuid.uuid4()
    ingestion.ingest(
        event(
            "audit.user_updated",
            {
                "actor_user_id": str(actor),
                "action": "user.updated",
                "entity_type": "user",
                "entity_id": "u1",
                "correlation_id": "req-1",
                "metadata": {"field": "name"},
            },
        )
    )
    rows = platform.repo.list_audit()
    assert len(rows) == 1
    assert rows[0].actor_user_id == actor
    assert rows[0].action == "user.updated"


def test_public_course_and_notice_search_remain_available(ingestion, platform):
    ingestion.ingest(event("platform.search.upsert", {
        "document_type": "course", "document_id": "public-c1", "title": "Open Course Catalog",
        "audience_roles": ["student", "teacher", "admin"],
    }))
    ingestion.ingest(event("platform.search.upsert", {
        "document_type": "announcement", "document_id": "public-a1", "title": "Open Campus Notice",
    }))
    assert len(platform.search("Open Course", {"student"})) == 1
    assert len(platform.search("Open Campus", {"teacher"})) == 1


def test_restricted_section_search_is_hidden_and_pagination_does_not_mask_public(ingestion, platform):
    for k in range(8):
        ingestion.ingest(event("platform.search.upsert", {
            "document_type": "learning_resource", "document_id": f"private-{k}",
            "title": "Resourced Topic", "audience_roles": ["student"],
            "metadata": {"section_id": "restricted-section", "allowed_user_ids": [str(uuid.uuid4())]},
        }))
    ingestion.ingest(event("platform.search.upsert", {
        "document_type": "course", "document_id": "public-course", "title": "Resourced Topic Catalog",
        "audience_roles": ["student"],
    }))
    results=platform.search("Resourced Topic", {"student"}, user_id=uuid.uuid4(), limit=1)
    assert [result.document_id for result in results] == ["public-course"]


def test_unscoped_resource_does_not_default_public(ingestion, platform):
    ingestion.ingest(event("platform.search.upsert", {
        "document_type": "learning_resource", "document_id": "resource-r1", "title": "Unscoped Private Lecture",
        "audience_roles": ["student"],
    }))
    assert platform.search("Unscoped Private", {"student"}, user_id=uuid.uuid4()) == []
