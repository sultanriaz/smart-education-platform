from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.clients.academic import AcademicClient
from app.clients.identity import IdentityClient
from app.schemas.notification import CampaignTarget, DirectRecipient


@dataclass(frozen=True, slots=True)
class ResolvedRecipient:
    user_id: uuid.UUID
    email: str | None = None


class TargetResolver:
    def __init__(
        self, identity: IdentityClient | None = None, academic: AcademicClient | None = None
    ):
        self.identity = identity or IdentityClient()
        self.academic = academic or AcademicClient()

    def resolve(
        self, target: CampaignTarget, forwarded_token: str | None = None
    ) -> list[ResolvedRecipient]:
        if target.kind == "DIRECT":
            return self._dedupe(
                [
                    ResolvedRecipient(
                        user_id=item.user_id, email=str(item.email) if item.email else None
                    )
                    for item in (target.recipients or [])
                ]
            )

        if target.kind == "ROLE":
            users = self.identity.list_users_by_role(target.role or "", forwarded_token)
            return self._dedupe(
                [ResolvedRecipient(u.id, str(u.email) if u.email else None) for u in users]
            )

        member_ids = self.academic.list_section_member_ids(target.section_id, forwarded_token)
        if not member_ids:
            return []
        by_id = {}
        try:
            by_id = {u.id: u for u in self.identity.get_users(member_ids)}
        except Exception:
            by_id = {}
        return self._dedupe(
            [
                ResolvedRecipient(
                    user_id=user_id,
                    email=str(by_id[user_id].email)
                    if by_id.get(user_id) and by_id[user_id].email
                    else None,
                )
                for user_id in member_ids
            ]
        )

    @staticmethod
    def _dedupe(values: list[ResolvedRecipient]) -> list[ResolvedRecipient]:
        result: dict[uuid.UUID, ResolvedRecipient] = {}
        for value in values:
            existing = result.get(value.user_id)
            if existing is None or (existing.email is None and value.email is not None):
                result[value.user_id] = value
        return list(result.values())

    def resolve_event_targets(self, targets: dict, payload: dict) -> list[ResolvedRecipient]:
        direct: list[DirectRecipient] = []
        email_by_user = (
            targets.get("emails", {}) if isinstance(targets.get("emails", {}), dict) else {}
        )
        raw_user_ids = targets.get("user_ids", [])
        if isinstance(raw_user_ids, list):
            for raw in raw_user_ids:
                user_id = uuid.UUID(str(raw))
                direct.append(
                    DirectRecipient(user_id=user_id, email=email_by_user.get(str(user_id)))
                )

        if not direct and payload.get("student_user_id"):
            direct.append(DirectRecipient(user_id=uuid.UUID(str(payload["student_user_id"]))))

        teacher = payload.get("teacher_user_id")
        if teacher:
            direct.append(DirectRecipient(user_id=uuid.UUID(str(teacher))))

        section_raw = targets.get("section_id") or payload.get("section_id")
        resolved = []
        if direct:
            resolved.extend(self.resolve(CampaignTarget(kind="DIRECT", recipients=direct)))
        if section_raw and not direct:
            resolved.extend(
                self.resolve(CampaignTarget(kind="SECTION", section_id=uuid.UUID(str(section_raw))))
            )
        for target in payload.get("targets", []):
            if isinstance(target, dict) and target.get("type") == "SECTION":
                resolved.extend(
                    self.resolve(CampaignTarget(kind="SECTION", section_id=uuid.UUID(target["id"])))
                )
            elif isinstance(target, dict) and target.get("type") == "COURSE":
                members = self.academic.list_course_member_ids(uuid.UUID(target["id"]))
                users = {user.id: user for user in self.identity.get_users(members)}
                resolved.extend(
                    ResolvedRecipient(
                        user_id=user_id,
                        email=str(users[user_id].email) if user_id in users else None,
                    )
                    for user_id in members
                )
        return self._dedupe(resolved)
