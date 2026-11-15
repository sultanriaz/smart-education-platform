import React, { useState } from "react";
import {
  FileQuestion,
  Play,
  RotateCcw,
  Plus,
  Trash2,
  Sparkles,
  Calendar,
  CheckCircle2,
  X,
} from "lucide-react";
import type { SelfLearningMaterial, SelfLearningTest, TestGeneratePayload } from "../types";

interface PracticeTestsTabProps {
  tests: SelfLearningTest[];
  materials: SelfLearningMaterial[];
  onGenerateTest: (payload: TestGeneratePayload) => Promise<void>;
  onStartTest: (test: SelfLearningTest) => void;
  onViewResult: (test: SelfLearningTest) => void;
  onDeleteTest: (testId: string) => Promise<void>;
  isGenerating?: boolean;
}

export const PracticeTestsTab: React.FC<PracticeTestsTabProps> = ({
  tests,
  materials,
  onGenerateTest,
  onStartTest,
  onViewResult,
  onDeleteTest,
  isGenerating = false,
}) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [count, setCount] = useState(10);
  const [difficulty, setDifficulty] = useState<"basic" | "medium" | "hard" | "mixed">("mixed");
  const [selectedTopics, setSelectedTopics] = useState<string[]>([]);
  const [testTitle, setTestTitle] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Collect all unique extracted topics from subject materials
  const allTopics: string[] = [];
  materials.forEach((m) => {
    (m.extracted_topics || []).forEach((t) => {
      if (!allTopics.includes(t)) allTopics.push(t);
    });
  });

  const toggleTopic = (topic: string) => {
    setSelectedTopics((prev) =>
      prev.includes(topic) ? prev.filter((t) => t !== topic) : [...prev, topic]
    );
  };

  const handleCreateTest = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await onGenerateTest({
        subject_id: "", // filled by parent
        count,
        difficulty,
        topics: selectedTopics.length > 0 ? selectedTopics : undefined,
        title: testTitle.trim() || undefined,
      });
      setModalOpen(false);
      setTestTitle("");
      setSelectedTopics([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate test.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Generate Button */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-bold">Personalized Assessment Engine</h3>
          <p className="text-xs text-muted">
            Generate Bloom's-calibrated practice tests powered by LangGraph and Google Gemini.
          </p>
        </div>

        <button
          type="button"
          onClick={() => setModalOpen(true)}
          className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white shadow-xs hover:bg-brand-700 transition"
        >
          <Plus className="h-4 w-4" />
          <span>Generate New Assessment</span>
        </button>
      </div>

      {/* Test Inventory */}
      {tests.length === 0 ? (
        <div className="rounded-2xl border border-line bg-panel p-10 text-center text-muted">
          <FileQuestion className="h-10 w-10 mx-auto mb-3 opacity-40 text-brand-600" />
          <p className="text-base font-bold text-text">No practice tests generated yet.</p>
          <p className="text-xs mt-1 max-w-sm mx-auto">
            Click &quot;Generate New Assessment&quot; to create a custom test calibrated to your syllabus materials.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {tests.map((t) => (
            <div
              key={t.id}
              className="flex flex-col justify-between rounded-2xl border border-line bg-panel p-5 shadow-xs transition hover:border-brand-200"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span
                      className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                        t.difficulty === "hard"
                          ? "bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300"
                          : t.difficulty === "basic"
                          ? "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300"
                          : "bg-brand-100 text-brand-800 dark:bg-brand-950 dark:text-brand-300"
                      }`}
                    >
                      {t.difficulty}
                    </span>
                    <h4 className="font-bold text-base mt-2 line-clamp-1">{t.title}</h4>
                    <p className="text-xs text-muted mt-1">
                      {t.total_questions} Questions • Created {new Date(t.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => onDeleteTest(t.id)}
                    className="rounded-lg p-1.5 text-muted hover:bg-red-50 hover:text-red-600 transition"
                    title="Delete test"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>

                {t.target_topics && t.target_topics.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1">
                    {t.target_topics.slice(0, 3).map((top, idx) => (
                      <span
                        key={idx}
                        className="rounded-md bg-surface border border-line px-2 py-0.5 text-[11px] text-muted truncate max-w-[200px]"
                      >
                        {top}
                      </span>
                    ))}
                    {t.target_topics.length > 3 && (
                      <span className="text-[11px] text-muted self-center">
                        +{t.target_topics.length - 3} more
                      </span>
                    )}
                  </div>
                )}
              </div>

              <div className="mt-5 flex items-center justify-between gap-3 pt-3 border-t border-line">
                <button
                  type="button"
                  onClick={() => onViewResult(t)}
                  className="rounded-xl border border-line px-3.5 py-2 text-xs font-semibold hover:bg-surface transition"
                >
                  View Last Result
                </button>

                <button
                  type="button"
                  onClick={() => onStartTest(t)}
                  className="inline-flex items-center gap-1.5 rounded-xl bg-brand-600 px-4 py-2 text-xs font-semibold text-white shadow-xs hover:bg-brand-700 transition"
                >
                  <Play className="h-3.5 w-3.5" />
                  <span>Start Test</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Generate Assessment Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
          <div className="w-full max-w-lg rounded-2xl border border-line bg-panel p-6 shadow-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-3 border-b border-line">
              <div className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-brand-600" />
                <h3 className="text-lg font-bold">Generate Practice Assessment</h3>
              </div>
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="rounded-lg p-1 text-muted hover:bg-surface"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateTest} className="mt-4 space-y-4">
              {error && (
                <div className="rounded-xl bg-red-50 p-3 text-xs text-red-700 border border-red-200">
                  {error}
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-muted uppercase">Assessment Title</label>
                <input
                  type="text"
                  placeholder="e.g. Unit 3: Transformers & Attention Synthesis"
                  value={testTitle}
                  onChange={(e) => setTestTitle(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-line bg-surface p-2.5 text-sm"
                />
              </div>

              {/* Question count (5 to 30) */}
              <div>
                <div className="flex justify-between items-center text-xs font-semibold text-muted uppercase">
                  <span>Questions Count</span>
                  <span className="font-mono text-brand-600 text-sm font-bold">{count} Questions</span>
                </div>
                <input
                  type="range"
                  min="5"
                  max="30"
                  step="1"
                  value={count}
                  onChange={(e) => setCount(parseInt(e.target.value, 10))}
                  className="mt-2 w-full accent-brand-600 cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-muted font-mono mt-0.5">
                  <span>5 (Quick Quiz)</span>
                  <span>15</span>
                  <span>30 (Full Exam)</span>
                </div>
              </div>

              {/* Difficulty calibration */}
              <div>
                <label className="block text-xs font-semibold text-muted uppercase mb-2">
                  Bloom&apos;s Taxonomy Calibration
                </label>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {[
                    { key: "basic", label: "Basic (Recall)", desc: "Remembering & Understanding" },
                    { key: "medium", label: "Medium (Applied)", desc: "Applying & Analyzing" },
                    { key: "hard", label: "Hard (Synthesis)", desc: "Evaluating & Creating" },
                    { key: "mixed", label: "Mixed (Balanced)", desc: "Proportional Bloom's Distribution" },
                  ].map((d) => (
                    <button
                      key={d.key}
                      type="button"
                      onClick={() => setDifficulty(d.key as any)}
                      className={`p-3 rounded-xl border text-left transition ${
                        difficulty === d.key
                          ? "border-brand-600 bg-brand-50/70 text-brand-900 dark:bg-brand-950/40 dark:text-brand-200 font-semibold ring-1 ring-brand-600"
                          : "border-line bg-surface hover:border-brand-300"
                      }`}
                    >
                      <p className="font-bold">{d.label}</p>
                      <p className="text-[10px] text-muted mt-0.5 leading-tight">{d.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Topics Filter */}
              {allTopics.length > 0 && (
                <div>
                  <label className="block text-xs font-semibold text-muted uppercase mb-1.5">
                    Filter by Extracted Topics ({selectedTopics.length} selected)
                  </label>
                  <p className="text-[11px] text-muted mb-2">
                    Leave unselected to cover all curriculum chapters evenly.
                  </p>
                  <div className="max-h-36 overflow-y-auto space-y-1.5 rounded-xl border border-line bg-surface p-2">
                    {allTopics.map((top) => {
                      const isChecked = selectedTopics.includes(top);
                      return (
                        <button
                          key={top}
                          type="button"
                          onClick={() => toggleTopic(top)}
                          className={`flex items-center gap-2 w-full text-left p-1.5 rounded-lg text-xs transition ${
                            isChecked
                              ? "bg-brand-100 text-brand-800 dark:bg-brand-950 dark:text-brand-300 font-semibold"
                              : "hover:bg-panel"
                          }`}
                        >
                          <span
                            className={`h-4 w-4 rounded border flex items-center justify-center shrink-0 ${
                              isChecked
                                ? "bg-brand-600 border-brand-600 text-white"
                                : "border-line bg-panel"
                            }`}
                          >
                            {isChecked && <CheckCircle2 className="h-3 w-3" />}
                          </span>
                          <span className="truncate">{top}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              <div className="mt-6 flex justify-end gap-3 pt-4 border-t border-line">
                <button
                  type="button"
                  onClick={() => setModalOpen(false)}
                  className="rounded-xl border border-line px-4 py-2 text-sm font-semibold hover:bg-surface"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting || isGenerating}
                  className="rounded-xl bg-brand-600 px-5 py-2 text-sm font-semibold text-white shadow-xs hover:bg-brand-700 disabled:opacity-50"
                >
                  {submitting || isGenerating ? "Executing LangGraph Pipeline..." : "Generate Test"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
