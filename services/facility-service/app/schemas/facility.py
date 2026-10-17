from __future__ import annotations

import uuid
from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

FACILITY_KINDS = {"ROOM", "LAB", "HALL", "AUDITORIUM", "SPORTS", "OTHER"}


def validate_hours(opens: time | None, closes: time | None, zone: str) -> None:
    if (opens is None) != (closes is None):
        raise ValueError("Both opening and closing time must be supplied together")
    if opens is not None and (opens.tzinfo or closes.tzinfo or opens >= closes):
        raise ValueError("Operating hours must be same-day local times with opening before closing")
    try:
        ZoneInfo(zone)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError("Unknown operating timezone") from exc


class FacilityCreate(BaseModel):
    code: str = Field(min_length=2, max_length=80)
    name: str = Field(min_length=2, max_length=160)
    kind: str
    description: str | None = None
    building: str | None = Field(default=None, max_length=120)
    floor: str | None = Field(default=None, max_length=40)
    capacity: int = Field(gt=0, le=100000)
    is_bookable: bool = True
    opens_at_local: time | None = None
    closes_at_local: time | None = None
    operating_timezone: str = Field(default="UTC", max_length=64)
    metadata: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def valid_operating_hours(self):
        validate_hours(self.opens_at_local, self.closes_at_local, self.operating_timezone)
        return self

    @field_validator("kind")
    @classmethod
    def valid_kind(cls, value: str) -> str:
        value = value.upper()
        if value not in FACILITY_KINDS:
            raise ValueError("Unsupported facility kind")
        return value


class FacilityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    kind: str | None = None
    description: str | None = None
    building: str | None = Field(default=None, max_length=120)
    floor: str | None = Field(default=None, max_length=40)
    capacity: int | None = Field(default=None, gt=0, le=100000)
    is_active: bool | None = None
    is_bookable: bool | None = None
    opens_at_local: time | None = None
    closes_at_local: time | None = None
    operating_timezone: str | None = Field(default=None, max_length=64)
    metadata: dict | None = None

    @field_validator("kind")
    @classmethod
    def valid_kind(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.upper()
        if value not in FACILITY_KINDS:
            raise ValueError("Unsupported facility kind")
        return value


class EquipmentCreate(BaseModel):
    code: str = Field(min_length=2, max_length=80)
    name: str = Field(min_length=2, max_length=160)
    description: str | None = None


class EquipmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: uuid.UUID
    code: str
    name: str
    description: str | None
    is_active: bool


class FacilityEquipmentAssign(BaseModel):
    equipment_id: uuid.UUID
    quantity: int = Field(gt=0, le=100000)


class FacilityEquipmentOut(BaseModel):
    equipment_id: uuid.UUID
    code: str
    name: str
    quantity: int


class FacilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: uuid.UUID
    code: str
    name: str
    kind: str
    description: str | None
    building: str | None
    floor: str | None
    capacity: int
    is_active: bool
    is_bookable: bool
    opens_at_local: time | None
    closes_at_local: time | None
    operating_timezone: str
    metadata: dict = Field(alias="metadata_json")
    created_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class FacilityDetailOut(FacilityOut):
    equipment: list[FacilityEquipmentOut] = Field(default_factory=list)
