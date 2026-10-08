import { Link } from "react-router-dom";
import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionLoader } from "../../components/ui/SectionLoader";
import {
  useAssessmentAssignments,
  useAssessmentResults
} from "../../features/student/hooks";

export function StudentAssessmentsPage() {
  const assignments = useAssessmentAssignments();
  const results = useAssessmentResults();

  if (assignments.isLoading || results.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading assessments…" />
      </div>
    );
  }

  if (assignments.error || results.error) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Student" title="Assessments" />
        <InlineError message="Assessment data could not be loaded." />
      </div>
    );
  }

  const openAssignments = [...(assignments.data ?? [])].sort(
    (a, b) => new Date(a.dueAt).getTime() - new Date(b.dueAt).getTime()
  );

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Student"
        title="Assessments"
        description="View available quizzes, attempt limits, deadlines, and graded results."
      />

      <section aria-labelledby="available-assessments">
        <h2 id="available-assessments" className="mb-4 text-xl font-bold">
          Available assessments
        </h2>

        {openAssignments.length ? (
          <div className="grid gap-4 md:grid-cols-2">
            {openAssignments.map((assignment) => {
              const due = new Date(assignment.dueAt);
              const now = Date.now();
              const opens = new Date(assignment.opensAt).getTime();
              const closes = due.getTime();
              const notOpen = Number.isFinite(opens) && now < opens;
              const expired = Number.isFinite(closes) && now > closes;
              const attemptsUsed = assignment.attemptsUsed ?? 0;
              const limitReached = !assignment.activeAttemptId && attemptsUsed >= assignment.attemptLimit;

              return (
                <Card key={assignment.id}>
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h3 className="text-lg font-semibold">{assignment.title}</h3>
                      {assignment.description ? (
                        <p className="mt-2 text-sm leading-6 text-muted">
                          {assignment.description}
                        </p>
                      ) : null}
                    </div>
                    <Badge>
                      {expired
                        ? "Closed"
                        : notOpen
                          ? "Upcoming"
                          : limitReached
                            ? "Limit reached"
                            : assignment.activeAttemptId ? "In progress" : "Available"}
                    </Badge>
                  </div>

                  <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
                    <div>
                      <dt className="text-xs uppercase tracking-wide text-muted">Opens</dt>
                      <dd className="mt-1">{new Date(assignment.opensAt).toLocaleString()}</dd>
                    </div>
                    <div>
                      <dt className="text-xs uppercase tracking-wide text-muted">Due</dt>
                      <dd className="mt-1">{due.toLocaleString()}</dd>
                    </div>
                    <div>
                      <dt className="text-xs uppercase tracking-wide text-muted">Attempts</dt>
                      <dd className="mt-1">
                        {attemptsUsed} / {assignment.attemptLimit}
                      </dd>
                    </div>
                  </dl>

                  <Link
                    to={`/app/student/assessments/${assignment.id}`}
                    aria-disabled={notOpen || expired || limitReached}
                    className={[
                      "mt-5 inline-flex rounded-xl px-4 py-2 text-sm font-semibold",
                      notOpen || expired || limitReached
                        ? "pointer-events-none bg-surface text-muted"
                        : "bg-brand-600 text-white"
                    ].join(" ")}
                  >
                    Open assessment
                  </Link>
                </Card>
              );
            })}
          </div>
        ) : (
          <Card>
            <p className="text-sm text-muted">No assessments are assigned right now.</p>
          </Card>
        )}
      </section>

      <section className="mt-8" aria-labelledby="results-heading">
        <h2 id="results-heading" className="mb-4 text-xl font-bold">
          Results
        </h2>

        <Card>
          {results.data?.length ? (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[700px] text-left text-sm">
                <thead>
                  <tr className="border-b border-line text-xs uppercase tracking-wide text-muted">
                    <th className="px-3 py-3">Assessment</th>
                    <th className="px-3 py-3">Status</th>
                    <th className="px-3 py-3">Score</th>
                    <th className="px-3 py-3">Percent</th>
                    <th className="px-3 py-3">Result</th>
                  </tr>
                </thead>
                <tbody>
                  {results.data.map((result) => (
                    <tr key={result.attemptId} className="border-b border-line/70">
                      <td className="px-3 py-3">
                        {result.title ?? result.quizId ?? result.assignmentId ?? "Assessment"}
                      </td>
                      <td className="px-3 py-3">
                        <Badge>{result.status}</Badge>
                      </td>
                      <td className="px-3 py-3">
                        {result.score != null
                          ? `${result.score}${result.maxScore != null ? ` / ${result.maxScore}` : ""}`
                          : "Pending"}
                      </td>
                      <td className="px-3 py-3">
                        {result.percent != null ? `${result.percent.toFixed(1)}%` : "—"}
                      </td>
                      <td className="px-3 py-3">
                        {result.passed == null ? "Pending" : result.passed ? "Passed" : "Not passed"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="text-sm text-muted">No submitted assessment results yet.</p>
          )}
        </Card>
      </section>
    </div>
  );
}
