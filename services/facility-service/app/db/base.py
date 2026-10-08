from __future__ import annotations

from app.db.base_class import Base
from app.domain.models import (  # noqa: F401
    Booking,
    BookingHistory,
    Equipment,
    ExternalReservation,
    Facility,
    FacilityBlock,
    FacilityEquipment,
    OutboxEvent,
)

__all__ = ["Base"]
