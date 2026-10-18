"""Bounded security activity presentation; never expose credential-bearing details."""
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SecurityActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID | None
    action: str
    outcome: str
    ip_address: str | None
    details: dict
    request_id: str | None
    correlation_id: str | None
    trace_id: str | None
    created_at: datetime
