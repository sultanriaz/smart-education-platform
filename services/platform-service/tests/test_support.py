from __future__ import annotations

import uuid

import pytest

from app.core.errors import ForbiddenError
from app.schemas.support import MessageCreate, TicketCreate, TicketUpdateAdmin


def test_ticket_lifecycle(platform):
    user = uuid.uuid4()
    admin = uuid.uuid4()

    ticket = platform.create_ticket(
        TicketCreate(
            subject="Cannot view timetable",
            description="My weekly timetable is empty.",
            category="SCHEDULING",
            priority="HIGH",
        ),
        user,
    )
    assert ticket.status == "OPEN"
    assert ticket.ticket_number.startswith("TKT-")

    message = platform.add_message(
        ticket.id,
        MessageCreate(body="Additional details", is_internal=False),
        user,
        False,
    )
    assert message.ticket_id == ticket.id

    updated = platform.update_ticket_admin(
        ticket.id,
        TicketUpdateAdmin(
            status="RESOLVED",
            assigned_to_user_id=admin,
        ),
    )
    assert updated.status == "RESOLVED"
    assert updated.assigned_to_user_id == admin

    closed = platform.update_ticket_admin(
        ticket.id,
        TicketUpdateAdmin(status="CLOSED"),
    )
    assert closed.status == "CLOSED"
    assert closed.closed_at is not None


def test_user_cannot_read_others_ticket(platform):
    owner = uuid.uuid4()
    other = uuid.uuid4()
    ticket = platform.create_ticket(
        TicketCreate(subject="Issue", description="Something is not working"),
        owner,
    )
    with pytest.raises(ForbiddenError):
        platform.get_ticket(ticket.id, other, False)


def test_user_cannot_add_internal_note(platform):
    user = uuid.uuid4()
    ticket = platform.create_ticket(
        TicketCreate(subject="Issue", description="Something is not working"),
        user,
    )
    with pytest.raises(ForbiddenError):
        platform.add_message(
            ticket.id,
            MessageCreate(body="private", is_internal=True),
            user,
            False,
        )
