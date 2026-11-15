from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SubjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Subject title or course name")
    code: str | None = Field(None, max_length=50, description="Subject course code, e.g. CS-401")
    department: str = Field(
        default="General",
        max_length=150,
        description="Academic department e.g. Computer Science, Law, Health Sciences",
    )
    description: str | None = Field(None, max_length=1000)
    color_hex: str = Field(default="#4F46E5", max_length=16)
    icon_name: str = Field(default="book-open", max_length=50)


class SubjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=200)
    code: str | None = Field(None, max_length=50)
    department: str | None = Field(None, max_length=150)
    description: str | None = Field(None, max_length=1000)
    color_hex: str | None = Field(None, max_length=16)
    icon_name: str | None = Field(None, max_length=50)


class SubjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    name: str
    code: str | None = None
    department: str
    description: str | None = None
    color_hex: str
    icon_name: str
    materials_count: int = 0
    created_at: datetime
    updated_at: datetime


class MaterialOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    subject_id: uuid.UUID
    title: str
    file_name: str
    file_type: str
    mime_type: str
    file_size_bytes: int
    file_hash: str
    extracted_topics: list[str] = Field(default_factory=list)
    status: str
    created_at: datetime
    chunks_count: int = 0


class TopicsOut(BaseModel):
    material_id: uuid.UUID
    title: str
    topics: list[str]


class ChunkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    material_id: uuid.UUID
    subject_id: uuid.UUID
    chunk_index: int
    topic_tag: str | None = None
    content: str
    similarity: float | None = None
    metadata_json: dict = Field(default_factory=dict)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Question or search query for semantic vector search")
    subject_id: uuid.UUID | None = Field(None, description="Optional subject ID filter")
    limit: int = Field(default=5, ge=1, le=50)


class SearchResult(BaseModel):
    query: str
    results: list[ChunkOut]


class StorageQuotaOut(BaseModel):
    student_id: uuid.UUID
    used_bytes: int
    total_quota_bytes: int
    used_percentage: float
    materials_count: int
