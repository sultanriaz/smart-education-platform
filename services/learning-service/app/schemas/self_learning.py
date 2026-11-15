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


# =============================================================================
# PHASE 2: LANGGRAPH & GEMINI MCQ ENGINE SCHEMAS
# =============================================================================

class QuestionItem(BaseModel):
    question_number: int = Field(..., ge=1)
    question_text: str = Field(..., min_length=5)
    options: dict[str, str] = Field(
        ...,
        description="Four distinct options with keys 'A', 'B', 'C', 'D'",
    )
    correct_option: str = Field(..., pattern=r"^[ABCD]$")
    explanation: str = Field(..., min_length=5, description="Pedagogical explanation of why the correct option is right")
    bloom_level: str = Field(default="UNDERSTAND", description="Bloom's Taxonomy Level: REMEMBER, UNDERSTAND, APPLY, ANALYZE, EVALUATE, CREATE")
    difficulty: str = Field(default="medium", description="Difficulty calibration: basic, medium, hard")
    is_quantitative: bool = Field(default=False)
    formula_latex: str | None = Field(None, description="Explicit LaTeX formula for quantitative/algorithmic questions")
    step_by_step_solution: list[str] = Field(default_factory=list, description="Step-by-step intermediate proof or solution steps")
    topic_tag: str | None = None


class QuestionOut(QuestionItem):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    test_id: uuid.UUID
    created_at: datetime


class TestGenerateRequest(BaseModel):
    subject_id: uuid.UUID
    count: int = Field(default=10, ge=5, le=30, description="Number of MCQs to generate (5 to 30)")
    difficulty: str = Field(default="mixed", description="Difficulty: 'basic', 'medium', 'hard', or 'mixed'")
    topics: list[str] | None = Field(default=None, description="Optional topic or chapter filters")
    title: str | None = Field(default=None, description="Optional custom test title")


class TestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_id: uuid.UUID
    subject_id: uuid.UUID
    title: str
    difficulty: str
    target_topics: list[str] = Field(default_factory=list)
    total_questions: int
    status: str
    created_at: datetime
    updated_at: datetime
    questions: list[QuestionOut] = Field(default_factory=list)

