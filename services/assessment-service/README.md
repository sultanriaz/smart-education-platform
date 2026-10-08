# Assessment Service — Sprint 8

Independent FastAPI service for quizzes, question banks, attempts, auto-grading,
manual grading, results, and assessment events.

## Ownership

Assessment Service owns:
- question banks
- questions and choices
- quizzes and quiz-question composition
- section quiz assignments
- attempts and answers
- grading history
- assessment outbox events

It does **not** own users, students, teachers, courses, sections, enrollments,
learning resources, attendance, rooms, schedules, or notifications.

Cross-service academic relationships are validated through Academic Service.
Identity is trusted through the JWT/JWKS contract.

## Local ports

- API: `http://localhost:8008`
- Swagger: `http://localhost:8008/docs`
- PostgreSQL: `localhost:5441`

## Assessment lifecycle

1. Teacher/Admin creates question bank.
2. Teacher/Admin creates questions.
3. Teacher/Admin creates draft quiz.
4. Questions are attached.
5. Quiz is published.
6. Published quiz is assigned to a section with open/due timestamps and attempt limit.
7. Enrolled student starts an attempt.
8. Student saves answers.
9. Submission auto-grades objective questions.
10. SHORT_TEXT questions leave the attempt in `SUBMITTED`.
11. Teacher/Admin grades subjective answers.
12. Once all subjective answers are scored, attempt becomes `GRADED`.
13. `assessment.attempt_graded` is written transactionally to outbox.

## Question types

- `MCQ_SINGLE`
- `TRUE_FALSE`
- `SHORT_TEXT`

Objective questions require exactly one correct choice.

## Statuses

Quiz:
- DRAFT
- PUBLISHED
- ARCHIVED

Attempt:
- IN_PROGRESS
- SUBMITTED
- GRADED

## Core routes

- `POST /api/v1/banks`
- `POST /api/v1/questions`
- `POST /api/v1/quizzes`
- `POST /api/v1/quizzes/{quiz_id}/questions`
- `POST /api/v1/quizzes/{quiz_id}/publish`
- `POST /api/v1/quizzes/{quiz_id}/assignments`
- `POST /api/v1/assignments/{assignment_id}/attempts`
- `PUT /api/v1/attempts/{attempt_id}/answers/{question_id}`
- `POST /api/v1/attempts/{attempt_id}/submit`
- `POST /api/v1/attempts/{attempt_id}/grade`
- `GET /health`
- `GET /ready`

## Authorization

Teacher/Admin:
- authoring and grading

Teacher:
- assignment creation must be validated against teacher-section assignment

Student:
- start own attempts
- update own in-progress attempts
- submit own attempts

Student enrollment is validated against Academic Service.

## Scoring

For objective questions, correct choice earns the question points, otherwise 0.

SHORT_TEXT is manually scored.

Quiz percentage:

`score / max_score * 100`

`passed = percent >= quiz.pass_percent`

## Migrations

```powershell
alembic upgrade head
alembic downgrade base
alembic upgrade head
alembic check
```

## Local setup

```powershell
cd servicesssessment-service
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
pytest -q
uvicorn app.main:app --reload --port 8008
```

## Docker

From repository root:

```powershell
docker compose -f .\docker-compose.assessment.yml up -d --build
```

## Integration note

The exact Academic Service endpoints and Identity JWKS URL must be reconciled
against the versions already present in the repository during merge.

The supplied `CODEX_MERGE_PROMPT.md` instructs the merge pass to do this.
