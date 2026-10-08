from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.domain.models import Equipment, Facility, FacilityEquipment, OutboxEvent
from app.repositories.facility_repository import FacilityRepository
from app.repositories.outbox_repository import OutboxRepository
from app.schemas.facility import (
    EquipmentCreate,
    FacilityCreate,
    FacilityEquipmentAssign,
    FacilityUpdate,
)
from app.security.auth import Principal


class FacilityService:
    def __init__(self, db: Session):
        self.db = db
        self.facilities = FacilityRepository(db)
        self.outbox = OutboxRepository(db)

    def create_facility(self, payload: FacilityCreate, actor: Principal) -> Facility:
        if self.facilities.get_facility_by_code(payload.code):
            raise ConflictError("Facility code already exists", code="facility_code_exists")
        facility = Facility(
            code=payload.code.upper(),
            name=payload.name.strip(),
            kind=payload.kind,
            description=payload.description,
            building=payload.building,
            floor=payload.floor,
            capacity=payload.capacity,
            is_bookable=payload.is_bookable,
            metadata_json=payload.metadata,
            created_by_user_id=actor.user_id,
        )
        try:
            self.facilities.add_facility(facility)
            self.outbox.add_event(
                OutboxEvent(
                    event_type="facility.created",
                    aggregate_type="facility",
                    aggregate_id=facility.id,
                    payload={
                        "facility_id": str(facility.id),
                        "code": facility.code,
                        "name": facility.name,
                    },
                    targets={},
                )
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return self.facilities.get_facility(facility.id) or facility

    def update_facility(
        self, facility_id: uuid.UUID, payload: FacilityUpdate, actor: Principal
    ) -> Facility:
        facility = self.facilities.get_facility(facility_id)
        if not facility:
            raise NotFoundError("Facility not found", code="facility_not_found")
        changes = payload.model_dump(exclude_unset=True)
        if "metadata" in changes:
            changes["metadata_json"] = changes.pop("metadata")
        for key, value in changes.items():
            setattr(facility, key, value)
        try:
            self.db.add(facility)
            self.outbox.add_event(
                OutboxEvent(
                    event_type="facility.updated",
                    aggregate_type="facility",
                    aggregate_id=facility.id,
                    payload={"facility_id": str(facility.id), "changes": list(changes.keys())},
                    targets={},
                )
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return self.facilities.get_facility(facility.id) or facility

    def get_facility(self, facility_id: uuid.UUID) -> Facility:
        facility = self.facilities.get_facility(facility_id)
        if not facility:
            raise NotFoundError("Facility not found", code="facility_not_found")
        return facility

    def create_equipment(self, payload: EquipmentCreate) -> Equipment:
        if self.facilities.get_equipment_by_code(payload.code):
            raise ConflictError("Equipment code already exists", code="equipment_code_exists")
        equipment = Equipment(
            code=payload.code.upper(), name=payload.name.strip(), description=payload.description
        )
        try:
            self.facilities.add_equipment(equipment)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return equipment

    def assign_equipment(
        self, facility_id: uuid.UUID, payload: FacilityEquipmentAssign
    ) -> FacilityEquipment:
        facility = self.get_facility(facility_id)
        equipment = self.facilities.get_equipment(payload.equipment_id)
        if not equipment:
            raise NotFoundError("Equipment not found", code="equipment_not_found")
        link = self.facilities.get_facility_equipment(facility.id, equipment.id)
        try:
            if link:
                link.quantity = payload.quantity
                self.db.add(link)
            else:
                link = FacilityEquipment(
                    facility_id=facility.id, equipment_id=equipment.id, quantity=payload.quantity
                )
                self.facilities.add_facility_equipment(link)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return link
