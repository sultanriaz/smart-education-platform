from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime

from smartedu_infra.runtime import RelayState
from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None


def utcnow() -> datetime:
    return datetime.now(UTC)


class ResourceType(enum.StrEnum):
    FILE = "FILE"
    LINK = "LINK"
    VIDEO = "VIDEO"
    NOTE = "NOTE"


class ResourceStatus(enum.StrEnum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class TargetType(enum.StrEnum):
    SECTION = "SECTION"
    COURSE = "COURSE"


class AccessAction(enum.StrEnum):
    VIEW = "VIEW"
    DOWNLOAD = "DOWNLOAD"


class ResourceCategory(Base):
    __tablename__ = "resource_categories"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(240), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    resource_type: Mapped[ResourceType] = mapped_column(Enum(ResourceType, name="resource_type"))
    status: Mapped[ResourceStatus] = mapped_column(
        Enum(ResourceStatus, name="resource_status"), default=ResourceStatus.DRAFT, index=True
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("resource_categories.id", ondelete="SET NULL"), nullable=True
    )
    creator_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    category: Mapped[ResourceCategory | None] = relationship()
    targets: Mapped[list[ResourceTarget]] = relationship(
        back_populates="resource", cascade="all, delete-orphan", lazy="selectin"
    )
    versions: Mapped[list[ResourceVersion]] = relationship(
        back_populates="resource",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ResourceVersion.version_number",
    )


class ResourceTarget(Base):
    __tablename__ = "resource_targets"
    __table_args__ = (
        UniqueConstraint("resource_id", "target_type", "target_id", name="uq_resource_target"),
        Index("ix_resource_targets_lookup", "target_type", "target_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("learning_resources.id", ondelete="CASCADE"), index=True
    )
    target_type: Mapped[TargetType] = mapped_column(Enum(TargetType, name="target_type"))
    target_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True))

    resource: Mapped[LearningResource] = relationship(back_populates="targets")


class ResourceVersion(Base):
    __tablename__ = "resource_versions"
    __table_args__ = (
        UniqueConstraint("resource_id", "version_number", name="uq_resource_version_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("learning_resources.id", ondelete="CASCADE"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer)
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True))
    text_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    storage_key: Mapped[str | None] = mapped_column(String(500), nullable=True, unique=True)
    original_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    change_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    resource: Mapped[LearningResource] = relationship(back_populates="versions")


class ResourceAccessLog(Base):
    __tablename__ = "resource_access_logs"
    __table_args__ = (Index("ix_resource_access_user_resource", "user_id", "resource_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("learning_resources.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    action: Mapped[AccessAction] = mapped_column(Enum(AccessAction, name="access_action"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )


class OutboxEvent(RelayState, Base):
    __tablename__ = "outbox_events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(160), index=True)
    aggregate_type: Mapped[str] = mapped_column(String(80))
    aggregate_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )


class FileDeletionTask(Base):
    """Durable request to erase an unreferenced file object after DB commit."""
    __tablename__ = "file_deletion_tasks"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    storage_key: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    resource_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    actor_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    next_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[str | None] = mapped_column(String(160), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class FileOperationAudit(Base):
    """Security audit contains object hash, but never file bytes or signed URLs."""
    __tablename__ = "file_operation_audits"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resource_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False, index=True)
    version_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    actor_user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    operation: Mapped[str] = mapped_column(String(24), nullable=False)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SelfLearningSubject(Base):
    """Student-curated subjects across departments for personalized learning."""
    __tablename__ = "self_learning_subjects"
    __table_args__ = (
        UniqueConstraint("student_id", "name", name="uq_self_learning_student_subject"),
        Index("ix_self_learning_subjects_student", "student_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    department: Mapped[str] = mapped_column(String(150), nullable=False, default="General")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    color_hex: Mapped[str] = mapped_column(String(16), default="#4F46E5")
    icon_name: Mapped[str] = mapped_column(String(50), default="book-open")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    materials: Mapped[list[SelfLearningMaterial]] = relationship(
        "SelfLearningMaterial",
        back_populates="subject",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    tests: Mapped[list[SelfLearningTest]] = relationship(
        "SelfLearningTest",
        back_populates="subject",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SelfLearningMaterial(Base):
    """Ingested multi-format documents (PDF, DOCX, PPTX, TXT) associated with a student subject."""
    __tablename__ = "self_learning_materials"
    __table_args__ = (
        Index("ix_self_learning_materials_student", "student_id"),
        Index("ix_self_learning_materials_subject", "subject_id"),
        Index("ix_self_learning_materials_hash", "student_id", "file_hash"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("self_learning_subjects.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    extracted_topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(30), default="PROCESSED")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    subject: Mapped[SelfLearningSubject] = relationship("SelfLearningSubject", back_populates="materials")
    chunks: Mapped[list[SelfLearningChunk]] = relationship(
        "SelfLearningChunk",
        back_populates="material",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class SelfLearningChunk(Base):
    """Vectorized semantic chunks with text-embedding-004 (768 dimensions) for RAG."""
    __tablename__ = "self_learning_chunks"
    __table_args__ = (
        Index("ix_self_learning_chunks_lookup", "student_id", "subject_id"),
        Index("ix_self_learning_chunks_material", "material_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    material_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("self_learning_materials.id", ondelete="CASCADE"), nullable=False
    )
    subject_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("self_learning_subjects.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    topic_tag: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding = mapped_column(Vector(768) if Vector is not None else JSON, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    material: Mapped[SelfLearningMaterial] = relationship("SelfLearningMaterial", back_populates="chunks")


class SelfLearningTest(Base):
    """Generated self-learning assessment tests with Bloom's taxonomy calibration."""
    __tablename__ = "self_learning_tests"
    __table_args__ = (
        Index("ix_self_learning_tests_student", "student_id"),
        Index("ix_self_learning_tests_subject", "subject_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("self_learning_subjects.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(30), default="mixed")
    target_topics: Mapped[list[str]] = mapped_column(JSON, default=list)
    total_questions: Mapped[int] = mapped_column(Integer, default=10)
    status: Mapped[str] = mapped_column(String(30), default="COMPLETED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    subject: Mapped[SelfLearningSubject] = relationship("SelfLearningSubject", back_populates="tests")
    questions: Mapped[list[SelfLearningQuestion]] = relationship(
        "SelfLearningQuestion",
        back_populates="test",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="SelfLearningQuestion.question_number",
    )
    submissions: Mapped[list[SelfLearningTestSubmission]] = relationship(
        "SelfLearningTestSubmission",
        back_populates="test",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="SelfLearningTestSubmission.created_at.desc()",
    )


class SelfLearningQuestion(Base):
    """MCQ question item with options, Bloom's level, LaTeX formula, and step-by-step solver."""
    __tablename__ = "self_learning_questions"
    __table_args__ = (
        Index("ix_self_learning_questions_test", "test_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("self_learning_tests.id", ondelete="CASCADE"), nullable=False
    )
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict[str, str]] = mapped_column(JSON, nullable=False)  # {"A": ..., "B": ..., "C": ..., "D": ...}
    correct_option: Mapped[str] = mapped_column(String(10), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    bloom_level: Mapped[str] = mapped_column(String(50), default="UNDERSTAND")
    difficulty: Mapped[str] = mapped_column(String(30), default="medium")
    is_quantitative: Mapped[bool] = mapped_column(Boolean, default=False)
    formula_latex: Mapped[str | None] = mapped_column(Text, nullable=True)
    step_by_step_solution: Mapped[list[str]] = mapped_column(JSON, default=list)
    topic_tag: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    test: Mapped[SelfLearningTest] = relationship("SelfLearningTest", back_populates="questions")


class SelfLearningTestSubmission(Base):
    """Graded submission for a self-learning test attempt with real-time feedback & diffs."""
    __tablename__ = "self_learning_test_submissions"
    __table_args__ = (
        Index("ix_self_learning_submissions_test", "test_id"),
        Index("ix_self_learning_submissions_student", "student_id"),
        Index("ix_self_learning_submissions_subject", "subject_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("self_learning_tests.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    subject_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("self_learning_subjects.id", ondelete="CASCADE"), nullable=False
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    answers: Mapped[dict] = mapped_column(JSON, default=dict)
    detailed_results: Mapped[list[dict]] = mapped_column(JSON, default=list)
    topic_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    time_taken_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )

    test: Mapped[SelfLearningTest] = relationship("SelfLearningTest", back_populates="submissions")
    subject: Mapped[SelfLearningSubject] = relationship("SelfLearningSubject")
