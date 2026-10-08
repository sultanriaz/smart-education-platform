from __future__ import annotations

import os
import threading

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.schemas.notification import InternalEventIn
from app.services.event_service import EventService

TEST_POSTGRES_URL = os.getenv("TEST_POSTGRES_URL")
pytestmark = pytest.mark.skipif(
    not TEST_POSTGRES_URL, reason="TEST_POSTGRES_URL is required for PostgreSQL race test"
)


def test_concurrent_inbox_ingest_is_idempotent():
    engine = create_engine(TEST_POSTGRES_URL, pool_pre_ping=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    barrier = threading.Barrier(2)
    results = []
    errors = []

    def worker():
        try:
            with SessionLocal() as db:
                barrier.wait(timeout=5)
                event, duplicate = EventService(db).ingest(
                    InternalEventIn(
                        event_id="concurrent-event",
                        source_service="scheduling",
                        event_type="schedule.updated",
                        targets={"user_ids": []},
                    )
                )
                results.append((str(event.id), duplicate))
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert not errors
    assert len(results) == 2
    assert len({item[0] for item in results}) == 1
    assert sorted(item[1] for item in results) == [False, True]
    Base.metadata.drop_all(engine)
