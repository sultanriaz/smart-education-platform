from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=5)
    category: str = Field(default="GENERAL", max_length=80)
    priority: str = Field(default="MEDIUM", max_length=24)


class TicketUpdateAdmin(BaseModel):
    status: str | None = None
    priority: str | None = None
    assigned_to_user_id: uuid.UUID | None = None


class MessageCreate(BaseModel):
    body: str = Field(min_length=1)
    is_internal: bool = False


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    author_user_id: uuid.UUID
    body: str
    is_internal: bool
    created_at: datetime


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ticket_number: str
    created_by_user_id: uuid.UUID
    assigned_to_user_id: uuid.UUID | None
    subject: str
    description: str
    category: str
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
