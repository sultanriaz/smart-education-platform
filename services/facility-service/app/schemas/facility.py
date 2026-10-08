from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

FACILITY_KINDS = {"ROOM", "LAB", "HALL", "AUDITORIUM", "SPORTS", "OTHER"}


class FacilityCreate(BaseModel):
    code: str = Field(min_length=2, max_length=80)
    name: str = Field(min_length=2, max_length=160)
    kind: str
    description: str | None = None
    building: str | None = Field(default=None, max_length=120)
    floor: str | None = Field(default=None, max_length=40)
    capacity: int = Field(gt=0, le=100000)
    is_bookable: bool = True
    metadata: dict = Field(default_factory=dict)

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
    metadata: dict = Field(alias="metadata_json")
    created_by_user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class FacilityDetailOut(FacilityOut):
    equipment: list[FacilityEquipmentOut] = Field(default_factory=list)
