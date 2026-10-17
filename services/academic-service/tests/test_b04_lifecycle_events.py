"""B04 owner-event consumer must be durable, idempotent, and fail closed."""
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app import event_worker
from app.domain.models import IdentityEligibilityInbox, StudentAcademicProfile

# Reuse the signed Identity owner fixture from the existing B04 contract suite.
from tests.test_identity_accounts import owner  # noqa: F401


def envelope(user_id, event_id=None, *, source="identity-service", subject=None):
    return SimpleNamespace(
        event_id=event_id or uuid4(), source=source,
        event_type="identity.account_eligibility_changed",
        subject=subject if subject is not None else str(user_id),
        data={"user_id": str(user_id)},
    )


def test_event_disables_restores_and_deduplicates(db, academic, owner, monkeypatch):
    student = academic.students[0]
    uid = student.external_user_id
    owner.state[str(uid)] = (False, ["student"], 1)
    monkeypatch.setattr(event_worker, "SessionLocal", lambda: Session(db.bind))
    monkeypatch.setattr(event_worker.IdentityAccountClient, "from_environment", lambda: owner.checker)
    first = envelope(uid)
    event_worker.handle_identity_eligibility(first)
    db.expire_all()
    assert db.get(StudentAcademicProfile, student.id).is_active is False
    assert db.get(IdentityEligibilityInbox, first.event_id) is not None
    event_worker.handle_identity_eligibility(first)
    assert db.query(IdentityEligibilityInbox).count() == 1

    owner.state[str(uid)] = (True, ["student"], 2)
    next_event = envelope(uid)
    event_worker.handle_identity_eligibility(next_event)
    db.expire_all()
    assert db.get(StudentAcademicProfile, student.id).is_active is True
    assert db.query(IdentityEligibilityInbox).count() == 2


@pytest.mark.parametrize("bad", ["wrong-source", "wrong-subject"])
def test_invalid_producer_or_subject_must_not_modify_db(db, academic, owner, monkeypatch, bad):
    student = academic.students[0]
    evt = envelope(student.external_user_id, source="assessment-service" if bad=="wrong-source" else "identity-service",
                   subject=str(uuid4()) if bad == "wrong-subject" else None)
    monkeypatch.setattr(event_worker, "SessionLocal", lambda: Session(db.bind))
    with pytest.raises(ValueError):
        event_worker.handle_identity_eligibility(evt)
    assert db.query(IdentityEligibilityInbox).count() == 0


def test_lookup_outage_leaves_no_processed_marker(db, academic, owner, monkeypatch):
    student = academic.students[0]
    owner.state[str(student.external_user_id)] = "down"
    monkeypatch.setattr(event_worker, "SessionLocal", lambda: Session(db.bind))
    monkeypatch.setattr(event_worker.IdentityAccountClient, "from_environment", lambda: owner.checker)
    with pytest.raises(Exception):
        event_worker.handle_identity_eligibility(envelope(student.external_user_id))
    assert db.query(IdentityEligibilityInbox).count() == 0
