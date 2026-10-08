from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SearchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_service: str
    document_type: str
    document_id: str
    title: str
    body: str
    url_path: str | None
    metadata_json: dict
    updated_at: datetime
