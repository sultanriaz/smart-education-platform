import uuid

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    description: str | None = Field(default=None, max_length=255)
    permissions: list[str] = Field(default_factory=list, max_length=100)

    @field_validator("name")
    @classmethod
    def valid_custom_role_name(cls, value: str) -> str:
        import re
        value = value.strip().lower()
        if not re.fullmatch(r"[a-z][a-z0-9_-]{1,49}", value):
            raise ValueError("Use 2-50 lower-case letters, numbers, underscores or hyphens")
        if value in {"admin", "teacher", "student"}:
            raise ValueError("Built-in role names are reserved")
        return value

    @field_validator("permissions")
    @classmethod
    def unique_permission_codes(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)) or any(not code or code != code.strip() for code in value):
            raise ValueError("Permission codes must be unique and non-empty")
        return value


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
