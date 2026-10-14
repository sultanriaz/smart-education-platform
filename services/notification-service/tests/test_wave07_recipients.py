from __future__ import annotations

import uuid
from app.clients.identity import IdentityUser
from app.services.target_resolver import TargetResolver


class Users:
    def __init__(self, data): self.data = data
    def get_users(self, ids, forwarded_token=None): return [u for u in self.data if u.id in ids]
    def list_users_by_role(self, role, forwarded_token=None): return [u for u in self.data if role in u.roles]


class Sections:
    def __init__(self, members): self.members = members
    def list_section_member_ids(self, _section, forwarded_token=None): return self.members


def test_schedule_notice_expands_section_even_when_teacher_directly_targeted():
    teacher, student = uuid.uuid4(), uuid.uuid4()
    r = TargetResolver(Users([IdentityUser(id=teacher, roles=["teacher"]), IdentityUser(id=student, roles=["student"])]), Sections([student]))
    result = r.resolve_event_targets({"user_ids": [str(teacher)], "section_id": str(uuid.uuid4())}, {"schedule_id": str(uuid.uuid4()), "teacher_user_id": str(teacher)})
    assert {recipient.user_id for recipient in result} == {teacher, student}


def test_booking_request_adds_admin_approvers_without_dropping_requester():
    requester, admin, stranger = (uuid.uuid4() for _ in range(3))
    identity = Users([IdentityUser(id=admin, roles=["admin"]), IdentityUser(id=stranger, roles=["student"])])
    r = TargetResolver(identity, Sections([]))
    result = r.resolve_event_targets({"user_ids": [str(requester)], "roles": ["admin"]}, {"booking_id": str(uuid.uuid4())})
    assert {recipient.user_id for recipient in result} == {requester, admin}
