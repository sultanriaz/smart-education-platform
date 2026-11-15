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
import { KaTeXViewer } from "./KaTeXViewer";

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
            ? "border-emerald-200 bg-emerald-50/60 dark:border-emerald-900/60 dark:bg-emerald-950/30"
            : "border-red-200 bg-red-50/60 dark:border-red-900/60 dark:bg-red-950/30"
        }`}
      >
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div
              className={`flex h-14 w-14 items-center justify-center rounded-2xl ${
                isPassed
                  ? "bg-emerald-600 text-white"
                  : "bg-red-600 text-white"
              }`}
            >
              <Award className="h-8 w-8" />
            </div>
            <div>
              <span
                className={`text-xs font-bold uppercase tracking-wider ${
                  isPassed ? "text-emerald-700 dark:text-emerald-400" : "text-red-700 dark:text-red-400"
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
          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={onBackToDashboard}
              className="rounded-xl border border-line bg-panel px-4 py-2.5 text-sm font-semibold hover:bg-surface transition"
            >
              Back to Overview
            </button>

            <button
              type="button"
              disabled={isRegenerating}
              onClick={() => onRegenerateSmartTest("weak_focus")}
              className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-brand-700 disabled:opacity-50 transition"
            >
              <Sparkles className="h-4 w-4" />
              <span>{isRegenerating ? "Regenerating..." : "1-Click Smart Remediation"}</span>
            </button>
          </div>
        </div>

        {/* Weak topic warning alert if any */}
        {weakTopics.length > 0 && (
          <div className="mt-4 flex items-center gap-2 rounded-xl bg-white/70 dark:bg-black/20 p-3 text-xs text-text border border-line">
            <TrendingDown className="h-4 w-4 text-red-500 shrink-0" />
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
                      ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300"
                      : tb.status === "Moderate"
                      ? "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300"
                      : "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300"
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
                      ? "bg-emerald-500"
                      : tb.status === "Moderate"
                      ? "bg-amber-500"
                      : "bg-red-500"
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
              className={`rounded-2xl border p-5 transition shadow-xs ${
                isCorrect
                  ? "border-emerald-200 bg-panel dark:border-emerald-950/60"
                  : "border-red-200 bg-panel dark:border-red-950/60"
              }`}
            >
              {/* Question Header */}
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2.5">
                  {isCorrect ? (
                    <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600 shrink-0" />
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
                      ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950"
                      : "bg-red-100 text-red-700 dark:bg-red-950"
                  }`}
                >
                  {isCorrect ? "Correct" : "Incorrect"}
                </span>
              </div>

              {/* Question Text */}
              <p className="mt-3 text-sm font-semibold leading-relaxed">{q.question_text}</p>

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
                      "border-emerald-500 bg-emerald-50/70 font-semibold text-emerald-900 dark:bg-emerald-950/50 dark:text-emerald-200 ring-1 ring-emerald-500";
                  } else if (isStudentPick && !isRightAnswer) {
                    styleClass =
                      "border-red-500 bg-red-50/70 font-semibold text-red-900 dark:bg-red-950/50 dark:text-red-200 line-through";
                  }

                  return (
                    <div
                      key={key}
                      className={`flex items-start gap-2.5 rounded-xl border p-3 text-xs leading-snug ${styleClass}`}
                    >
                      <span className="font-bold shrink-0">{key}.</span>
                      <span className="truncate">{optText}</span>
                    </div>
                  );
                })}
              </div>

              {/* Pedagogical Feedback / Rationale */}
              <div className="mt-4 rounded-xl border border-line bg-surface p-3.5 text-xs leading-relaxed">
                <div className="flex items-center gap-1.5 font-bold text-brand-600 mb-1">
                  <BookOpen className="h-3.5 w-3.5" />
                  <span>Pedagogical Analysis & Source Reference</span>
                </div>
                <p className="text-text">{q.explanation}</p>
              </div>

              {/* Collapsible View Solution for Quantitative Questions */}
              {q.is_quantitative && (
                <div className="mt-3">
                  <button
                    type="button"
                    onClick={() => toggleSolution(q.question_id)}
                    className="flex items-center gap-1.5 text-xs font-semibold text-brand-600 hover:text-brand-700 transition"
                  >
                    <span>{isSolutionOpen ? "Hide Step-by-Step Proof" : "View Solution & Formula Proof"}</span>
                    {isSolutionOpen ? (
                      <ChevronUp className="h-3.5 w-3.5" />
                    ) : (
                      <ChevronDown className="h-3.5 w-3.5" />
                    )}
                  </button>

                  {isSolutionOpen && (
                    <div className="mt-3 rounded-xl border border-brand-200 bg-brand-50/40 dark:bg-brand-950/20 p-4 space-y-3">
                      {q.formula_latex && (
                        <div>
                          <p className="text-xs font-semibold text-brand-700 uppercase tracking-wide">
                            Governing LaTeX Formula:
                          </p>
                          <KaTeXViewer math={q.formula_latex} className="my-1 text-sm font-semibold" />
                        </div>
                      )}

                      {q.step_by_step_solution && q.step_by_step_solution.length > 0 && (
                        <div>
                          <p className="text-xs font-semibold text-brand-700 uppercase tracking-wide mb-1.5">
                            Intermediate Derivation Proof:
                          </p>
                          <ol className="list-decimal list-inside space-y-1 text-xs text-text">
                            {q.step_by_step_solution.map((step, idx) => (
                              <li key={idx} className="leading-relaxed">
                                {step}
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
