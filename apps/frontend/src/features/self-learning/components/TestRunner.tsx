import React, { useState, useEffect } from "react";
import {
  Clock,
  CheckCircle,
  ChevronLeft,
  ChevronRight,
  Send,
  AlertTriangle,
} from "lucide-react";
import type { QuestionOut, SelfLearningTest } from "../types";
import { RichMathText } from "./KaTeXViewer";

interface TestRunnerProps {
  test: SelfLearningTest;
  onSubmit: (answers: Record<string, string>, timeTakenSeconds: number) => Promise<void>;
  onCancel: () => void;
  isSubmitting?: boolean;
}

export const TestRunner: React.FC<TestRunnerProps> = ({
  test,
  onSubmit,
  onCancel,
  isSubmitting = false,
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [timeLeft, setTimeLeft] = useState<number>(test.questions.length * 60); // 60s per question
  const [timeTaken, setTimeTaken] = useState(0);
  const [showConfirmModal, setShowConfirmModal] = useState(false);

  const questions: QuestionOut[] = test.questions || [];
  const currentQuestion: QuestionOut | undefined = questions[currentIndex];

  // Countdown timer
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          void handleAutoSubmit();
          return 0;
        }
        return prev - 1;
      });
      setTimeTaken((t) => t + 1);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleSelectOption = (questionId: string, optionKey: string) => {
    setAnswers((prev) => ({
      ...prev,
      [questionId]: optionKey,
    }));
  };

  const handleAutoSubmit = async () => {
    await onSubmit(answers, timeTaken);
  };

  const handleManualSubmit = async () => {
    setShowConfirmModal(false);
    await onSubmit(answers, timeTaken);
  };

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const answeredCount = Object.keys(answers).length;
  const isAllAnswered = answeredCount === questions.length;

  if (!currentQuestion) {
    return (
      <div className="p-8 text-center text-muted">
        <p>No questions found in this assessment.</p>
        <button
          type="button"
          onClick={onCancel}
          className="mt-4 rounded-xl bg-brand-600 px-4 py-2 text-sm font-semibold text-white"
        >
          Return to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top Header & Countdown Timer */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-line bg-panel p-4 shadow-xs">
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-brand-600">
            {test.difficulty.toUpperCase()} CALIBRATION
          </span>
          <h2 className="text-lg font-bold">{test.title}</h2>
        </div>

        <div className="flex items-center gap-4">
          {/* Countdown Clock */}
          <div
            className={`flex items-center gap-2 rounded-xl px-3.5 py-1.5 text-sm font-mono font-bold ${
              timeLeft < 120
                ? "bg-red-50 text-red-600 dark:bg-red-950/50 border border-red-200 animate-pulse"
                : "bg-surface border border-line text-text"
            }`}
          >
            <Clock className="h-4 w-4" />
            <span>{formatTimer(timeLeft)}</span>
          </div>

          <button
            type="button"
            onClick={() => setShowConfirmModal(true)}
            disabled={isSubmitting}
            className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-xs hover:bg-emerald-700 disabled:opacity-50 transition"
          >
            <Send className="h-4 w-4" />
            <span>Finish Test</span>
          </button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-4">
        {/* Left: Active Question Card */}
        <div className="lg:col-span-3 space-y-4">
          <div className="rounded-2xl border border-line bg-panel p-6 shadow-xs">
            <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-muted pb-3 border-b border-line">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-ink">
                  Question {currentIndex + 1} of {questions.length}
                </span>
                {currentQuestion.topic_tag && (
                  <span className="rounded-md bg-surface px-2 py-0.5 border border-line">
                    {currentQuestion.topic_tag}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                {currentQuestion.is_quantitative && (
                  <span className="rounded-full bg-indigo-500/10 px-2.5 py-0.5 text-indigo-600 dark:text-indigo-300 font-bold">
                    Numerical Solver (LaTeX)
                  </span>
                )}
                <span className="rounded-full bg-surface px-2.5 py-0.5 border border-line font-medium">
                  Bloom&apos;s: {currentQuestion.bloom_level}
                </span>
              </div>
            </div>

            {/* Question Text */}
            <div className="mt-4 text-base font-semibold leading-relaxed">
              <RichMathText text={currentQuestion.question_text} />
            </div>

            {/* Options List */}
            <div className="mt-6 space-y-3">
              {(["A", "B", "C", "D"] as const).map((key) => {
                const optText = currentQuestion.options[key];
                if (!optText) return null;
                const isSelected = answers[currentQuestion.id] === key;

                return (
                  <button
                    key={key}
                    type="button"
                    onClick={() => handleSelectOption(currentQuestion.id, key)}
                    className={`flex w-full items-start gap-3.5 rounded-xl border p-4 text-left text-sm transition ${
                      isSelected
                        ? "border-brand-600 bg-brand-50/60 font-semibold text-brand-900 dark:bg-brand-950/40 dark:text-brand-200 ring-1 ring-brand-600"
                        : "border-line bg-surface hover:border-brand-300"
                    }`}
                  >
                    <span
                      className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                        isSelected
                          ? "bg-brand-600 text-white"
                          : "bg-panel border border-line text-muted"
                      }`}
                    >
                      {key}
                    </span>
                    <span className="mt-0.5 leading-snug break-words">
                      <RichMathText text={optText} />
                    </span>
                  </button>
                );
              })}
            </div>

            {/* Next / Prev Navigation */}
            <div className="mt-8 flex items-center justify-between pt-4 border-t border-line">
              <button
                type="button"
                disabled={currentIndex === 0}
                onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
                className="inline-flex items-center gap-1.5 rounded-xl border border-line px-4 py-2 text-sm font-semibold hover:bg-surface disabled:opacity-40 transition"
              >
                <ChevronLeft className="h-4 w-4" />
                <span>Previous</span>
              </button>

              <button
                type="button"
                disabled={currentIndex === questions.length - 1}
                onClick={() => setCurrentIndex((i) => Math.min(questions.length - 1, i + 1))}
                className="inline-flex items-center gap-1.5 rounded-xl bg-brand-600 px-5 py-2 text-sm font-semibold text-white shadow-xs hover:bg-brand-700 disabled:opacity-40 transition"
              >
                <span>Next Question</span>
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Right: Question Navigator Panel */}
        <div className="space-y-4">
          <div className="rounded-2xl border border-line bg-panel p-5 shadow-xs">
            <h4 className="font-bold text-sm mb-1">Question Navigator</h4>
            <p className="text-xs text-muted mb-4">
              {answeredCount} of {questions.length} answered
            </p>

            <div className="grid grid-cols-5 gap-2">
              {questions.map((q, idx) => {
                const isAnswered = Boolean(answers[q.id]);
                const isCurrent = idx === currentIndex;

                return (
                  <button
                    key={q.id}
                    type="button"
                    onClick={() => setCurrentIndex(idx)}
                    className={`h-9 w-9 rounded-xl text-xs font-bold transition flex items-center justify-center ${
                      isCurrent
                        ? "ring-2 ring-brand-600 ring-offset-2 bg-brand-600 text-white"
                        : isAnswered
                        ? "bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 font-semibold"
                        : "bg-surface border border-line text-muted hover:border-brand-400"
                    }`}
                  >
                    {idx + 1}
                  </button>
                );
              })}
            </div>

            <div className="mt-6 flex flex-col gap-2 pt-4 border-t border-line text-xs text-muted">
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
                <span>Answered</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="h-2.5 w-2.5 rounded-full bg-surface border border-line" />
                <span>Unanswered</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
          <div className="w-full max-w-md rounded-2xl border border-line bg-panel p-6 shadow-2xl">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-600 dark:bg-amber-950/50">
                <AlertTriangle className="h-5 w-5" />
              </div>
              <div>
                <h3 className="font-bold text-base">Submit Test Assessment?</h3>
                <p className="text-xs text-muted">
                  {isAllAnswered
                    ? "You have answered all questions."
                    : `You have answered ${answeredCount} of ${questions.length} questions.`}
                </p>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3 pt-4 border-t border-line">
              <button
                type="button"
                onClick={() => setShowConfirmModal(false)}
                className="rounded-xl border border-line px-4 py-2 text-sm font-semibold hover:bg-surface"
              >
                Continue Test
              </button>
              <button
                type="button"
                onClick={handleManualSubmit}
                disabled={isSubmitting}
                className="rounded-xl bg-emerald-600 px-5 py-2 text-sm font-semibold text-white shadow-xs hover:bg-emerald-700 disabled:opacity-50"
              >
                {isSubmitting ? "Grading..." : "Confirm & Submit"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
