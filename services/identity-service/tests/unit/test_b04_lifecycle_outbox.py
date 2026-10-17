"""B04 transactional Identity lifecycle events and duplicate suppression."""

from sqlalchemy import select

from app.domain.entities.outbox import OutboxEvent
from app.schemas.user import AdminUserUpdate, UserRegister
from app.services.auth_service import AuthService
from app.services.user_service import UserService


def test_deactivation_and_reactivation_queue_durable_events(db):
    user = AuthService(db).register(UserRegister(
        email="b04events@example.edu", full_name="B04 Events", password="StrongPass123!",
    ))
    service = UserService(db)
    service.deactivate(user.id)
    events = list(db.scalars(select(OutboxEvent).where(
        OutboxEvent.event_type == "identity.account_eligibility_changed"
    )))
    assert len(events) == 1
    assert events[0].aggregate_id == user.id
    assert events[0].payload == {"user_id": str(user.id), "is_active": False,
                                 "roles": ["student"], "auth_version": 1}
    service.deactivate(user.id)
    assert len(list(db.scalars(select(OutboxEvent).where(
        OutboxEvent.event_type == "identity.account_eligibility_changed")))) == 1
    service.update_by_admin(user.id, AdminUserUpdate(is_active=True))
    events = list(db.scalars(select(OutboxEvent).where(
        OutboxEvent.event_type == "identity.account_eligibility_changed"
    ).order_by(OutboxEvent.created_at, OutboxEvent.id)))
    assert len(events) == 2
    assert any(e.payload["is_active"] is True for e in events)


def test_cosmetic_changes_do_not_publish_identity_eligibility(db):
    user = AuthService(db).register(UserRegister(
        email="b04cosmetic@example.edu", full_name="Cosmetic User", password="StrongPass123!",
    ))
    UserService(db).update_by_admin(user.id, AdminUserUpdate(full_name="New Display Name"))
    assert list(db.scalars(select(OutboxEvent).where(
        OutboxEvent.event_type == "identity.account_eligibility_changed"))) == []


def test_roles_changed_publish_without_pii(db):
    user = AuthService(db).register(UserRegister(
        email="b04role@example.edu", full_name="B04 Roles", password="StrongPass123!",
    ))
    UserService(db).update_by_admin(user.id, AdminUserUpdate(roles=["teacher"]))
    event = db.scalar(select(OutboxEvent).where(
        OutboxEvent.event_type == "identity.account_eligibility_changed"
    ))
    assert event.payload["roles"] == ["teacher"]
    assert "email" not in event.payload
