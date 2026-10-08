from __future__ import annotations

import uuid

from app.clients.identity import IdentityUser
from app.schemas.notification import CampaignTarget, DirectRecipient
from app.services.target_resolver import TargetResolver


class FakeIdentity:
    def __init__(self, users):
        self.users = users

    def list_users_by_role(self, role, forwarded_token=None):
        return [u for u in self.users if role in u.roles]

    def get_users(self, user_ids, forwarded_token=None):
        wanted = set(user_ids)
        return [u for u in self.users if u.id in wanted]


class FakeAcademic:
    def __init__(self, user_ids):
        self.user_ids = user_ids

    def list_section_member_ids(self, section_id, forwarded_token=None):
        return list(self.user_ids)


def test_direct_targets_are_deduplicated():
    user_id = uuid.uuid4()
    resolver = TargetResolver(FakeIdentity([]), FakeAcademic([]))
    result = resolver.resolve(
        CampaignTarget(
            kind="DIRECT",
            recipients=[
                DirectRecipient(user_id=user_id),
                DirectRecipient(user_id=user_id, email="student@example.edu"),
            ],
        )
    )
    assert len(result) == 1
    assert result[0].email == "student@example.edu"


def test_role_target_filters_identity_users():
    student = IdentityUser(id=uuid.uuid4(), email="s@example.edu", roles=["student"])
    teacher = IdentityUser(id=uuid.uuid4(), email="t@example.edu", roles=["teacher"])
    resolver = TargetResolver(FakeIdentity([student, teacher]), FakeAcademic([]))
    result = resolver.resolve(CampaignTarget(kind="ROLE", role="student"), "token")
    assert [item.user_id for item in result] == [student.id]


def test_section_target_uses_academic_roster(monkeypatch):
    user_id = uuid.uuid4()
    student = IdentityUser(id=user_id, email="s@example.edu", roles=["student"])
    resolver = TargetResolver(FakeIdentity([student]), FakeAcademic([user_id]))
    result = resolver.resolve(CampaignTarget(kind="SECTION", section_id=uuid.uuid4()), "token")
    assert len(result) == 1
    assert result[0].user_id == user_id
    assert result[0].email == "s@example.edu"


def test_event_target_infers_student_user_id():
    user_id = uuid.uuid4()
    resolver = TargetResolver(FakeIdentity([]), FakeAcademic([]))
    result = resolver.resolve_event_targets({}, {"student_user_id": str(user_id)})
    assert result[0].user_id == user_id
