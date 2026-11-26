from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class StrictRequestModel(BaseModel):
    """Base for security-sensitive request bodies: reject unexpected fields."""

    model_config = ConfigDict(extra="forbid")
