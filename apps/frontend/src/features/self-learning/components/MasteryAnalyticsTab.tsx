import React from "react";
import {
  CheckCircle,
  AlertCircle,
  HelpCircle,
  BarChart3,
  Sparkles,
  Radar,
  Target,
  TrendingDown,
} from "lucide-react";
import type { SelfLearningTest, SubjectMasteryOut } from "../types";
import { TopicMasteryRadarChart } from "./TopicMasteryRadarChart";

interface MasteryAnalyticsTabProps {
  mastery: SubjectMasteryOut | null;
  tests: SelfLearningTest[];
  onTakeTestForTopic: (topic: string) => void;
  onSmartRegenerateGaps?: (weakTopics: string[]) => Promise<void>;
  isRegenerating?: boolean;
}

export const MasteryAnalyticsTab: React.FC<MasteryAnalyticsTabProps> = ({
  mastery,
  tests,
  onTakeTestForTopic,
  onSmartRegenerateGaps,
  isRegenerating = false,
}) => {
  if (!mastery || (mastery.total_questions_attempted === 0 && tests.length === 0)) {
    return (
      <div className="rounded-2xl border border-line bg-panel p-10 text-center text-muted">
        <BarChart3 className="h-10 w-10 mx-auto mb-3 opacity-40 text-brand-600" />
        <h3 className="text-base font-bold text-text">No Assessment Data Yet</h3>
        <p className="text-sm mt-1 max-w-md mx-auto">
          Complete practice tests for this subject to unlock your syllabus mastery radar chart,
          document-cited diagnostic feedback, and 1-click knowledge gap regeneration.
        </p>
      </div>
    );
  }

  const overall = mastery.overall_mastery_percentage;
  const weakTopics = mastery.topics.filter((t) => t.status === "Weak");
  const moderateTopics = mastery.topics.filter((t) => t.status === "Moderate");
  const gapTopicNames = [
    ...weakTopics.map((t) => t.topic),
    ...moderateTopics.slice(0, 2).map((t) => t.topic),
  ];

  return (
    <div className="space-y-6">
      {/* Overview Stat Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl border border-line bg-panel p-5 shadow-xs">
          <span className="text-xs font-semibold text-muted uppercase">Overall Mastery</span>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-primary-ink font-mono">
              {overall.toFixed(1)}%
            </span>
          </div>
          <p className="text-xs text-muted mt-1">
            Across {mastery.total_questions_attempted} attempted questions ({mastery.total_tests_taken} tests)
          </p>
        </div>

        <div className="rounded-2xl border border-line bg-panel p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-muted uppercase">Strong (≥75%)</span>
            <CheckCircle className="h-4 w-4 text-success-ink" />
          </div>
          <div className="mt-2 text-3xl font-extrabold text-success-ink font-mono">
            {mastery.strong_topics_count}
          </div>
          <p className="text-xs text-muted mt-1">Exam-ready syllabus mastery</p>
        </div>

        <div className="rounded-2xl border border-line bg-panel p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-muted uppercase">Moderate (50–74%)</span>
            <HelpCircle className="h-4 w-4 text-warning-ink" />
          </div>
          <div className="mt-2 text-3xl font-extrabold text-warning-ink font-mono">
            {mastery.moderate_topics_count}
          </div>
          <p className="text-xs text-muted mt-1">Approaching solid mastery</p>
        </div>

        <div className="rounded-2xl border border-line bg-panel p-5 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-muted uppercase">Weak (&lt;50%)</span>
            <AlertCircle className="h-4 w-4 text-danger-ink" />
          </div>
          <div className="mt-2 text-3xl font-extrabold text-danger-ink font-mono">
            {mastery.weak_topics_count}
          </div>
          <p className="text-xs text-muted mt-1">High-priority remediation targets</p>
        </div>
      </div>

      {/* Radar Chart + 1-Click Smart Regenerate Knowledge Gaps Panel */}
      <div className="grid gap-6 lg:grid-cols-[1.15fr_1fr]">
        {/* Interactive Syllabus Mastery Radar Chart */}
        <div className="rounded-2xl border border-line bg-panel p-6 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Radar className="h-5 w-5 text-primary-ink" />
              <div>
                <h3 className="text-base font-bold">Syllabus Topic Mastery Radar</h3>
                <p className="text-xs text-muted">
                  Polar diagnostic profile across Strong (≥75%), Moderate (50–74%), and Weak (&lt;50%) zones
                </p>
              </div>
            </div>
            <span className="text-xs font-semibold bg-surface border border-line px-2.5 py-1 rounded-full">
              {mastery.topics.length} Indexed Topics
            </span>
          </div>

          {mastery.topics.length > 0 ? (
            <TopicMasteryRadarChart
              topics={mastery.topics}
              onSelectTopic={(topic) => onTakeTestForTopic(topic)}
            />
          ) : (
            <p className="text-xs text-muted py-8 text-center">
              Submit at least one practice test to plot your syllabus radar polygon.
            </p>
          )}
        </div>

        {/* 1-Click Smart Regenerate & Priority Remediation Deck */}
        <div className="flex flex-col justify-between rounded-2xl border border-line bg-panel p-6 shadow-xs space-y-5">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-primary-ink" />
              <div>
                <h3 className="text-base font-bold">Adaptive Remediation Engine</h3>
                <p className="text-xs text-muted">
                  Auto-targeted practice focusing 70% of questions on identified syllabus knowledge gaps
                </p>
              </div>
            </div>

            {weakTopics.length > 0 ? (
              <div className="rounded-xl border border-danger/40 bg-danger-soft/70 p-4 space-y-2.5">
                <div className="flex items-center gap-2 text-xs font-bold text-danger-ink">
                  <TrendingDown className="h-4 w-4 shrink-0" />
                  <span>Priority Knowledge Gaps Detected ({weakTopics.length})</span>
                </div>
                <ul className="space-y-1.5 text-xs">
                  {weakTopics.slice(0, 4).map((w) => (
                    <li key={w.topic} className="flex items-center justify-between gap-2">
                      <span className="font-semibold text-ink truncate">{w.topic}</span>
                      <span className="font-mono font-bold text-danger-ink shrink-0">
                        {w.mastery_percentage}%
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="rounded-xl border border-success/40 bg-success-soft/70 p-4 text-xs text-success-ink">
                <strong>Great standing!</strong> No critical weak topics below 50%. Use Smart Regenerate to push Moderate topics past the 75% Strong mastery threshold.
              </div>
            )}

            {/* Recent Test History Summary */}
            <div className="space-y-2">
              <p className="text-xs font-bold uppercase tracking-wider text-muted">
                Recent Assessments ({tests.length})
              </p>
              {tests.length === 0 ? (
                <p className="text-xs text-muted">No assessments recorded yet.</p>
              ) : (
                <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
                  {tests.slice(0, 4).map((t) => (
                    <div
                      key={t.id}
                      className="flex items-center justify-between rounded-xl border border-line bg-surface px-3 py-2 text-xs"
                    >
                      <div className="truncate pr-2">
                        <p className="font-semibold text-ink truncate">{t.title}</p>
                        <p className="text-[11px] text-muted">
                          {t.total_questions} Qs · {t.difficulty.toUpperCase()} ·{" "}
                          {new Date(t.created_at).toLocaleDateString()}
                        </p>
                      </div>
                      <span className="rounded-md bg-panel border border-line px-2 py-0.5 text-[10px] font-bold uppercase text-primary-ink shrink-0">
                        {t.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Primary 1-Click Smart Regenerate CTA */}
          {onSmartRegenerateGaps && (
            <button
              type="button"
              disabled={isRegenerating || gapTopicNames.length === 0}
              onClick={() => void onSmartRegenerateGaps(gapTopicNames)}
              className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-4 py-3 text-sm font-bold text-on-primary shadow-xs hover:bg-primary-hover disabled:opacity-50 transition"
            >
              <Sparkles className="h-4 w-4" />
              <span>
                {isRegenerating
                  ? "Generating Gap-Focused Assessment…"
                  : weakTopics.length > 0
                  ? `1-Click Smart Regenerate (${weakTopics.length} Weak Topics)`
                  : "1-Click Smart Regenerate (Advance Mastery)"}
              </span>
            </button>
          )}
        </div>
      </div>

      {/* Detailed Topic Accuracy Profiler & Recommendations */}
      <div className="rounded-2xl border border-line bg-panel p-6 shadow-xs">
        <h3 className="text-base font-bold mb-1">Curriculum Topic Mastery & Diagnostic Recommendations</h3>
        <p className="text-xs text-muted mb-6">
          Topics classified by Bloom&apos;s taxonomy performance. Click any topic to launch a targeted practice test.
        </p>

        <div className="space-y-4">
          {mastery.topics.map((item, idx) => {
            const isStrong = item.status === "Strong";
            const isModerate = item.status === "Moderate";

            return (
              <div
                key={idx}
                className="rounded-xl border border-line bg-surface p-4 transition hover:border-primary/40"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2.5">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${
                        isStrong
                          ? "bg-success-soft text-success-ink"
                          : isModerate
                          ? "bg-warning-soft text-warning-ink"
                          : "bg-danger-soft text-danger-ink"
                      }`}
                    >
                      {item.status}
                    </span>
                    <h4 className="font-bold text-sm">{item.topic}</h4>
                  </div>

                  <div className="flex items-center gap-4">
                    <span className="text-xs text-muted">
                      {item.total_correct} / {item.total_attempted} correct (
                      <strong className="text-ink font-mono">{item.mastery_percentage}%</strong>)
                    </span>

                    <button
                      type="button"
                      onClick={() => onTakeTestForTopic(item.topic)}
                      className="inline-flex items-center gap-1 rounded-lg bg-panel border border-line px-3 py-1.5 text-xs font-semibold hover:bg-primary-soft hover:text-primary-ink transition"
                    >
                      <Sparkles className="h-3.5 w-3.5 text-primary-ink" />
                      <span>Target Test</span>
                    </button>
                  </div>
                </div>

                {/* Progress bar */}
                <div className="mt-3 h-2 w-full rounded-full bg-panel overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${
                      isStrong
                        ? "bg-success"
                        : isModerate
                        ? "bg-warning"
                        : "bg-danger"
                    }`}
                    style={{ width: `${Math.max(2, item.mastery_percentage)}%` }}
                  />
                </div>

                {/* Diagnostic Recommendation */}
                <p className="mt-2.5 text-xs text-muted leading-relaxed">
                  <strong>Diagnostic Recommendation:</strong> {item.recommendation}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
