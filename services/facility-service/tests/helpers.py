from __future__ import annotations

from app.domain.models import Facility
from app.security.auth import Principal


def make_facility(db, actor: Principal, *, code="R101", capacity=40, bookable=True):
    facility = Facility(
        code=code,
        name=f"Room {code}",
        kind="ROOM",
        building="Main",
        floor="1",
        capacity=capacity,
        is_active=True,
        is_bookable=bookable,
        metadata_json={},
        created_by_user_id=actor.user_id,
    )
    db.add(facility)
    db.commit()
    db.refresh(facility)
    return facility
