import React, { useState } from "react";
import {
  Award,
  CheckCircle2,
  XCircle,
  Sparkles,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  BookOpen,
  ArrowRight,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import type { TestResultOut } from "../types";
import { KaTeXViewer, RichMathText } from "./KaTeXViewer";

interface TestReviewScreenProps {
  result: TestResultOut;
  onRegenerateSmartTest: (mode: "weak_focus" | "balanced" | "challenge") => Promise<void>;
  onBackToDashboard: () => void;
  isRegenerating?: boolean;
}

export const TestReviewScreen: React.FC<TestReviewScreenProps> = ({
  result,
  onRegenerateSmartTest,
  onBackToDashboard,
  isRegenerating = false,
}) => {
  const [openSolutions, setOpenSolutions] = useState<Record<string, boolean>>({});

  const toggleSolution = (qId: string) => {
    setOpenSolutions((prev) => ({
      ...prev,
      [qId]: !prev[qId],
    }));
  };

  const isPassed = result.passed;
  const scorePct = result.percentage;

  // Identify weak topics to highlight in remediation
  const weakTopics = result.topic_breakdown.filter((t) => t.status === "Weak");
  const moderateTopics = result.topic_breakdown.filter((t) => t.status === "Moderate");

  return (
    <div className="space-y-6">
      {/* Top Banner: Score & Pass/Fail */}
      <div
        className={`rounded-2xl border p-6 shadow-xs ${
          isPassed
            ? "border-success/40 bg-success-soft/60"
            : "border-danger/40 bg-danger-soft/60"
        }`}
      >
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div
              className={`flex h-14 w-14 items-center justify-center rounded-2xl ${
                isPassed
                  ? "bg-success text-success-fg"
                  : "bg-danger text-danger-fg"
              }`}
            >
              <Award className="h-8 w-8" />
            </div>
            <div>
              <span
                className={`text-xs font-bold uppercase tracking-wider ${
                  isPassed ? "text-success-ink" : "text-danger-ink"
                }`}
              >
                {isPassed ? "Assessment Passed" : "Needs Remediation"}
              </span>
              <h2 className="text-2xl font-bold">
                {result.score} / {result.total_questions} Questions Correct ({scorePct}%)
              </h2>
            </div>
          </div>

          {/* 1-Click Smart Regeneration */}
          <div className="flex flex-wrap items-center gap-2.5">
            <button
              type="button"
              onClick={onBackToDashboard}
              className="rounded-xl border border-line bg-panel px-4 py-2.5 text-xs font-semibold hover:bg-surface transition"
            >
              Back to Studio
            </button>

            <button
              type="button"
              disabled={isRegenerating}
              onClick={() => onRegenerateSmartTest("balanced")}
              className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-panel px-3.5 py-2.5 text-xs font-semibold hover:border-primary hover:text-primary-ink disabled:opacity-50 transition"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Balanced Retest</span>
            </button>

            <button
              type="button"
              disabled={isRegenerating}
              onClick={() => onRegenerateSmartTest("challenge")}
              className="inline-flex items-center gap-1.5 rounded-xl border border-secondary/40 bg-secondary-soft px-3.5 py-2.5 text-xs font-bold text-secondary-ink hover:opacity-90 disabled:opacity-50 transition"
            >
              <TrendingUp className="h-3.5 w-3.5" />
              <span>Challenge Mode</span>
            </button>

            <button
              type="button"
              disabled={isRegenerating}
              onClick={() => onRegenerateSmartTest("weak_focus")}
              className="inline-flex items-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-xs font-bold text-on-primary shadow-xs hover:bg-primary-hover disabled:opacity-50 transition"
            >
              <Sparkles className="h-4 w-4" />
              <span>{isRegenerating ? "Regenerating…" : "1-Click Smart Regenerate (Gaps)"}</span>
            </button>
          </div>
        </div>

        {/* Weak topic warning alert if any */}
        {weakTopics.length > 0 && (
          <div className="mt-4 flex items-center gap-2 rounded-xl bg-panel/80 p-3 text-xs text-ink border border-line">
            <TrendingDown className="h-4 w-4 text-danger-ink shrink-0" />
            <span>
              <strong>Target Remediation Areas:</strong> Smart Regeneration will focus 70% of questions on{" "}
              {weakTopics.map((w) => `"${w.topic}"`).join(", ")}.
            </span>
          </div>
        )}
      </div>

      {/* Per-Topic Performance Breakdown */}
      <div className="rounded-2xl border border-line bg-panel p-5 shadow-xs">
        <h3 className="text-base font-bold mb-4">Topic Performance Breakdown</h3>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {result.topic_breakdown.map((tb, idx) => (
            <div
              key={idx}
              className="rounded-xl border border-line bg-surface p-3.5 space-y-2"
            >
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold truncate max-w-[180px]">{tb.topic}</span>
                <span
                  className={`rounded-md px-2 py-0.5 font-bold text-xs ${
                    tb.status === "Strong"
                      ? "bg-success-soft text-success-ink"
                      : tb.status === "Moderate"
                      ? "bg-warning-soft text-warning-ink"
                      : "bg-danger-soft text-danger-ink"
                  }`}
                >
                  {tb.status}
                </span>
              </div>
              <div className="flex items-center justify-between text-xs text-muted">
                <span>
                  {tb.correct} / {tb.total} correct
                </span>
                <span className="font-mono">{tb.percentage}%</span>
              </div>
              <div className="h-1.5 w-full rounded-full bg-panel overflow-hidden">
                <div
                  className={`h-full ${
                    tb.status === "Strong"
                      ? "bg-success"
                      : tb.status === "Moderate"
                      ? "bg-warning"
                      : "bg-danger"
                  }`}
                  style={{ width: `${tb.percentage}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Detailed Question Diffs & Pedagogical Feedback */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold">Question Diagnostic Diffs</h3>

        {result.detailed_results.map((q) => {
          const isCorrect = q.is_correct;
          const isSolutionOpen = Boolean(openSolutions[q.question_id]);

          return (
            <div
              key={q.question_id}
              className={`rounded-2xl border p-5 transition shadow-xs bg-panel ${
                isCorrect
                  ? "border-success/40"
                  : "border-danger/40"
              }`}
            >
              {/* Question Header */}
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  {isCorrect ? (
                    <CheckCircle2 className="h-5 w-5 text-success-ink shrink-0" />
                  ) : (
                    <XCircle className="h-5 w-5 text-danger-ink shrink-0" />
                  )}
                  <span className="font-bold text-sm">Question {q.question_number}</span>
                  {q.topic_tag && (
                    <span className="rounded-md bg-surface border border-line px-2 py-0.5 text-xs text-muted">
                      {q.topic_tag}
                    </span>
                  )}
                  <span className="rounded-md bg-surface border border-line px-2 py-0.5 text-xs text-muted">
                    Bloom's: {q.bloom_level}
                  </span>
                </div>

                <span
                  className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                    isCorrect
                      ? "bg-success-soft text-success-ink"
                      : "bg-danger-soft text-danger-ink"
                  }`}
                >
                  {isCorrect ? "Correct" : "Incorrect"}
                </span>
              </div>

              {/* Question Text */}
              <div className="mt-3 text-sm font-semibold leading-relaxed">
                <RichMathText text={q.question_text} />
              </div>

              {/* Options diff */}
              <div className="mt-4 grid gap-2 sm:grid-cols-2">
                {(["A", "B", "C", "D"] as const).map((key) => {
                  const optText = q.options[key];
                  if (!optText) return null;

                  const isStudentPick = q.selected_option === key;
                  const isRightAnswer = q.correct_option === key;

                  let styleClass = "border-line bg-surface text-muted";
                  if (isRightAnswer) {
                    styleClass =
                      "border-success bg-success-soft/80 font-semibold text-success-ink ring-1 ring-success";
                  } else if (isStudentPick && !isRightAnswer) {
                    styleClass =
                      "border-danger bg-danger-soft/80 font-semibold text-danger-ink line-through";
                  }

                  return (
                    <div
                      key={key}
                      className={`flex items-start gap-2.5 rounded-xl border p-3 text-xs leading-snug ${styleClass}`}
                    >
                      <span className="font-bold shrink-0">{key}.</span>
                      <span className="break-words whitespace-normal">
                        <RichMathText text={optText} />
                      </span>
                    </div>
                  );
                })}
              </div>

              {/* Pedagogical Feedback / Document-Cited Rationale */}
              <div className="mt-4 rounded-xl border border-line bg-surface p-3.5 text-xs leading-relaxed space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-1.5 font-bold text-primary-ink">
                    <BookOpen className="h-3.5 w-3.5" />
                    <span>Document-Cited Diagnostic Explanation</span>
                  </div>
                  {q.topic_tag && (
                    <span className="rounded-md bg-primary-soft px-2 py-0.5 text-[11px] font-semibold text-primary-ink">
                      Cited Topic: {q.topic_tag}
                    </span>
                  )}
                </div>
                <p className="text-ink">
                  <RichMathText text={q.explanation} />
                </p>
              </div>

              {/* Collapsible View Solution for Quantitative Questions */}
              {q.is_quantitative && (
                <div className="mt-3">
                  <button
                    type="button"
                    onClick={() => toggleSolution(q.question_id)}
                    className="flex items-center gap-1.5 text-xs font-semibold text-primary-ink hover:underline transition"
                  >
                    <span>{isSolutionOpen ? "Hide Step-by-Step LaTeX Proof" : "View Solution & LaTeX Formula Proof"}</span>
                    {isSolutionOpen ? (
                      <ChevronUp className="h-3.5 w-3.5" />
                    ) : (
                      <ChevronDown className="h-3.5 w-3.5" />
                    )}
                  </button>

                  {isSolutionOpen && (
                    <div className="mt-3 rounded-xl border border-primary/30 bg-primary-soft/40 p-4 space-y-3">
                      {q.formula_latex && (
                        <div>
                          <p className="text-xs font-semibold text-primary-ink uppercase tracking-wide">
                            Governing LaTeX Formula:
                          </p>
                          <KaTeXViewer math={q.formula_latex} className="my-1 text-sm font-semibold" />
                        </div>
                      )}

                      {q.step_by_step_solution && q.step_by_step_solution.length > 0 && (
                        <div>
                          <p className="text-xs font-semibold text-primary-ink uppercase tracking-wide mb-1.5">
                            Intermediate Derivation Proof:
                          </p>
                          <ol className="list-decimal list-inside space-y-1.5 text-xs text-ink">
                            {q.step_by_step_solution.map((step, idx) => (
                              <li key={idx} className="leading-relaxed">
                                <RichMathText text={step} />
                              </li>
                            ))}
                          </ol>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
