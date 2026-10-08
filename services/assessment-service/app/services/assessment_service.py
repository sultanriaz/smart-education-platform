from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, ForbiddenError, NotFoundError
from app.domain.entities.models import (
    Attempt,
    AttemptAnswer,
    AttemptStatus,
    GradeReview,
    OutboxEvent,
    Question,
    QuestionBank,
    QuestionChoice,
    QuestionType,
    Quiz,
    QuizAssignment,
    QuizQuestion,
    QuizStatus,
)
from app.repositories.repositories import AssessmentRepository
from app.schemas.models import (
    AnswerUpsert,
    AssignmentCreate,
    ManualGrade,
    QuestionBankCreate,
    QuestionCreate,
    QuizCreate,
    QuizQuestionAdd,
)


def now() -> datetime:
    return datetime.now(UTC)


def aware(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


class AssessmentService:
    def __init__(self, db: Session, academic_client=None):
        self.db = db
        self.repo = AssessmentRepository(db)
        self.academic = academic_client

    def _event(self, event_type: str, aggregate_type: str, aggregate_id: uuid.UUID, payload: dict):
        self.db.add(
            OutboxEvent(
                event_type=event_type,
                aggregate_type=aggregate_type,
                aggregate_id=aggregate_id,
                payload=payload,
            )
        )

    def create_bank(self, payload: QuestionBankCreate, actor_id: uuid.UUID):
        bank = QuestionBank(
            name=payload.name,
            course_id=payload.course_id,
            created_by_user_id=actor_id,
        )
        self.db.add(bank)
        self.db.commit()
        self.db.refresh(bank)
        return bank

    def create_question(self, payload: QuestionCreate, actor_id: uuid.UUID):
        if not self.repo.get_bank(payload.bank_id):
            raise NotFoundError("Question bank not found")
        q = Question(
            bank_id=payload.bank_id,
            question_type=payload.question_type,
            prompt=payload.prompt,
            points=payload.points,
            correct_text=payload.correct_text,
            explanation=payload.explanation,
            created_by_user_id=actor_id,
        )
        q.choices = [
            QuestionChoice(text=c.text, is_correct=c.is_correct, position=i)
            for i, c in enumerate(payload.choices)
        ]
        self.db.add(q)
        self.db.commit()
        self.db.refresh(q)
        return self.repo.get_question(q.id)

    def create_quiz(self, payload: QuizCreate, actor_id: uuid.UUID):
        quiz = Quiz(
            title=payload.title,
            description=payload.description,
            course_id=payload.course_id,
            duration_minutes=payload.duration_minutes,
            pass_percent=payload.pass_percent,
            created_by_user_id=actor_id,
        )
        self.db.add(quiz)
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def add_question(self, quiz_id: uuid.UUID, payload: QuizQuestionAdd):
        quiz = self.repo.get_quiz(quiz_id)
        if not quiz:
            raise NotFoundError("Quiz not found")
        if quiz.status != QuizStatus.DRAFT.value:
            raise ConflictError("Only draft quizzes can be modified")
        if not self.repo.get_question(payload.question_id):
            raise NotFoundError("Question not found")
        self.db.add(
            QuizQuestion(
                quiz_id=quiz_id,
                question_id=payload.question_id,
                position=payload.position,
                points_override=payload.points_override,
            )
        )
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Question already attached to quiz") from exc
        self.db.expire_all()
        return self.repo.get_quiz(quiz_id)

    def publish_quiz(self, quiz_id: uuid.UUID):
        quiz = self.repo.get_quiz(quiz_id)
        if not quiz:
            raise NotFoundError("Quiz not found")
        if not quiz.questions:
            raise ConflictError("Quiz must contain at least one question")
        quiz.status = QuizStatus.PUBLISHED.value
        self._event(
            "assessment.quiz_published",
            "quiz",
            quiz.id,
            {
                "quiz_id": str(quiz.id),
                "course_id": str(quiz.course_id),
                "title": quiz.title,
            },
        )
        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def create_assignment(
        self,
        quiz_id: uuid.UUID,
        payload: AssignmentCreate,
        actor_id: uuid.UUID,
        actor_roles: set[str],
        bearer_token: str | None = None,
    ):
        quiz = self.repo.get_quiz(quiz_id)
        if not quiz:
            raise NotFoundError("Quiz not found")
        if quiz.status != QuizStatus.PUBLISHED.value:
            raise ConflictError("Quiz must be published before assignment")
        if self.academic:
            self.academic.get_section(payload.section_id, bearer_token)
            if "teacher" in actor_roles and "admin" not in actor_roles:
                if not self.academic.validate_teacher_assignment(
                    actor_id, payload.section_id, bearer_token
                ):
                    raise ForbiddenError("Teacher is not assigned to this section")

        assignment = QuizAssignment(
            quiz_id=quiz_id,
            section_id=payload.section_id,
            opens_at=payload.opens_at,
            due_at=payload.due_at,
            attempt_limit=payload.attempt_limit,
            created_by_user_id=actor_id,
        )
        self.db.add(assignment)
        self.db.flush()
        self._event(
            "assessment.quiz_assigned",
            "assignment",
            assignment.id,
            {
                "quiz_id": str(quiz_id),
                "section_id": str(payload.section_id),
                "title": quiz.title,
            },
        )
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Quiz already assigned to this section") from exc
        self.db.refresh(assignment)
        return assignment

    def start_attempt(
        self,
        assignment_id: uuid.UUID,
        student_id: uuid.UUID,
        bearer_token: str | None = None,
    ):
        assignment = self.repo.get_assignment(assignment_id)
        if not assignment:
            raise NotFoundError("Assignment not found")
        current = now()
        if current < aware(assignment.opens_at):
            raise ConflictError("Assessment has not opened")
        if current >= aware(assignment.due_at):
            raise ConflictError("Assessment deadline has passed")
        if self.academic and not self.academic.validate_student_enrollment(
            student_id, assignment.section_id, bearer_token
        ):
            raise ForbiddenError("Student is not enrolled in this section")

        count = self.repo.count_attempts(assignment_id, student_id)
        if count >= assignment.attempt_limit:
            raise ConflictError("Attempt limit reached")

        quiz = self.repo.get_quiz(assignment.quiz_id)
        expires_at = aware(assignment.due_at)
        if quiz.duration_minutes is not None:
            expires_at = min(expires_at, current + timedelta(minutes=quiz.duration_minutes))
        attempt = Attempt(
            assignment_id=assignment_id,
            student_user_id=student_id,
            attempt_number=count + 1,
            started_at=current,
            expires_at=expires_at,
        )
        self.db.add(attempt)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Concurrent attempt creation conflict") from exc
        self.db.refresh(attempt)
        return attempt

    def answer_question(
        self,
        attempt_id: uuid.UUID,
        question_id: uuid.UUID,
        payload: AnswerUpsert,
        student_id: uuid.UUID,
    ):
        attempt = self.repo.get_attempt(attempt_id, lock=True)
        if not attempt:
            raise NotFoundError("Attempt not found")
        if attempt.student_user_id != student_id:
            raise ForbiddenError("Attempt belongs to another student")
        if attempt.status != AttemptStatus.IN_PROGRESS.value:
            raise ConflictError("Submitted attempts cannot be modified")
        if self.finalize_if_expired(attempt):
            raise ConflictError("Assessment time has expired; saved answers were submitted")

        assignment = self.repo.get_assignment(attempt.assignment_id)
        quiz = self.repo.get_quiz(assignment.quiz_id)
        allowed = {qq.question_id for qq in quiz.questions}
        if question_id not in allowed:
            raise NotFoundError("Question is not part of this quiz")
        question = next(item.question for item in quiz.questions if item.question_id == question_id)
        if payload.selected_choice_id is not None and not any(
            choice.id == payload.selected_choice_id for choice in question.choices
        ):
            raise ConflictError("Selected choice does not belong to this question")

        answer = self.repo.get_answer(attempt_id, question_id)
        if answer is None:
            answer = AttemptAnswer(attempt_id=attempt_id, question_id=question_id)
            self.db.add(answer)

        answer.selected_choice_id = payload.selected_choice_id
        answer.text_answer = payload.text_answer
        answer.answered_at = now()
        self.db.commit()
        self.db.refresh(answer)
        self.db.expire_all()
        return answer

    def submit_attempt(self, attempt_id: uuid.UUID, student_id: uuid.UUID):
        attempt = self.repo.get_attempt(attempt_id, lock=True)
        if not attempt:
            raise NotFoundError("Attempt not found")
        if attempt.student_user_id != student_id:
            raise ForbiddenError("Attempt belongs to another student")
        if attempt.status != AttemptStatus.IN_PROGRESS.value:
            return attempt

        return self._finalize_locked(attempt)

    def finalize_if_expired(self, attempt: Attempt) -> bool:
        """Caller must hold the attempt row lock; expiry never accepts new answers."""
        if (
            attempt.status == AttemptStatus.IN_PROGRESS.value
            and attempt.expires_at is not None
            and now() >= aware(attempt.expires_at)
        ):
            self._finalize_locked(attempt)
            return True
        return False

    def read_student_attempt(self, attempt_id: uuid.UUID, student_id: uuid.UUID):
        attempt = self.repo.get_attempt(attempt_id, lock=True)
        if not attempt:
            raise NotFoundError("Attempt not found")
        if attempt.student_user_id != student_id:
            raise ForbiddenError("Attempt belongs to another student")
        self.finalize_if_expired(attempt)
        return attempt

    def _finalize_locked(self, attempt: Attempt):
        """Grade and persist the saved answer snapshot in the owned transaction."""

        assignment = self.repo.get_assignment(attempt.assignment_id)
        quiz = self.repo.get_quiz(assignment.quiz_id)

        answer_by_question = {a.question_id: a for a in attempt.answers}
        total = 0.0
        earned = 0.0
        manual_required = False

        for qq in quiz.questions:
            question = qq.question
            points = qq.points_override if qq.points_override is not None else question.points
            total += points
            answer = answer_by_question.get(question.id)

            if question.question_type in {
                QuestionType.MCQ_SINGLE.value,
                QuestionType.TRUE_FALSE.value,
            }:
                score = 0.0
                if answer and answer.selected_choice_id:
                    correct = next((c for c in question.choices if c.is_correct), None)
                    if correct and correct.id == answer.selected_choice_id:
                        score = points
                if answer:
                    answer.auto_score = score
                earned += score
            else:
                manual_required = True
                if answer is None:
                    answer = AttemptAnswer(question_id=question.id, text_answer="")
                    attempt.answers.append(answer)

        attempt.score = earned
        attempt.max_score = total
        attempt.percent = (earned / total * 100) if total else 0.0
        current = now()
        attempt.submitted_at = (
            min(current, aware(attempt.expires_at)) if attempt.expires_at else current
        )
        attempt.status = (
            AttemptStatus.SUBMITTED.value if manual_required else AttemptStatus.GRADED.value
        )
        if not manual_required:
            attempt.graded_at = now()
            attempt.passed = attempt.percent >= quiz.pass_percent

        self._event(
            "assessment.attempt_submitted",
            "attempt",
            attempt.id,
            {
                "attempt_id": str(attempt.id),
                "student_user_id": str(attempt.student_user_id),
                "quiz_id": str(quiz.id),
                "status": attempt.status,
            },
        )
        if attempt.status == AttemptStatus.GRADED.value:
            self._event(
                "assessment.attempt_graded",
                "attempt",
                attempt.id,
                {
                    "attempt_id": str(attempt.id),
                    "student_user_id": str(attempt.student_user_id),
                    "percent": attempt.percent,
                    "passed": attempt.passed,
                },
            )

        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def manual_grade(self, attempt_id: uuid.UUID, payload: ManualGrade, grader_id: uuid.UUID):
        attempt = self.repo.get_attempt(attempt_id, lock=True)
        if not attempt:
            raise NotFoundError("Attempt not found")
        if attempt.status == AttemptStatus.IN_PROGRESS.value:
            raise ConflictError("Attempt must be submitted before grading")
        answer = self.db.get(AttemptAnswer, payload.answer_id)
        if not answer or answer.attempt_id != attempt_id:
            raise NotFoundError("Answer not found")
        question = self.repo.get_question(answer.question_id)
        assignment = self.repo.get_assignment(attempt.assignment_id)
        quiz = self.repo.get_quiz(assignment.quiz_id)
        qq = next(x for x in quiz.questions if x.question_id == question.id)
        maximum = qq.points_override if qq.points_override is not None else question.points
        if payload.score > maximum:
            raise ConflictError("Manual score exceeds question maximum")

        previous = answer.manual_score
        answer.manual_score = payload.score
        answer.feedback = payload.feedback
        self.db.add(
            GradeReview(
                attempt_id=attempt.id,
                answer_id=answer.id,
                previous_score=previous,
                new_score=payload.score,
                reason=payload.reason,
                graded_by_user_id=grader_id,
            )
        )

        score = 0.0
        total = 0.0
        pending_manual = False
        answers = {a.question_id: a for a in attempt.answers}
        for item in quiz.questions:
            q = item.question
            points = item.points_override if item.points_override is not None else q.points
            total += points
            a = answers.get(q.id)
            if q.question_type == QuestionType.SHORT_TEXT.value:
                if a is None or a.manual_score is None:
                    pending_manual = True
                else:
                    score += a.manual_score
            elif a is not None:
                score += a.auto_score or 0.0

        attempt.score = score
        attempt.max_score = total
        attempt.percent = (score / total * 100) if total else 0.0
        if not pending_manual:
            attempt.status = AttemptStatus.GRADED.value
            attempt.graded_at = now()
            attempt.passed = attempt.percent >= quiz.pass_percent
            self._event(
                "assessment.attempt_graded",
                "attempt",
                attempt.id,
                {
                    "attempt_id": str(attempt.id),
                    "student_user_id": str(attempt.student_user_id),
                    "percent": attempt.percent,
                    "passed": attempt.passed,
                },
            )

        self.db.commit()
        self.db.refresh(attempt)
        return attempt
