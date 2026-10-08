from __future__ import annotations

import os
import threading
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.domain.models import Booking, Facility
from app.schemas.booking import BookingCreate
from app.security.auth import Principal
from app.services.booking_service import BookingService

POSTGRES_URL = os.getenv("FACILITY_TEST_POSTGRES_URL")
pytestmark = pytest.mark.skipif(
    not POSTGRES_URL, reason="FACILITY_TEST_POSTGRES_URL not configured"
)


def test_concurrent_requests_for_same_slot_have_one_winner():
    engine = create_engine(POSTGRES_URL, pool_pre_ping=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    admin_id = uuid.uuid4()
    with Session() as db:
        facility = Facility(
            code="RACE-1",
            name="Race Room",
            kind="ROOM",
            capacity=20,
            is_active=True,
            is_bookable=True,
            metadata_json={},
            created_by_user_id=admin_id,
        )
        db.add(facility)
        db.commit()
        facility_id = facility.id

    start = datetime.now(UTC) + timedelta(days=3)
    end = start + timedelta(hours=1)
    barrier = threading.Barrier(2)
    results = []

    def worker():
        with Session() as db:
            actor = Principal(uuid.uuid4(), frozenset({"student"}), "")
            service = BookingService(db)
            barrier.wait()
            try:
                service.create_booking(
                    BookingCreate(
                        facility_id=facility_id,
                        purpose="Race",
                        starts_at=start,
                        ends_at=end,
                        attendees=2,
                    ),
                    actor,
                )
                results.append("ok")
            except Exception:
                results.append("conflict")

    threads = [threading.Thread(target=worker), threading.Thread(target=worker)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results.count("ok") == 1
    with Session() as db:
        assert db.query(Booking).count() == 1
    Base.metadata.drop_all(engine)
