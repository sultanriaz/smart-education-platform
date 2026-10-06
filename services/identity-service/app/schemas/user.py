import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=8, max_length=128)


class AdminUserCreate(UserRegister):
    role: str = "student"


class UserSelfUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=160)


class AdminUserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=160)
    is_active: bool | None = None
    is_verified: bool | None = None
    roles: list[str] | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool
    is_verified: bool
    roles: list[str] = []
    created_at: datetime

    @field_validator("roles", mode="before")
    @classmethod
    def role_names(cls, value):
        if value is None:
            return []
        return [item.name if hasattr(item, "name") else str(item) for item in value]
