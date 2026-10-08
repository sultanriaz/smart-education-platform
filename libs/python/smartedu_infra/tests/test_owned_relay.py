import asyncio
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import JSON, DateTime, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from smartedu_infra.runtime import MAX_RELAY_ATTEMPTS, RelayState, relay_once


class Base(DeclarativeBase):
    pass


class Event(RelayState, Base):
    __tablename__ = "test_events"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    aggregate_id: Mapped[str] = mapped_column(String)
    event_type: Mapped[str] = mapped_column(String)
    payload: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Bus:
    def __init__(self, fail=False):
        self.fail, self.events = fail, []

    async def publish(self, event):
        if self.fail:
            raise ConnectionError("sensitive broker credentials must not be retained")
        self.events.append(event)


def test_confirmation_marks_published_and_restart_does_not_resend(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'owned.db'}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    event_id = str(uuid4())
    with factory.begin() as db:
        db.add(
            Event(
                id=event_id,
                aggregate_id=str(uuid4()),
                event_type="test.changed",
                payload={"value": 1},
                created_at=datetime.now(UTC),
            )
        )
    bus = Bus()
    assert asyncio.run(relay_once(bus, factory, Event, "test-service"))
    assert not asyncio.run(relay_once(bus, factory, Event, "test-service"))
    assert str(bus.events[0].event_id) == event_id
    with factory() as db:
        assert db.get(Event, event_id).published_at is not None


def test_failure_backoff_is_persisted_and_exhaustion_quarantines(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'owned.db'}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine)
    event_id = str(uuid4())
    with factory.begin() as db:
        db.add(
            Event(
                id=event_id,
                aggregate_id=str(uuid4()),
                event_type="test.changed",
                payload={},
                created_at=datetime.now(UTC),
            )
        )
    assert asyncio.run(relay_once(Bus(True), factory, Event, "test-service"))
    with factory.begin() as db:
        row = db.get(Event, event_id)
        assert row.published_at is None and row.relay_attempts == 1
        assert row.relay_error == "ConnectionError"
        assert row.relay_retry_at is not None
        row.relay_attempts, row.relay_retry_at = (
            MAX_RELAY_ATTEMPTS,
            datetime.now(UTC) - timedelta(seconds=1),
        )
    assert not asyncio.run(relay_once(Bus(), factory, Event, "test-service"))
