import { useCallback, useMemo, useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";
import { Button } from "../../components/ui/Button";
import { AssessmentDeadline } from "../../components/ui/AssessmentDeadline";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { useToast } from "../../components/ui/useToast";
import {
  useAssessmentAssignmentDetail,
  useStartAttempt,
  useSubmitAttempt
} from "../../features/student/hooks";
import { getActiveAttempt, saveAttemptAnswer } from "../../features/student/student-api";

type AnswerState = Record<
  string,
  { selected_choice_id?: string; text_answer?: string }
>;

export function StudentAssessmentAttemptPage() {
  const { assignmentId = "" } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const detail = useAssessmentAssignmentDetail(assignmentId);
  const start = useStartAttempt();
  const submit = useSubmitAttempt();
  const [attemptId, setAttemptId] = useState<string | null>(null);
  const [expiresAt, setExpiresAt] = useState<string | null>(null);
  const [serverTime, setServerTime] = useState<string | null>(null);
  const [expired, setExpired] = useState(false);
  const [answers, setAnswers] = useState<AnswerState>({});
  const [saving, setSaving] = useState(false);
  const [starting, setStarting] = useState(false);
  const finalizeExpired = useCallback(() => {
    setExpired(true);
    if (!attemptId) return;
    void submit.mutateAsync(attemptId).then(() => {
      toast.push("Time ended. Your saved answers were submitted.", "success");
      navigate("/app/student/assessments", { replace: true });
    }).catch(() => toast.push("Time ended. Saved answers will finalize on the server. Reopen your results to check.", "error"));
  }, [attemptId, submit, toast, navigate]);

  const answeredCount = useMemo(
    () =>
      Object.values(answers).filter(
        (value) => value.selected_choice_id || value.text_answer?.trim()
      ).length,
    [answers]
  );

  if (!assignmentId) return <Navigate to="/app/student/assessments" replace />;

  if (detail.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading assessment…" />
      </div>
    );
  }

  if (detail.error || !detail.data) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Student" title="Assessment" />
        <InlineError message="This assessment could not be loaded." />
      </div>
    );
  }

  const assignment = detail.data;

  const begin = async () => {
    setStarting(true);
    try {
      const previous = await getActiveAttempt(assignmentId);
      const attempt = previous ?? await start.mutateAsync(assignmentId);
      setAttemptId(attempt.id);
      setExpiresAt(attempt.expiresAt ?? null);
      setServerTime(attempt.serverTime ?? null);
      setExpired(false);

      // Create explicit blank subjective answers so a submitted SHORT_TEXT
      // question always has an AttemptAnswer row available for Teacher grading,
      // even if the Student leaves it blank.
      setAnswers((current) => {
        const next = { ...current };
        for (const answer of attempt.answers ?? []) {
          next[answer.questionId] = { selected_choice_id: answer.selectedChoiceId, text_answer: answer.textAnswer };
        }
        for (const question of assignment.questions) {
          if (question.questionType === "SHORT_TEXT" && !next[question.id]) {
            next[question.id] = { text_answer: "" };
          }
        }
        return next;
      });

      toast.push(previous ? "Saved assessment resumed." : "Assessment attempt started.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Could not start attempt.", "error");
    } finally {
      setStarting(false);
    }
  };

  const persistAnswers = async () => {
    if (!attemptId) return;
    setSaving(true);
    try {
      for (const question of assignment.questions) {
        const answer = answers[question.id];
        if (!answer) continue;
        await saveAttemptAnswer(attemptId, question.id, answer);
      }
      toast.push("Answers saved.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Could not save answers.", "error");
      throw error;
    } finally {
      setSaving(false);
    }
  };

  const finish = async () => {
    if (!attemptId) return;
    try {
      await persistAnswers();
      const result = await submit.mutateAsync(attemptId);
      toast.push(
        result.status === "GRADED"
          ? "Assessment submitted and graded."
          : "Assessment submitted for review.",
        "success"
      );
      navigate("/app/student/assessments", { replace: true });
    } catch {
      // Toast already reports the underlying failure.
    }
  };

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Assessment"
        title={assignment.title}
        description={assignment.description ?? undefined}
      />

      {!attemptId ? (
        <Card title="Before you begin">
          <dl className="grid gap-4 sm:grid-cols-3">
            <div>
              <dt className="text-xs uppercase tracking-wide text-muted">Questions</dt>
              <dd className="mt-1 text-lg font-semibold">{assignment.questions.length}</dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-muted">Duration</dt>
              <dd className="mt-1 text-lg font-semibold">
                {assignment.durationMinutes ? `${assignment.durationMinutes} min` : "Not timed"}
              </dd>
            </div>
            <div>
              <dt className="text-xs uppercase tracking-wide text-muted">Due</dt>
              <dd className="mt-1 text-sm">{new Date(assignment.dueAt).toLocaleString()}</dd>
            </div>
          </dl>

          <Button className="mt-6" onClick={() => void begin()} disabled={starting}>
            {starting ? "Opening…" : assignment.activeAttemptId ? "Resume attempt" : "Start attempt"}
          </Button>
        </Card>
      ) : (
        <>
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-line bg-panel px-4 py-3 text-sm">
            <span>
              Answered {answeredCount} of {assignment.questions.length}
            </span>
            {expiresAt && <AssessmentDeadline key={attemptId} expiresAt={expiresAt} serverTime={serverTime} onExpire={finalizeExpired} />}
          </div>
          {expiresAt && <p className="mb-4 text-sm text-muted">Save progress before time ends. The timer continues if you leave this page; saved answers are submitted automatically.</p>}

          <div className="space-y-5">
            {assignment.questions.map((question, index) => (
              <Card
                key={question.id}
                title={`Question ${index + 1}`}
                description={`${question.points} point${question.points === 1 ? "" : "s"}`}
              >
                <p className="mb-4 font-medium leading-6">{question.prompt}</p>

                {question.questionType === "SHORT_TEXT" ? (
                  <label className="block text-sm font-medium">
                    Your answer
                    <textarea
                      className="mt-2 min-h-32 w-full rounded-xl border border-line bg-panel px-3 py-2"
                      value={answers[question.id]?.text_answer ?? ""}
                      disabled={expired}
                      onChange={(event) =>
                        setAnswers((current) => ({
                          ...current,
                          [question.id]: {
                            text_answer: event.target.value
                          }
                        }))
                      }
                    />
                  </label>
                ) : (
                  <fieldset className="space-y-2">
                    <legend className="sr-only">Choose one answer</legend>
                    {question.choices.map((choice) => (
                      <label
                        key={choice.id}
                        className="flex cursor-pointer items-center gap-3 rounded-xl border border-line p-3 hover:bg-surface"
                      >
                        <input
                          type="radio"
                          disabled={expired}
                          name={`question-${question.id}`}
                          value={choice.id}
                          checked={
                            answers[question.id]?.selected_choice_id === choice.id
                          }
                          onChange={() =>
                            setAnswers((current) => ({
                              ...current,
                              [question.id]: {
                                selected_choice_id: choice.id
                              }
                            }))
                          }
                        />
                        <span className="text-sm">{choice.text}</span>
                      </label>
                    ))}
                  </fieldset>
                )}
              </Card>
            ))}
          </div>

          <div className="mt-6 flex flex-wrap justify-end gap-3">
            <Button
              variant="secondary"
              onClick={() => void persistAnswers().catch(() => undefined)}
              disabled={expired || saving || submit.isPending}
            >
              {saving ? "Saving…" : "Save progress"}
            </Button>
            <Button
              onClick={() => void finish()}
              disabled={expired || saving || submit.isPending}
            >
              {submit.isPending ? "Submitting…" : "Submit assessment"}
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
