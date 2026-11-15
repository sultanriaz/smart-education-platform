from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status

from app.api.dependencies import get_self_learning_service
from app.core.errors import DomainError
from app.schemas.self_learning import (
    MaterialOut,
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
    TopicsOut,
)
from app.security.auth import Principal, require_roles
from app.services.self_learning_service import SelfLearningService

router = APIRouter(prefix="/self-learning", tags=["Student Self-Learning & Gemini RAG"])


# =============================================================================
# SUBJECT ENGINE ENDPOINTS
# =============================================================================

@router.post("/subjects", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
def create_subject(
    payload: SubjectCreate,
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> SubjectOut:
    """Create a new custom subject for the student across any academic department."""
    try:
        return service.create_subject(principal.user_id, payload)
    except DomainError as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 400),
            detail=str(exc),
        ) from exc


@router.get("/subjects", response_model=list[SubjectOut])
def list_subjects(
    department: str | None = Query(None, description="Filter by department"),
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> list[SubjectOut]:
    """List all subjects created by the current student with material counts."""
    return service.list_subjects(principal.user_id, department=department)


@router.get("/subjects/{subject_id}", response_model=SubjectOut)
def get_subject(
    subject_id: uuid.UUID,
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> SubjectOut:
    """Get subject details by ID."""
    try:
        return service.get_subject(principal.user_id, subject_id)
    except DomainError as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 404),
            detail=str(exc),
        ) from exc


@router.put("/subjects/{subject_id}", response_model=SubjectOut)
def update_subject(
    subject_id: uuid.UUID,
    payload: SubjectUpdate,
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> SubjectOut:
    """Update custom subject details."""
    try:
        return service.update_subject(principal.user_id, subject_id, payload)
    except DomainError as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 400),
            detail=str(exc),
        ) from exc


@router.delete("/subjects/{subject_id}")
def delete_subject(
    subject_id: uuid.UUID,
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> dict[str, Any]:
    """Delete a subject and all associated materials and vector chunks."""
    try:
        return service.delete_subject(principal.user_id, subject_id)
    except DomainError as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 404),
            detail=str(exc),
        ) from exc


# =============================================================================
# MATERIAL INGESTION & TOPIC EXTRACTION ENDPOINTS
# =============================================================================

@router.post("/materials/upload", response_model=MaterialOut, status_code=status.HTTP_201_CREATED)
async def upload_material(
    subject_id: uuid.UUID = Form(...),
    title: str | None = Form(None),
    file: UploadFile = File(...),
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> MaterialOut:
    """Upload educational material (.pdf, .docx, .pptx, .txt).

    Performs MIME validation, 100MB quota check, SHA-256 deduplication,
    Gemini topic discovery, and pgvector semantic chunking.
    """
    try:
        content = await file.read()
        filename = file.filename or "uploaded_document.txt"
        return service.upload_material(
            student_id=principal.user_id,
            subject_id=subject_id,
            filename=filename,
            content=content,
            title=title,
        )
    except DomainError as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 400),
            detail=str(exc),
        ) from exc


@router.get("/materials", response_model=list[MaterialOut])
def list_materials(
    subject_id: uuid.UUID | None = Query(None, description="Optional subject filter"),
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> list[MaterialOut]:
    """List uploaded materials for the current student."""
    return service.list_materials(principal.user_id, subject_id=subject_id)


@router.get("/materials/{material_id}", response_model=MaterialOut)
def get_material(
    material_id: uuid.UUID,
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> MaterialOut:
    """Get metadata for a specific material."""
    try:
        return service.get_material(principal.user_id, material_id)
    except DomainError as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 404),
            detail=str(exc),
        ) from exc


@router.get("/materials/{material_id}/topics", response_model=TopicsOut)
def get_material_topics(
    material_id: uuid.UUID,
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> TopicsOut:
    """Retrieve Gemini-extracted syllabus topics and chapters for a material."""
    try:
        return service.get_material_topics(principal.user_id, material_id)
    except DomainError as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 404),
            detail=str(exc),
        ) from exc


@router.delete("/materials/{material_id}")
def delete_material(
    material_id: uuid.UUID,
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> dict[str, Any]:
    """Delete material, its storage file, and all associated vector chunks."""
    try:
        return service.delete_material(principal.user_id, material_id)
    except DomainError as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 404),
            detail=str(exc),
        ) from exc


# =============================================================================
# VECTOR SEARCH & QUOTA ENDPOINTS
# =============================================================================

@router.post("/search", response_model=SearchResult)
def search_materials(
    payload: SearchRequest,
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> SearchResult:
    """Perform pgvector semantic search over student materials with Gemini embeddings."""
    return service.semantic_search(
        student_id=principal.user_id,
        query=payload.query,
        subject_id=payload.subject_id,
        limit=payload.limit,
    )


@router.get("/quota", response_model=StorageQuotaOut)
def get_storage_quota(
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> StorageQuotaOut:
    """Check student storage quota usage (100MB capacity)."""
    return service.get_storage_quota(principal.user_id)


# =============================================================================
# PHASE 2: LANGGRAPH & GEMINI MCQ GENERATION ENGINE ENDPOINTS
# =============================================================================

@router.post("/tests/generate", response_model=TestOut, status_code=status.HTTP_201_CREATED)
def generate_test(
    payload: TestGenerateRequest,
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> TestOut:
    """Generate Bloom's-calibrated MCQs with numerical solvers via LangGraph pipeline.

    Accepts count (5 to 30), difficulty ('basic', 'medium', 'hard', 'mixed'),
    and optional target topics.
    """
    try:
        return service.generate_test(principal.user_id, payload)
    except DomainError as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 400),
            detail=str(exc),
        ) from exc


@router.get("/tests", response_model=list[TestOut])
def list_tests(
    subject_id: uuid.UUID | None = Query(None, description="Optional subject filter"),
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> list[TestOut]:
    """List all generated tests for current student."""
    return service.list_tests(principal.user_id, subject_id=subject_id)


@router.get("/tests/{test_id}", response_model=TestOut)
def get_test(
    test_id: uuid.UUID,
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> TestOut:
    """Retrieve details and all questions for a specific generated test."""
    try:
        return service.get_test(principal.user_id, test_id)
    except DomainError as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 404),
            detail=str(exc),
        ) from exc


@router.delete("/tests/{test_id}")
def delete_test(
    test_id: uuid.UUID,
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> dict[str, Any]:
    """Delete a test and all its questions."""
    try:
        return service.delete_test(principal.user_id, test_id)
    except DomainError as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 404),
            detail=str(exc),
        ) from exc


# =============================================================================
# PHASE 3: EVALUATION, FEEDBACK, MASTERY & REGENERATION ENDPOINTS
# =============================================================================

@router.post("/tests/{test_id}/submit", response_model=TestResultOut)
def submit_test(
    test_id: uuid.UUID,
    payload: TestSubmitRequest,
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> TestResultOut:
    """Real-time Grader: Evaluates student answers, provides pedagogical diffs,

    computes percentage score, and profiles per-topic performance.
    """
    try:
        return service.submit_test(principal.user_id, test_id, payload)
    except DomainError as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 400),
            detail=str(exc),
        ) from exc


@router.get("/tests/{test_id}/result", response_model=TestResultOut)
def get_test_result(
    test_id: uuid.UUID,
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> TestResultOut:
    """Retrieve the latest graded diagnostic result for a test."""
    try:
        return service.get_test_result(principal.user_id, test_id)
    except DomainError as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 404),
            detail=str(exc),
        ) from exc


@router.post("/tests/{test_id}/regenerate", response_model=TestOut, status_code=status.HTTP_201_CREATED)
def regenerate_test(
    test_id: uuid.UUID,
    payload: TestRegenerateRequest,
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> TestOut:
    """Smart Test Regeneration: Analyzes past test results and generates a new test

    with weighted focus on weak topics (70% weak / 30% strong in 'weak_focus' mode).
    """
    try:
        return service.regenerate_test(principal.user_id, test_id, payload)
    except DomainError as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 400),
            detail=str(exc),
        ) from exc


@router.get("/subjects/{subject_id}/mastery", response_model=SubjectMasteryOut)
def get_subject_mastery(
    subject_id: uuid.UUID,
    principal: Principal = Depends(require_roles("student", "teacher", "admin")),
    service: SelfLearningService = Depends(get_self_learning_service),
) -> SubjectMasteryOut:
    """Topic Mastery Profiler: Aggregates student's cumulative subject performance,

    classifying topics into Strong (>=75%), Moderate (50-74%), and Weak (<50%).
    """
    try:
        return service.get_subject_mastery(principal.user_id, subject_id)
    except DomainError as exc:
        raise HTTPException(
            status_code=getattr(exc, "status_code", 404),
            detail=str(exc),
        ) from exc
