from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.models import Equipment, Facility, FacilityEquipment


class FacilityRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_facility(self, facility: Facility) -> None:
        self.db.add(facility)
        self.db.flush()

    def get_facility(self, facility_id: uuid.UUID) -> Facility | None:
        return self.db.scalar(
            select(Facility)
            .options(
                selectinload(Facility.equipment_links).selectinload(FacilityEquipment.equipment)
            )
            .where(Facility.id == facility_id)
        )

    def get_facility_by_code(self, code: str) -> Facility | None:
        return self.db.scalar(select(Facility).where(Facility.code == code.upper()))

    def list_facilities(
        self, *, offset: int, limit: int, active_only: bool = False
    ) -> list[Facility]:
        stmt = select(Facility).order_by(Facility.code).offset(offset).limit(limit)
        if active_only:
            stmt = stmt.where(Facility.is_active.is_(True))
        return list(self.db.scalars(stmt).all())

    def add_equipment(self, equipment: Equipment) -> None:
        self.db.add(equipment)
        self.db.flush()

    def get_equipment(self, equipment_id: uuid.UUID) -> Equipment | None:
        return self.db.get(Equipment, equipment_id)

    def get_equipment_by_code(self, code: str) -> Equipment | None:
        return self.db.scalar(select(Equipment).where(Equipment.code == code.upper()))

    def list_equipment(self) -> list[Equipment]:
        return list(self.db.scalars(select(Equipment).order_by(Equipment.code)).all())

    def get_facility_equipment(
        self, facility_id: uuid.UUID, equipment_id: uuid.UUID
    ) -> FacilityEquipment | None:
        return self.db.scalar(
            select(FacilityEquipment).where(
                FacilityEquipment.facility_id == facility_id,
                FacilityEquipment.equipment_id == equipment_id,
            )
        )

    def add_facility_equipment(self, link: FacilityEquipment) -> None:
        self.db.add(link)
        self.db.flush()
