import { useMemo, useState, type FormEvent } from "react";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { useToast } from "../../components/ui/useToast";
import {
  useAddQuestionToQuiz,
  useAssignmentAttempts,
  useAssignQuiz,
  useCreateQuestion,
  useCreateQuestionBank,
  useCreateQuiz,
  useGradeAttempt,
  usePublishQuiz,
  useTeacherAssignments,
  useTeacherBanks,
  useTeacherQuestions,
  useTeacherQuizzes,
  useTeacherSections
} from "../../features/teacher/hooks";
import type { TeacherAttemptAnswer } from "../../features/teacher/types";

type QuestionType = "MCQ_SINGLE" | "TRUE_FALSE" | "SHORT_TEXT";

export function TeacherAssessmentsPage() {
  const toast = useToast();
  const sections = useTeacherSections();
  const banks = useTeacherBanks();
  const questions = useTeacherQuestions();
  const quizzes = useTeacherQuizzes();
  const assignments = useTeacherAssignments();

  const createBank = useCreateQuestionBank();
  const createQuestion = useCreateQuestion();
  const createQuiz = useCreateQuiz();
  const addQuestion = useAddQuestionToQuiz();
  const publishQuiz = usePublishQuiz();
  const assignQuiz = useAssignQuiz();

  const [bankName, setBankName] = useState("");
  const [bankCourseId, setBankCourseId] = useState("");

  const [questionBankId, setQuestionBankId] = useState("");
  const [questionType, setQuestionType] = useState<QuestionType>("MCQ_SINGLE");
  const [prompt, setPrompt] = useState("");
  const [points, setPoints] = useState(1);
  const [choiceA, setChoiceA] = useState("");
  const [choiceB, setChoiceB] = useState("");
  const [correctChoice, setCorrectChoice] = useState<"A" | "B">("A");
  const [correctText, setCorrectText] = useState("");
  const [explanation, setExplanation] = useState("");

  const [quizTitle, setQuizTitle] = useState("");
  const [quizDescription, setQuizDescription] = useState("");
  const [quizCourseId, setQuizCourseId] = useState("");
  const [durationMinutes, setDurationMinutes] = useState("");
  const [passPercent, setPassPercent] = useState(50);

  const [composeQuizId, setComposeQuizId] = useState("");
  const [composeQuestionId, setComposeQuestionId] = useState("");

  const [assignQuizId, setAssignQuizId] = useState("");
  const [assignSectionId, setAssignSectionId] = useState("");
  const [opensAt, setOpensAt] = useState("");
  const [dueAt, setDueAt] = useState("");
  const [attemptLimit, setAttemptLimit] = useState(1);

  const [gradingAssignmentId, setGradingAssignmentId] = useState("");
  const attempts = useAssignmentAttempts(gradingAssignmentId);
  const grade = useGradeAttempt(gradingAssignmentId);
  const [gradeForms, setGradeForms] = useState<
    Record<string, { score: string; feedback: string; reason: string }>
  >({});

  const courses = useMemo(() => {
    const byId = new Map<string, string>();
    for (const section of sections.data ?? []) {
      if (section.courseId) {
        byId.set(
          section.courseId,
          section.courseCode
            ? `${section.courseCode}${section.courseTitle ? ` · ${section.courseTitle}` : ""}`
            : section.courseTitle ?? section.courseId
        );
      }
    }
    return Array.from(byId, ([id, label]) => ({ id, label }));
  }, [sections.data]);

  const selectedQuiz = quizzes.data?.find((quiz) => quiz.id === composeQuizId);

  if (
    sections.isLoading ||
    banks.isLoading ||
    questions.isLoading ||
    quizzes.isLoading ||
    assignments.isLoading
  ) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading assessment workspace…" />
      </div>
    );
  }

  if (
    sections.error ||
    banks.error ||
    questions.error ||
    quizzes.error ||
    assignments.error
  ) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Teacher" title="Assessment management" />
        <InlineError message="The assessment workspace could not be loaded." />
      </div>
    );
  }

  const submitBank = async (event: FormEvent) => {
    event.preventDefault();
    if (!bankName.trim()) {
      toast.push("Enter a question bank name.", "error");
      return;
    }
    try {
      const created = await createBank.mutateAsync({
        name: bankName.trim(),
        course_id: bankCourseId || null
      });
      setQuestionBankId(created.id);
      setBankName("");
      toast.push("Question bank created.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Could not create bank.", "error");
    }
  };

  const submitQuestion = async (event: FormEvent) => {
    event.preventDefault();
    if (!questionBankId || !prompt.trim()) {
      toast.push("Choose a bank and enter a question.", "error");
      return;
    }

    const choices =
      questionType === "SHORT_TEXT"
        ? []
        : [
            { text: choiceA.trim(), is_correct: correctChoice === "A" },
            { text: choiceB.trim(), is_correct: correctChoice === "B" }
          ];

    if (questionType !== "SHORT_TEXT" && choices.some((choice) => !choice.text)) {
      toast.push("Objective questions need at least two answer choices.", "error");
      return;
    }

    try {
      await createQuestion.mutateAsync({
        bank_id: questionBankId,
        question_type: questionType,
        prompt: prompt.trim(),
        points,
        correct_text: questionType === "SHORT_TEXT" ? correctText.trim() || null : null,
        explanation: explanation.trim() || null,
        choices
      });
      setPrompt("");
      setChoiceA("");
      setChoiceB("");
      setCorrectText("");
      setExplanation("");
      toast.push("Question created.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Could not create question.",
        "error"
      );
    }
  };

  const submitQuiz = async (event: FormEvent) => {
    event.preventDefault();
    if (!quizTitle.trim() || !quizCourseId) {
      toast.push("Provide a quiz title and course.", "error");
      return;
    }
    try {
      const created = await createQuiz.mutateAsync({
        title: quizTitle.trim(),
        description: quizDescription.trim() || undefined,
        course_id: quizCourseId,
        duration_minutes: durationMinutes ? Number(durationMinutes) : null,
        pass_percent: passPercent
      });
      setComposeQuizId(created.id);
      setQuizTitle("");
      setQuizDescription("");
      toast.push("Draft quiz created.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Could not create quiz.", "error");
    }
  };

  const attachQuestion = async () => {
    if (!composeQuizId || !composeQuestionId) {
      toast.push("Choose a draft quiz and question.", "error");
      return;
    }
    try {
      await addQuestion.mutateAsync({
        quizId: composeQuizId,
        input: {
          question_id: composeQuestionId,
          position: selectedQuiz?.questionCount ?? 0
        }
      });
      toast.push("Question added to quiz.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Could not add question.",
        "error"
      );
    }
  };

  const publish = async () => {
    if (!composeQuizId) return;
    try {
      await publishQuiz.mutateAsync(composeQuizId);
      toast.push("Quiz published.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Could not publish quiz.",
        "error"
      );
    }
  };

  const submitAssignment = async (event: FormEvent) => {
    event.preventDefault();
    if (!assignQuizId || !assignSectionId || !opensAt || !dueAt) {
      toast.push("Complete all assignment fields.", "error");
      return;
    }

    const opens = new Date(opensAt);
    const due = new Date(dueAt);
    if (due <= opens) {
      toast.push("Due time must be after opening time.", "error");
      return;
    }

    try {
      await assignQuiz.mutateAsync({
        quizId: assignQuizId,
        input: {
          section_id: assignSectionId,
          opens_at: opens.toISOString(),
          due_at: due.toISOString(),
          attempt_limit: attemptLimit
        }
      });
      toast.push("Quiz assigned to section.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Could not assign quiz.",
        "error"
      );
    }
  };

  const manualGrade = async (
    attemptId: string,
    answer: TeacherAttemptAnswer
  ) => {
    const form = gradeForms[answer.id] ?? {
      score: "",
      feedback: "",
      reason: ""
    };
    const score = Number(form.score);

    if (!Number.isFinite(score) || score < 0 || !form.reason.trim()) {
      toast.push("Enter a valid score and grading reason.", "error");
      return;
    }

    try {
      await grade.mutateAsync({
        attemptId,
        answerId: answer.id,
        score,
        feedback: form.feedback.trim() || undefined,
        reason: form.reason.trim()
      });
      toast.push("Manual grade saved.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Grading failed.", "error");
    }
  };

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Teacher"
        title="Assessment management"
        description="Build question banks and quizzes, publish assignments to your sections, review submissions, and manually grade subjective answers."
      />

      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="1. Question bank">
          <form className="space-y-4" onSubmit={(event) => void submitBank(event)}>
            <Input
              label="Bank name"
              value={bankName}
              onChange={(event) => setBankName(event.target.value)}
            />
            <label className="block text-sm font-medium">
              Course
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={bankCourseId}
                onChange={(event) => setBankCourseId(event.target.value)}
              >
                <option value="">General bank</option>
                {courses.map((course) => (
                  <option key={course.id} value={course.id}>
                    {course.label}
                  </option>
                ))}
              </select>
            </label>
            <Button type="submit" disabled={createBank.isPending}>
              Create bank
            </Button>
          </form>

          <div className="mt-5 flex flex-wrap gap-2">
            {(banks.data ?? []).map((bank) => (
              <button
                key={bank.id}
                onClick={() => setQuestionBankId(bank.id)}
                className={[
                  "rounded-full border px-3 py-1.5 text-xs font-semibold",
                  questionBankId === bank.id
                    ? "border-brand-600 bg-brand-50 text-brand-700"
                    : "border-line"
                ].join(" ")}
              >
                {bank.name}
              </button>
            ))}
          </div>
        </Card>

        <Card title="2. Create question">
          <form className="space-y-4" onSubmit={(event) => void submitQuestion(event)}>
            <label className="block text-sm font-medium">
              Bank
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={questionBankId}
                onChange={(event) => setQuestionBankId(event.target.value)}
              >
                <option value="">Select bank</option>
                {(banks.data ?? []).map((bank) => (
                  <option key={bank.id} value={bank.id}>
                    {bank.name}
                  </option>
                ))}
              </select>
            </label>

            <label className="block text-sm font-medium">
              Question type
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={questionType}
                onChange={(event) =>
                  setQuestionType(event.target.value as QuestionType)
                }
              >
                <option value="MCQ_SINGLE">MCQ · single answer</option>
                <option value="TRUE_FALSE">True / false</option>
                <option value="SHORT_TEXT">Short text · manual grade</option>
              </select>
            </label>

            <label className="block text-sm font-medium">
              Prompt
              <textarea
                className="mt-2 min-h-24 w-full rounded-xl border border-line px-3 py-2"
                value={prompt}
                onChange={(event) => setPrompt(event.target.value)}
              />
            </label>

            <Input
              label="Points"
              type="number"
              min={0.25}
              step={0.25}
              value={points}
              onChange={(event) => setPoints(Math.max(0.25, Number(event.target.value) || 1))}
            />

            {questionType === "SHORT_TEXT" ? (
              <Input
                label="Reference answer (optional)"
                value={correctText}
                onChange={(event) => setCorrectText(event.target.value)}
              />
            ) : (
              <>
                <Input
                  label={questionType === "TRUE_FALSE" ? "Choice A · usually True" : "Choice A"}
                  value={choiceA}
                  onChange={(event) => setChoiceA(event.target.value)}
                />
                <Input
                  label={questionType === "TRUE_FALSE" ? "Choice B · usually False" : "Choice B"}
                  value={choiceB}
                  onChange={(event) => setChoiceB(event.target.value)}
                />
                <label className="block text-sm font-medium">
                  Correct choice
                  <select
                    className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                    value={correctChoice}
                    onChange={(event) =>
                      setCorrectChoice(event.target.value as "A" | "B")
                    }
                  >
                    <option value="A">Choice A</option>
                    <option value="B">Choice B</option>
                  </select>
                </label>
              </>
            )}

            <Input
              label="Explanation (optional)"
              value={explanation}
              onChange={(event) => setExplanation(event.target.value)}
            />

            <Button type="submit" disabled={createQuestion.isPending}>
              Create question
            </Button>
          </form>
        </Card>

        <Card title="3. Create quiz">
          <form className="space-y-4" onSubmit={(event) => void submitQuiz(event)}>
            <Input
              label="Quiz title"
              value={quizTitle}
              onChange={(event) => setQuizTitle(event.target.value)}
            />
            <Input
              label="Description"
              value={quizDescription}
              onChange={(event) => setQuizDescription(event.target.value)}
            />
            <label className="block text-sm font-medium">
              Course
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={quizCourseId}
                onChange={(event) => setQuizCourseId(event.target.value)}
              >
                <option value="">Select course</option>
                {courses.map((course) => (
                  <option key={course.id} value={course.id}>
                    {course.label}
                  </option>
                ))}
              </select>
            </label>
            <Input
              label="Duration in minutes (optional)"
              type="number"
              min={1}
              value={durationMinutes}
              onChange={(event) => setDurationMinutes(event.target.value)}
            />
            <Input
              label="Pass percentage"
              type="number"
              min={0}
              max={100}
              value={passPercent}
              onChange={(event) =>
                setPassPercent(Math.min(100, Math.max(0, Number(event.target.value) || 0)))
              }
            />
            <Button type="submit" disabled={createQuiz.isPending}>
              Create draft quiz
            </Button>
          </form>
        </Card>

        <Card title="4. Compose & publish">
          <div className="space-y-4">
            <label className="block text-sm font-medium">
              Draft quiz
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={composeQuizId}
                onChange={(event) => setComposeQuizId(event.target.value)}
              >
                <option value="">Select quiz</option>
                {(quizzes.data ?? []).map((quiz) => (
                  <option key={quiz.id} value={quiz.id}>
                    {quiz.title} · {quiz.status}
                  </option>
                ))}
              </select>
            </label>

            <label className="block text-sm font-medium">
              Question
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={composeQuestionId}
                onChange={(event) => setComposeQuestionId(event.target.value)}
              >
                <option value="">Select question</option>
                {(questions.data ?? []).map((question) => (
                  <option key={question.id} value={question.id}>
                    {question.prompt}
                  </option>
                ))}
              </select>
            </label>

            <div className="flex flex-wrap gap-3">
              <Button
                variant="secondary"
                onClick={() => void attachQuestion()}
                disabled={addQuestion.isPending}
              >
                Add question
              </Button>
              <Button
                onClick={() => void publish()}
                disabled={
                  publishQuiz.isPending ||
                  !selectedQuiz ||
                  selectedQuiz.status !== "DRAFT"
                }
              >
                Publish quiz
              </Button>
            </div>
          </div>
        </Card>

        <Card title="5. Assign published quiz">
          <form className="space-y-4" onSubmit={(event) => void submitAssignment(event)}>
            <label className="block text-sm font-medium">
              Published quiz
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={assignQuizId}
                onChange={(event) => setAssignQuizId(event.target.value)}
              >
                <option value="">Select quiz</option>
                {(quizzes.data ?? [])
                  .filter((quiz) => quiz.status === "PUBLISHED")
                  .map((quiz) => (
                    <option key={quiz.id} value={quiz.id}>
                      {quiz.title}
                    </option>
                  ))}
              </select>
            </label>

            <label className="block text-sm font-medium">
              Assigned section
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={assignSectionId}
                onChange={(event) => setAssignSectionId(event.target.value)}
              >
                <option value="">Select section</option>
                {(sections.data ?? []).map((section) => (
                  <option key={section.id} value={section.id}>
                    {section.courseCode ? `${section.courseCode} · ` : ""}
                    {section.name}
                  </option>
                ))}
              </select>
            </label>

            <Input
              label="Opens"
              type="datetime-local"
              value={opensAt}
              onChange={(event) => setOpensAt(event.target.value)}
            />
            <Input
              label="Due"
              type="datetime-local"
              value={dueAt}
              onChange={(event) => setDueAt(event.target.value)}
            />
            <Input
              label="Attempt limit"
              type="number"
              min={1}
              max={20}
              value={attemptLimit}
              onChange={(event) =>
                setAttemptLimit(Math.min(20, Math.max(1, Number(event.target.value) || 1)))
              }
            />

            <Button type="submit" disabled={assignQuiz.isPending}>
              Assign quiz
            </Button>
          </form>
        </Card>

        <Card title="6. Submitted attempts & grading">
          <label className="block text-sm font-medium">
            Assignment
            <select
              className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
              value={gradingAssignmentId}
              onChange={(event) => setGradingAssignmentId(event.target.value)}
            >
              <option value="">Select assignment</option>
              {(assignments.data ?? []).map((assignment) => (
                <option key={assignment.id} value={assignment.id}>
                  {assignment.quizTitle ?? assignment.quizId} · {assignment.sectionId}
                </option>
              ))}
            </select>
          </label>

          {gradingAssignmentId && attempts.isLoading ? (
            <div className="mt-4">
              <SectionLoader label="Loading attempts…" />
            </div>
          ) : null}

          {attempts.error ? (
            <div className="mt-4">
              <InlineError message="Attempts could not be loaded." />
            </div>
          ) : null}

          <div className="mt-5 space-y-5">
            {(attempts.data ?? []).map((attempt) => (
              <div key={attempt.id} className="rounded-xl border border-line p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold">
                      Student {attempt.studentUserId}
                    </p>
                    <p className="mt-1 text-xs text-muted">
                      Attempt {attempt.attemptNumber} ·{" "}
                      {attempt.submittedAt
                        ? new Date(attempt.submittedAt).toLocaleString()
                        : "Not submitted"}
                    </p>
                  </div>
                  <Badge>{attempt.status}</Badge>
                </div>

                <div className="mt-4 space-y-4">
                  {attempt.answers
                    .filter((answer) => answer.questionType === "SHORT_TEXT")
                    .map((answer) => {
                      const form = gradeForms[answer.id] ?? {
                        score:
                          answer.manualScore != null
                            ? String(answer.manualScore)
                            : "",
                        feedback: answer.feedback ?? "",
                        reason: ""
                      };
                      return (
                        <div
                          key={answer.id}
                          className="rounded-xl bg-surface p-4"
                        >
                          <p className="text-sm font-semibold">
                            {answer.prompt ?? `Question ${answer.questionId}`}
                          </p>
                          <p className="mt-2 whitespace-pre-wrap text-sm text-muted">
                            {answer.textAnswer || "No text answer submitted."}
                          </p>
                          <div className="mt-4 grid gap-3 sm:grid-cols-3">
                            <Input
                              label={`Score${answer.points != null ? ` / ${answer.points}` : ""}`}
                              type="number"
                              min={0}
                              step={0.25}
                              value={form.score}
                              onChange={(event) =>
                                setGradeForms((current) => ({
                                  ...current,
                                  [answer.id]: {
                                    ...form,
                                    score: event.target.value
                                  }
                                }))
                              }
                            />
                            <Input
                              label="Feedback"
                              value={form.feedback}
                              onChange={(event) =>
                                setGradeForms((current) => ({
                                  ...current,
                                  [answer.id]: {
                                    ...form,
                                    feedback: event.target.value
                                  }
                                }))
                              }
                            />
                            <Input
                              label="Grading reason"
                              value={form.reason}
                              onChange={(event) =>
                                setGradeForms((current) => ({
                                  ...current,
                                  [answer.id]: {
                                    ...form,
                                    reason: event.target.value
                                  }
                                }))
                              }
                            />
                          </div>
                          <Button
                            className="mt-3"
                            onClick={() => void manualGrade(attempt.id, answer)}
                            disabled={grade.isPending}
                          >
                            Save grade
                          </Button>
                        </div>
                      );
                    })}
                </div>

                {attempt.status === "GRADED" ? (
                  <p className="mt-4 text-sm font-semibold">
                    Final result:{" "}
                    {attempt.percent != null
                      ? `${attempt.percent.toFixed(1)}%`
                      : "Graded"}
                  </p>
                ) : null}
              </div>
            ))}

            {gradingAssignmentId &&
            !attempts.isLoading &&
            !(attempts.data ?? []).length ? (
              <p className="text-sm text-muted">No attempts exist for this assignment yet.</p>
            ) : null}
          </div>
        </Card>
      </div>

      <section className="mt-8">
        <h2 className="mb-4 text-xl font-bold">Current quizzes & assignments</h2>
        <div className="grid gap-4 lg:grid-cols-2">
          {(quizzes.data ?? []).map((quiz) => (
            <Card key={quiz.id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-semibold">{quiz.title}</h3>
                  <p className="mt-1 text-xs text-muted">
                    Course {quiz.courseId} · pass {quiz.passPercent}%
                  </p>
                </div>
                <Badge>{quiz.status}</Badge>
              </div>
            </Card>
          ))}
          {(assignments.data ?? []).map((assignment) => (
            <Card key={assignment.id}>
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h3 className="font-semibold">
                    {assignment.quizTitle ?? "Assigned quiz"}
                  </h3>
                  <p className="mt-1 text-xs text-muted">
                    Section {assignment.sectionId}
                  </p>
                  <p className="mt-1 text-xs text-muted">
                    Due {new Date(assignment.dueAt).toLocaleString()}
                  </p>
                </div>
                <Badge>ASSIGNED</Badge>
              </div>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
