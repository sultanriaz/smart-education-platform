from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import DomainError
from app.domain.entities.models import (
    SelfLearningChunk,
    SelfLearningMaterial,
    SelfLearningQuestion,
    SelfLearningSubject,
    SelfLearningTest,
    SelfLearningTestSubmission,
)
from app.schemas.self_learning import (
    ChunkOut,
    MaterialOut,
    QuestionEvaluationDetail,
    QuestionOut,
    SearchRequest,
    SearchResult,
    StorageQuotaOut,
    SubjectCreate,
    SubjectMasteryOut,
    SubjectOut,
    SubjectUpdate,
    TestGenerateRequest,
    TestOut,
    TestRegenerateRequest,
    TestResultOut,
    TestSubmitRequest,
    TopicMasteryDetail,
    TopicScore,
    TopicsOut,
)
from app.services.document_parser import (
    DocumentParsingError,
    chunk_text,
    compute_sha256,
    detect_file_type,
    extract_text,
)
from app.services.gemini_client import GeminiClient, get_gemini_client
from app.services.mcq_generator import LangGraphMCQEngine
from app.storage.base import StorageBackend

logger = logging.getLogger("learning-service.self-learning")


class SelfLearningError(DomainError):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


class SelfLearningService:
    def __init__(
        self,
        db: Session,
        storage: StorageBackend,
        gemini: GeminiClient | None = None,
    ):
        self.db = db
        self.storage = storage
        self.gemini = gemini or get_gemini_client()
        self.max_quota_bytes = settings.STUDENT_STORAGE_QUOTA_BYTES

    # =========================================================================
    # SUBJECT ENGINE
    # =========================================================================

    def create_subject(self, student_id: uuid.UUID, payload: SubjectCreate) -> SubjectOut:
        """Create a custom subject for a student across any academic department."""
        existing = (
            self.db.query(SelfLearningSubject)
            .filter(
                SelfLearningSubject.student_id == student_id,
                func.lower(SelfLearningSubject.name) == payload.name.strip().lower(),
            )
            .first()
        )
        if existing:
            raise SelfLearningError(
                f"Subject '{payload.name.strip()}' already exists for this student.",
                status_code=400,
            )

        subject = SelfLearningSubject(
            student_id=student_id,
            name=payload.name.strip(),
            code=payload.code.strip() if payload.code else None,
            department=payload.department.strip() if payload.department else "General",
            description=payload.description.strip() if payload.description else None,
            color_hex=payload.color_hex or "#4F46E5",
            icon_name=payload.icon_name or "book-open",
        )
        self.db.add(subject)
        self.db.commit()
        self.db.refresh(subject)
        return self._subject_to_out(subject, materials_count=0)

    def list_subjects(
        self, student_id: uuid.UUID, department: str | None = None
    ) -> list[SubjectOut]:
        """List all subjects created by the student, optionally filtered by department."""
        query = self.db.query(SelfLearningSubject).filter(
            SelfLearningSubject.student_id == student_id
        )
        if department:
            query = query.filter(
                func.lower(SelfLearningSubject.department) == department.strip().lower()
            )

        subjects = query.order_by(SelfLearningSubject.created_at.desc()).all()
        if not subjects:
            return []

        # Count materials per subject in one batch query
        subject_ids = [s.id for s in subjects]
        counts = dict(
            self.db.query(
                SelfLearningMaterial.subject_id,
                func.count(SelfLearningMaterial.id),
            )
            .filter(SelfLearningMaterial.subject_id.in_(subject_ids))
            .group_by(SelfLearningMaterial.subject_id)
            .all()
        )

        return [self._subject_to_out(s, materials_count=counts.get(s.id, 0)) for s in subjects]

    def get_subject(self, student_id: uuid.UUID, subject_id: uuid.UUID) -> SubjectOut:
        """Retrieve a specific subject belonging to the student."""
        subject = (
            self.db.query(SelfLearningSubject)
            .filter(
                SelfLearningSubject.id == subject_id,
                SelfLearningSubject.student_id == student_id,
            )
            .first()
        )
        if not subject:
            raise SelfLearningError("Subject not found.", status_code=404)

        materials_count = (
            self.db.query(func.count(SelfLearningMaterial.id))
            .filter(SelfLearningMaterial.subject_id == subject_id)
            .scalar()
            or 0
        )
        return self._subject_to_out(subject, materials_count=materials_count)

    def update_subject(
        self, student_id: uuid.UUID, subject_id: uuid.UUID, payload: SubjectUpdate
    ) -> SubjectOut:
        """Update properties of an existing custom subject."""
        subject = (
            self.db.query(SelfLearningSubject)
            .filter(
                SelfLearningSubject.id == subject_id,
                SelfLearningSubject.student_id == student_id,
            )
            .first()
        )
        if not subject:
            raise SelfLearningError("Subject not found.", status_code=404)

        if payload.name is not None and payload.name.strip():
            new_name = payload.name.strip()
            # Check unique constraint against other subjects of same student
            conflict = (
                self.db.query(SelfLearningSubject)
                .filter(
                    SelfLearningSubject.student_id == student_id,
                    SelfLearningSubject.id != subject_id,
                    func.lower(SelfLearningSubject.name) == new_name.lower(),
                )
                .first()
            )
            if conflict:
                raise SelfLearningError(
                    f"Another subject with name '{new_name}' already exists.", status_code=400
                )
            subject.name = new_name

        if payload.code is not None:
            subject.code = payload.code.strip() if payload.code else None
        if payload.department is not None:
            subject.department = payload.department.strip() or "General"
        if payload.description is not None:
            subject.description = payload.description.strip() if payload.description else None
        if payload.color_hex is not None:
            subject.color_hex = payload.color_hex.strip()
        if payload.icon_name is not None:
            subject.icon_name = payload.icon_name.strip()

        self.db.commit()
        self.db.refresh(subject)

        materials_count = (
            self.db.query(func.count(SelfLearningMaterial.id))
            .filter(SelfLearningMaterial.subject_id == subject_id)
            .scalar()
            or 0
        )
        return self._subject_to_out(subject, materials_count=materials_count)

    def delete_subject(self, student_id: uuid.UUID, subject_id: uuid.UUID) -> dict[str, Any]:
        """Delete subject, cascading deletion of associated materials and chunks."""
        subject = (
            self.db.query(SelfLearningSubject)
            .filter(
                SelfLearningSubject.id == subject_id,
                SelfLearningSubject.student_id == student_id,
            )
            .first()
        )
        if not subject:
            raise SelfLearningError("Subject not found.", status_code=404)

        # Clean up storage files for materials under this subject
        materials = (
            self.db.query(SelfLearningMaterial)
            .filter(SelfLearningMaterial.subject_id == subject_id)
            .all()
        )
        for mat in materials:
            if mat.storage_path:
                try:
                    self.storage.delete(mat.storage_path)
                except Exception as e:
                    logger.warning("Failed to delete storage file %s: %s", mat.storage_path, e)

        self.db.delete(subject)
        self.db.commit()
        return {"deleted": True, "subject_id": str(subject_id)}

    # =========================================================================
    # DOCUMENT INGESTION, DEDUPLICATION & RAG
    # =========================================================================

    def upload_material(
        self,
        student_id: uuid.UUID,
        subject_id: uuid.UUID,
        filename: str,
        content: bytes,
        title: str | None = None,
    ) -> MaterialOut:
        """Ingest a document (.pdf, .docx, .pptx, .txt) with quota validation,

        SHA-256 deduplication, Gemini topic discovery, and pgvector chunking.
        """
        # 1. Verify subject belongs to student
        subject = (
            self.db.query(SelfLearningSubject)
            .filter(
                SelfLearningSubject.id == subject_id,
                SelfLearningSubject.student_id == student_id,
            )
            .first()
        )
        if not subject:
            raise SelfLearningError("Subject not found.", status_code=404)

        file_size = len(content)
        if file_size == 0:
            raise SelfLearningError("Cannot upload empty file.", status_code=400)

        # 2. Check 100MB per-student storage quota
        current_used = (
            self.db.query(func.coalesce(func.sum(SelfLearningMaterial.file_size_bytes), 0))
            .filter(SelfLearningMaterial.student_id == student_id)
            .scalar()
            or 0
        )
        if current_used + file_size > self.max_quota_bytes:
            raise SelfLearningError(
                f"Storage quota exceeded. Used: {current_used / (1024*1024):.2f}MB, "
                f"File: {file_size / (1024*1024):.2f}MB, Quota: {self.max_quota_bytes / (1024*1024):.0f}MB.",
                status_code=413,
            )

        # 3. MIME & extension validation
        try:
            file_type, canonical_mime = detect_file_type(filename)
        except DocumentParsingError as e:
            raise SelfLearningError(str(e), status_code=400) from e

        # 4. SHA-256 Deduplication check
        file_hash = compute_sha256(content)
        existing_material = (
            self.db.query(SelfLearningMaterial)
            .filter(
                SelfLearningMaterial.student_id == student_id,
                SelfLearningMaterial.file_hash == file_hash,
            )
            .first()
        )

        if existing_material:
            logger.info(
                "SHA-256 Deduplication: File hash %s already ingested for student %s.",
                file_hash,
                student_id,
            )
            # If already in the exact same subject, return it directly without re-embedding
            if existing_material.subject_id == subject_id:
                chunks_count = (
                    self.db.query(func.count(SelfLearningChunk.id))
                    .filter(SelfLearningChunk.material_id == existing_material.id)
                    .scalar()
                    or 0
                )
                return self._material_to_out(existing_material, chunks_count=chunks_count)

            # If ingested under another subject, reuse extracted text, topics and clone chunks
            return self._clone_deduplicated_material(
                existing_material=existing_material,
                new_subject_id=subject_id,
                filename=filename,
                title=title,
            )

        # 5. Extract text from file bytes
        try:
            extracted_text = extract_text(file_type, content)
        except DocumentParsingError as e:
            raise SelfLearningError(f"Failed to extract text from {filename}: {e}", status_code=422) from e

        # 6. Store file in storage backend
        storage_key = f"students/{student_id}/subjects/{subject_id}/{file_hash[:16]}_{filename}"
        try:
            stored_obj = self.storage.put_bytes(storage_key, content, canonical_mime)
            storage_path = stored_obj.key
        except Exception as e:
            logger.warning("Storage backend write error, continuing with key: %s", e)
            storage_path = storage_key

        # 7. Gemini Topic & Syllabus Discovery
        doc_title = title.strip() if title and title.strip() else filename
        topics = self.gemini.extract_topics(extracted_text, filename)

        # 8. Create Material entity
        material = SelfLearningMaterial(
            student_id=student_id,
            subject_id=subject_id,
            title=doc_title,
            file_name=filename,
            file_type=file_type,
            mime_type=canonical_mime,
            file_size_bytes=file_size,
            file_hash=file_hash,
            storage_path=storage_path,
            extracted_topics=topics,
            status="PROCESSED",
        )
        self.db.add(material)
        self.db.flush()  # assign material.id

        # 9. Semantic Chunking & Gemini pgvector Embeddings
        chunks = chunk_text(
            extracted_text,
            chunk_size_chars=settings.CHUNK_SIZE_CHARS,
            chunk_overlap_chars=settings.CHUNK_OVERLAP_CHARS,
        )

        if chunks:
            # Generate 768-dimensional embeddings
            embeddings = self.gemini.generate_embeddings(chunks)

            # Associate each chunk with the most relevant topic tag if possible
            for idx, chunk_content in enumerate(chunks):
                topic_tag = topics[min(idx, len(topics) - 1)] if topics else None
                emb = embeddings[idx] if idx < len(embeddings) else None
                chunk_entity = SelfLearningChunk(
                    material_id=material.id,
                    subject_id=subject_id,
                    student_id=student_id,
                    chunk_index=idx,
                    topic_tag=topic_tag,
                    content=chunk_content,
                    embedding=emb,
                    metadata_json={
                        "filename": filename,
                        "file_type": file_type,
                        "char_count": len(chunk_content),
                    },
                )
                self.db.add(chunk_entity)

        self.db.commit()
        self.db.refresh(material)
        return self._material_to_out(material, chunks_count=len(chunks))

    def _clone_deduplicated_material(
        self,
        existing_material: SelfLearningMaterial,
        new_subject_id: uuid.UUID,
        filename: str,
        title: str | None,
    ) -> MaterialOut:
        """Clone existing ingested material and its embeddings to another subject without re-embedding."""
        new_title = title.strip() if title and title.strip() else existing_material.title
        material = SelfLearningMaterial(
            student_id=existing_material.student_id,
            subject_id=new_subject_id,
            title=new_title,
            file_name=filename,
            file_type=existing_material.file_type,
            mime_type=existing_material.mime_type,
            file_size_bytes=existing_material.file_size_bytes,
            file_hash=existing_material.file_hash,
            storage_path=existing_material.storage_path,
            extracted_topics=list(existing_material.extracted_topics),
            status="PROCESSED",
        )
        self.db.add(material)
        self.db.flush()

        existing_chunks = (
            self.db.query(SelfLearningChunk)
            .filter(SelfLearningChunk.material_id == existing_material.id)
            .order_by(SelfLearningChunk.chunk_index.asc())
            .all()
        )
        for ec in existing_chunks:
            chunk_copy = SelfLearningChunk(
                material_id=material.id,
                subject_id=new_subject_id,
                student_id=existing_material.student_id,
                chunk_index=ec.chunk_index,
                topic_tag=ec.topic_tag,
                content=ec.content,
                embedding=ec.embedding,
                metadata_json=dict(ec.metadata_json),
            )
            self.db.add(chunk_copy)

        self.db.commit()
        self.db.refresh(material)
        return self._material_to_out(material, chunks_count=len(existing_chunks))

    def get_material(self, student_id: uuid.UUID, material_id: uuid.UUID) -> MaterialOut:
        """Get single material metadata."""
        mat = (
            self.db.query(SelfLearningMaterial)
            .filter(
                SelfLearningMaterial.id == material_id,
                SelfLearningMaterial.student_id == student_id,
            )
            .first()
        )
        if not mat:
            raise SelfLearningError("Material not found.", status_code=404)

        chunks_count = (
            self.db.query(func.count(SelfLearningChunk.id))
            .filter(SelfLearningChunk.material_id == material_id)
            .scalar()
            or 0
        )
        return self._material_to_out(mat, chunks_count=chunks_count)

    def list_materials(
        self, student_id: uuid.UUID, subject_id: uuid.UUID | None = None
    ) -> list[MaterialOut]:
        """List materials for student, optionally filtered by subject."""
        query = self.db.query(SelfLearningMaterial).filter(
            SelfLearningMaterial.student_id == student_id
        )
        if subject_id:
            query = query.filter(SelfLearningMaterial.subject_id == subject_id)

        materials = query.order_by(SelfLearningMaterial.created_at.desc()).all()
        if not materials:
            return []

        mat_ids = [m.id for m in materials]
        chunk_counts = dict(
            self.db.query(
                SelfLearningChunk.material_id,
                func.count(SelfLearningChunk.id),
            )
            .filter(SelfLearningChunk.material_id.in_(mat_ids))
            .group_by(SelfLearningChunk.material_id)
            .all()
        )

        return [self._material_to_out(m, chunks_count=chunk_counts.get(m.id, 0)) for m in materials]

    def get_material_topics(self, student_id: uuid.UUID, material_id: uuid.UUID) -> TopicsOut:
        """Return the Gemini-extracted chapters and subtopics for a material."""
        mat = (
            self.db.query(SelfLearningMaterial)
            .filter(
                SelfLearningMaterial.id == material_id,
                SelfLearningMaterial.student_id == student_id,
            )
            .first()
        )
        if not mat:
            raise SelfLearningError("Material not found.", status_code=404)

        return TopicsOut(
            material_id=mat.id,
            title=mat.title,
            topics=list(mat.extracted_topics or []),
        )

    def delete_material(self, student_id: uuid.UUID, material_id: uuid.UUID) -> dict[str, Any]:
        """Delete material, cascading deletion to chunks and removing storage file."""
        mat = (
            self.db.query(SelfLearningMaterial)
            .filter(
                SelfLearningMaterial.id == material_id,
                SelfLearningMaterial.student_id == student_id,
            )
            .first()
        )
        if not mat:
            raise SelfLearningError("Material not found.", status_code=404)

        # Remove from storage if stored
        if mat.storage_path:
            try:
                self.storage.delete(mat.storage_path)
            except Exception as e:
                logger.warning("Failed to delete storage file %s: %s", mat.storage_path, e)

        self.db.delete(mat)
        self.db.commit()
        return {"deleted": True, "material_id": str(material_id)}

    # =========================================================================
    # VECTOR SEARCH & QUOTA
    # =========================================================================

    def semantic_search(
        self,
        student_id: uuid.UUID,
        query: str,
        subject_id: uuid.UUID | None = None,
        limit: int = 5,
    ) -> SearchResult:
        """Perform semantic similarity search over student's document chunks using pgvector."""
        query_text = query.strip()
        if not query_text:
            return SearchResult(query=query, results=[])

        query_emb = self.gemini.generate_embedding(query_text)

        # Check if vector cosine distance is supported
        results: list[ChunkOut] = []
        try:
            if hasattr(SelfLearningChunk.embedding, "cosine_distance"):
                # pgvector cosine distance query
                distance_col = SelfLearningChunk.embedding.cosine_distance(query_emb).label("distance")
                stmt = (
                    select(SelfLearningChunk, distance_col)
                    .where(SelfLearningChunk.student_id == student_id)
                )
                if subject_id:
                    stmt = stmt.where(SelfLearningChunk.subject_id == subject_id)

                stmt = stmt.order_by(distance_col.asc()).limit(limit)
                rows = self.db.execute(stmt).all()

                for chunk, dist in rows:
                    similarity = max(0.0, 1.0 - float(dist)) if dist is not None else 0.5
                    results.append(
                        ChunkOut(
                            id=chunk.id,
                            material_id=chunk.material_id,
                            subject_id=chunk.subject_id,
                            chunk_index=chunk.chunk_index,
                            topic_tag=chunk.topic_tag,
                            content=chunk.content,
                            similarity=round(similarity, 4),
                            metadata_json=chunk.metadata_json or {},
                        )
                    )
                return SearchResult(query=query_text, results=results)
        except Exception as exc:
            logger.warning("pgvector query failed, falling back to Python dot product: %s", exc)

        # Fallback: compute cosine similarity in Python over student chunks
        base_query = self.db.query(SelfLearningChunk).filter(
            SelfLearningChunk.student_id == student_id
        )
        if subject_id:
            base_query = base_query.filter(SelfLearningChunk.subject_id == subject_id)

        all_chunks = base_query.limit(200).all()
        scored: list[tuple[float, SelfLearningChunk]] = []
        for ch in all_chunks:
            if ch.embedding:
                # Dot product since vectors are normalized
                sim = sum(a * b for a, b in zip(query_emb, ch.embedding))
                scored.append((sim, ch))

        scored.sort(key=lambda x: x[0], reverse=True)
        for sim, ch in scored[:limit]:
            results.append(
                ChunkOut(
                    id=ch.id,
                    material_id=ch.material_id,
                    subject_id=ch.subject_id,
                    chunk_index=ch.chunk_index,
                    topic_tag=ch.topic_tag,
                    content=ch.content,
                    similarity=round(max(0.0, sim), 4),
                    metadata_json=ch.metadata_json or {},
                )
            )

        return SearchResult(query=query_text, results=results)

    def get_storage_quota(self, student_id: uuid.UUID) -> StorageQuotaOut:
        """Return student storage usage vs 100MB quota."""
        used_bytes = (
            self.db.query(func.coalesce(func.sum(SelfLearningMaterial.file_size_bytes), 0))
            .filter(SelfLearningMaterial.student_id == student_id)
            .scalar()
            or 0
        )
        count = (
            self.db.query(func.count(SelfLearningMaterial.id))
            .filter(SelfLearningMaterial.student_id == student_id)
            .scalar()
            or 0
        )
        pct = round((used_bytes / self.max_quota_bytes) * 100, 2)
        return StorageQuotaOut(
            student_id=student_id,
            used_bytes=used_bytes,
            total_quota_bytes=self.max_quota_bytes,
            used_percentage=pct,
            materials_count=count,
        )

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _subject_to_out(self, s: SelfLearningSubject, materials_count: int = 0) -> SubjectOut:
        return SubjectOut(
            id=s.id,
            student_id=s.student_id,
            name=s.name,
            code=s.code,
            department=s.department,
            description=s.description,
            color_hex=s.color_hex,
            icon_name=s.icon_name,
            materials_count=materials_count,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )

    def _material_to_out(self, m: SelfLearningMaterial, chunks_count: int = 0) -> MaterialOut:
        return MaterialOut(
            id=m.id,
            student_id=m.student_id,
            subject_id=m.subject_id,
            title=m.title,
            file_name=m.file_name,
            file_type=m.file_type,
            mime_type=m.mime_type,
            file_size_bytes=m.file_size_bytes,
            file_hash=m.file_hash,
            extracted_topics=list(m.extracted_topics or []),
            status=m.status,
            created_at=m.created_at,
            chunks_count=chunks_count,
        )

    # =========================================================================
    # PHASE 2: LANGGRAPH & GEMINI MCQ ENGINE
    # =========================================================================

    def generate_test(
        self, student_id: uuid.UUID, request: TestGenerateRequest
    ) -> TestOut:
        """Executes the LangGraph StateGraph MCQ pipeline with Bloom's calibration & numerical solvers."""
        subject = (
            self.db.query(SelfLearningSubject)
            .filter(
                SelfLearningSubject.id == request.subject_id,
                SelfLearningSubject.student_id == student_id,
            )
            .first()
        )
        if not subject:
            raise SelfLearningError("Subject not found.", status_code=404)

        if request.count < 5 or request.count > 30:
            raise SelfLearningError("Question count must be between 5 and 30.", status_code=400)

        engine = LangGraphMCQEngine(self.db, self.gemini)
        test_entity = engine.generate_test(student_id, request)
        return self._test_to_out(test_entity)

    def get_test(self, student_id: uuid.UUID, test_id: uuid.UUID) -> TestOut:
        """Retrieve test details with all generated questions and numerical solutions."""
        test = (
            self.db.query(SelfLearningTest)
            .filter(
                SelfLearningTest.id == test_id,
                SelfLearningTest.student_id == student_id,
            )
            .first()
        )
        if not test:
            raise SelfLearningError("Test not found.", status_code=404)

        return self._test_to_out(test)

    def list_tests(
        self, student_id: uuid.UUID, subject_id: uuid.UUID | None = None
    ) -> list[TestOut]:
        """List tests generated for the student, optionally filtered by subject."""
        query = self.db.query(SelfLearningTest).filter(
            SelfLearningTest.student_id == student_id
        )
        if subject_id:
            query = query.filter(SelfLearningTest.subject_id == subject_id)

        tests = query.order_by(SelfLearningTest.created_at.desc()).all()
        return [self._test_to_out(t) for t in tests]

    def delete_test(self, student_id: uuid.UUID, test_id: uuid.UUID) -> dict[str, Any]:
        """Delete test and cascade delete its questions."""
        test = (
            self.db.query(SelfLearningTest)
            .filter(
                SelfLearningTest.id == test_id,
                SelfLearningTest.student_id == student_id,
            )
            .first()
        )
        if not test:
            raise SelfLearningError("Test not found.", status_code=404)

        self.db.delete(test)
        self.db.commit()
        return {"deleted": True, "test_id": str(test_id)}

    def _test_to_out(self, t: SelfLearningTest) -> TestOut:
        qs_out = [
            QuestionOut(
                id=q.id,
                test_id=q.test_id,
                question_number=q.question_number,
                question_text=q.question_text,
                options=q.options,
                correct_option=q.correct_option,
                explanation=q.explanation,
                bloom_level=q.bloom_level,
                difficulty=q.difficulty,
                is_quantitative=q.is_quantitative,
                formula_latex=q.formula_latex,
                step_by_step_solution=list(q.step_by_step_solution or []),
                topic_tag=q.topic_tag,
                created_at=q.created_at,
            )
            for q in t.questions
        ]
        return TestOut(
            id=t.id,
            student_id=t.student_id,
            subject_id=t.subject_id,
            title=t.title,
            difficulty=t.difficulty,
            target_topics=list(t.target_topics or []),
            total_questions=t.total_questions,
            status=t.status,
            created_at=t.created_at,
            updated_at=t.updated_at,
            questions=qs_out,
        )

    # =========================================================================
    # PHASE 3: EVALUATION, FEEDBACK, MASTERY & SMART REGENERATION
    # =========================================================================

    def submit_test(
        self,
        student_id: uuid.UUID,
        test_id: uuid.UUID,
        payload: TestSubmitRequest,
    ) -> TestResultOut:
        """Real-time Grader: Evaluates student answers, generates diffs,

        cites pedagogical rationale, renders LaTeX formulas, and saves submission.
        """
        test = (
            self.db.query(SelfLearningTest)
            .filter(
                SelfLearningTest.id == test_id,
                SelfLearningTest.student_id == student_id,
            )
            .first()
        )
        if not test:
            raise SelfLearningError("Test not found.", status_code=404)

        questions = sorted(test.questions, key=lambda q: q.question_number)
        if not questions:
            raise SelfLearningError("Test has no questions to evaluate.", status_code=400)

        score = 0
        detailed_results: list[dict[str, Any]] = []
        topic_stats: dict[str, dict[str, int]] = {}

        # Build answer map: support lookup by str(q.id) and str(q.question_number)
        raw_answers = payload.answers or {}

        for q in questions:
            q_id_str = str(q.id)
            q_num_str = str(q.question_number)

            selected_opt: str | None = None
            if q_id_str in raw_answers:
                selected_opt = str(raw_answers[q_id_str]).strip().upper()
            elif q_num_str in raw_answers:
                selected_opt = str(raw_answers[q_num_str]).strip().upper()

            is_correct = selected_opt == q.correct_option
            if is_correct:
                score += 1

            topic = q.topic_tag or "General"
            if topic not in topic_stats:
                topic_stats[topic] = {"correct": 0, "total": 0}
            topic_stats[topic]["total"] += 1
            if is_correct:
                topic_stats[topic]["correct"] += 1

            # Pedagogical rationale citing source materials
            feedback = (
                f"Why is this correct? According to the curriculum documentation on '{topic}', "
                f"Option {q.correct_option} is the accurate formulation: {q.explanation}"
            )

            detail = {
                "question_id": str(q.id),
                "question_number": q.question_number,
                "question_text": q.question_text,
                "options": q.options,
                "selected_option": selected_opt,
                "correct_option": q.correct_option,
                "is_correct": is_correct,
                "explanation": feedback,
                "bloom_level": q.bloom_level,
                "difficulty": q.difficulty,
                "is_quantitative": q.is_quantitative,
                "formula_latex": q.formula_latex,
                "step_by_step_solution": list(q.step_by_step_solution or []),
                "topic_tag": topic,
            }
            detailed_results.append(detail)

        total_questions = len(questions)
        pct = round((score / total_questions) * 100, 2)
        passed = pct >= 50.0

        # Topic Breakdown
        topic_breakdown: list[dict[str, Any]] = []
        for t_name, s_data in topic_stats.items():
            t_pct = round((s_data["correct"] / s_data["total"]) * 100, 2)
            if t_pct >= 75.0:
                t_status = "Strong"
            elif t_pct >= 50.0:
                t_status = "Moderate"
            else:
                t_status = "Weak"

            topic_breakdown.append(
                {
                    "topic": t_name,
                    "correct": s_data["correct"],
                    "total": s_data["total"],
                    "percentage": t_pct,
                    "status": t_status,
                }
            )

        submission = SelfLearningTestSubmission(
            test_id=test.id,
            student_id=student_id,
            subject_id=test.subject_id,
            score=score,
            total_questions=total_questions,
            percentage=pct,
            passed=passed,
            answers=raw_answers,
            detailed_results=detailed_results,
            topic_breakdown=topic_breakdown,
            time_taken_seconds=payload.time_taken_seconds,
        )
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)

        logger.info(
            "Graded Test '%s': Score %d/%d (%.2f%%) - Passed: %s",
            test.title,
            score,
            total_questions,
            pct,
            passed,
        )
        return self._submission_to_out(submission)

    def get_test_result(self, student_id: uuid.UUID, test_id: uuid.UUID) -> TestResultOut:
        """Retrieve the latest graded result for a specific test."""
        sub = (
            self.db.query(SelfLearningTestSubmission)
            .filter(
                SelfLearningTestSubmission.test_id == test_id,
                SelfLearningTestSubmission.student_id == student_id,
            )
            .order_by(SelfLearningTestSubmission.created_at.desc())
            .first()
        )
        if not sub:
            raise SelfLearningError("No submission found for this test.", status_code=404)

        return self._submission_to_out(sub)

    def get_subject_mastery(
        self, student_id: uuid.UUID, subject_id: uuid.UUID
    ) -> SubjectMasteryOut:
        """Topic Mastery Profiler: Aggregates student's cumulative performance across all tests

        and classifies topics into Strong (>=75%), Moderate (50-74%), and Weak (<50%).
        """
        subject = (
            self.db.query(SelfLearningSubject)
            .filter(
                SelfLearningSubject.id == subject_id,
                SelfLearningSubject.student_id == student_id,
            )
            .first()
        )
        if not subject:
            raise SelfLearningError("Subject not found.", status_code=404)

        submissions = (
            self.db.query(SelfLearningTestSubmission)
            .filter(
                SelfLearningTestSubmission.subject_id == subject_id,
                SelfLearningTestSubmission.student_id == student_id,
            )
            .all()
        )

        topic_aggregation: dict[str, dict[str, int]] = {}

        # 1. Aggregate from test submissions
        for sub in submissions:
            for item in sub.detailed_results or []:
                t_name = item.get("topic_tag") or "General"
                if t_name not in topic_aggregation:
                    topic_aggregation[t_name] = {"attempted": 0, "correct": 0}
                topic_aggregation[t_name]["attempted"] += 1
                if item.get("is_correct"):
                    topic_aggregation[t_name]["correct"] += 1

        # 2. Also ensure extracted topics from subject materials are represented
        materials = (
            self.db.query(SelfLearningMaterial)
            .filter(
                SelfLearningMaterial.subject_id == subject_id,
                SelfLearningMaterial.student_id == student_id,
            )
            .all()
        )
        for mat in materials:
            for t in mat.extracted_topics or []:
                if t not in topic_aggregation:
                    topic_aggregation[t] = {"attempted": 0, "correct": 0}

        topics_detail: list[TopicMasteryDetail] = []
        strong_count = 0
        moderate_count = 0
        weak_count = 0
        total_attempted_sum = 0
        total_correct_sum = 0

        for t_name, counts in topic_aggregation.items():
            att = counts["attempted"]
            corr = counts["correct"]
            total_attempted_sum += att
            total_correct_sum += corr

            pct = round((corr / att) * 100, 2) if att > 0 else 0.0

            if pct >= 75.0:
                status = "Strong"
                recom = "Demonstrates strong conceptual mastery. Ready for advanced synthesis or challenge problems."
                strong_count += 1
            elif pct >= 50.0:
                status = "Moderate"
                recom = "Approaching mastery. Review application problems and step-by-step proofs."
                moderate_count += 1
            else:
                status = "Weak"
                recom = "Needs targeted diagnostic review on foundational concepts and core formulas."
                weak_count += 1

            topics_detail.append(
                TopicMasteryDetail(
                    topic=t_name,
                    total_attempted=att,
                    total_correct=corr,
                    mastery_percentage=pct,
                    status=status,
                    recommendation=recom,
                )
            )

        overall_pct = (
            round((total_correct_sum / total_attempted_sum) * 100, 2)
            if total_attempted_sum > 0
            else 0.0
        )

        return SubjectMasteryOut(
            subject_id=subject_id,
            student_id=student_id,
            overall_mastery_percentage=overall_pct,
            total_tests_taken=len(submissions),
            total_questions_attempted=total_attempted_sum,
            strong_topics_count=strong_count,
            moderate_topics_count=moderate_count,
            weak_topics_count=weak_count,
            topics=topics_detail,
        )

    def regenerate_test(
        self,
        student_id: uuid.UUID,
        test_id: uuid.UUID,
        payload: TestRegenerateRequest,
    ) -> TestOut:
        """Smart Test Regeneration: Analyzes past test results and applies weighted allocation.

        Heavily focuses on weak topics (70% weak / 30% strong in 'weak_focus' mode).
        """
        test = (
            self.db.query(SelfLearningTest)
            .filter(
                SelfLearningTest.id == test_id,
                SelfLearningTest.student_id == student_id,
            )
            .first()
        )
        if not test:
            raise SelfLearningError("Test not found.", status_code=404)

        latest_submission = (
            self.db.query(SelfLearningTestSubmission)
            .filter(
                SelfLearningTestSubmission.test_id == test_id,
                SelfLearningTestSubmission.student_id == student_id,
            )
            .order_by(SelfLearningTestSubmission.created_at.desc())
            .first()
        )

        engine = LangGraphMCQEngine(self.db, self.gemini)
        regenerated_test = engine.plan_and_regenerate_test(
            student_id=student_id,
            original_test=test,
            submission=latest_submission,
            mode=payload.mode,
            count=payload.count,
            title=payload.title,
        )
        return self._test_to_out(regenerated_test)

    def _submission_to_out(self, sub: SelfLearningTestSubmission) -> TestResultOut:
        details = [
            QuestionEvaluationDetail(
                question_id=uuid.UUID(d["question_id"]) if isinstance(d["question_id"], str) else d["question_id"],
                question_number=d["question_number"],
                question_text=d["question_text"],
                options=d["options"],
                selected_option=d.get("selected_option"),
                correct_option=d["correct_option"],
                is_correct=d["is_correct"],
                explanation=d["explanation"],
                bloom_level=d.get("bloom_level", "UNDERSTAND"),
                difficulty=d.get("difficulty", "medium"),
                is_quantitative=d.get("is_quantitative", False),
                formula_latex=d.get("formula_latex"),
                step_by_step_solution=list(d.get("step_by_step_solution") or []),
                topic_tag=d.get("topic_tag"),
            )
            for d in (sub.detailed_results or [])
        ]

        breakdown = [
            TopicScore(
                topic=b["topic"],
                correct=b["correct"],
                total=b["total"],
                percentage=b["percentage"],
                status=b["status"],
            )
            for b in (sub.topic_breakdown or [])
        ]

        return TestResultOut(
            id=sub.id,
            test_id=sub.test_id,
            student_id=sub.student_id,
            subject_id=sub.subject_id,
            score=sub.score,
            total_questions=sub.total_questions,
            percentage=sub.percentage,
            passed=sub.passed,
            answers=dict(sub.answers or {}),
            detailed_results=details,
            topic_breakdown=breakdown,
            time_taken_seconds=sub.time_taken_seconds,
            created_at=sub.created_at,
        )
