import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    permissions: list[str] = []


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    permissions: list[str] = []

    @field_validator("permissions", mode="before")
    @classmethod
    def permission_codes(cls, value):
        if value is None:
            return []
        return [item.code if hasattr(item, "code") else str(item) for item in value]


class PermissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    description: str | None
