import { lazy, Suspense, useState, useEffect, useCallback } from "react";
import {
  BookOpen,
  FolderOpen,
  FileQuestion,
  BarChart2,
  Library,
  ArrowLeft,
} from "lucide-react";
import { PageHeader } from "../../components/ui/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { InlineError } from "../../components/ui/InlineError";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { useToast } from "../../components/ui/useToast";

// Existing hooks & helpers for institutional resources
import {
  useRecommendations,
  useLearningActivity,
  useResources,
} from "../../features/student/hooks";
import {
  downloadLearningResource,
  logLearningResourceView,
} from "../../features/student/student-api";
import type { LearningResource } from "../../features/student/types";

// Self-Learning components and API (lazy-loaded per tab to keep KaTeX & radar chart off initial render)
import { SubjectSwitcher } from "../../features/self-learning/components/SubjectSwitcher";

const MaterialLibraryTab = lazy(() =>
  import("../../features/self-learning/components/MaterialLibraryTab").then((m) => ({
    default: m.MaterialLibraryTab,
  }))
);
const PracticeTestsTab = lazy(() =>
  import("../../features/self-learning/components/PracticeTestsTab").then((m) => ({
    default: m.PracticeTestsTab,
  }))
);
const MasteryAnalyticsTab = lazy(() =>
  import("../../features/self-learning/components/MasteryAnalyticsTab").then((m) => ({
    default: m.MasteryAnalyticsTab,
  }))
);
const TestRunner = lazy(() =>
  import("../../features/self-learning/components/TestRunner").then((m) => ({
    default: m.TestRunner,
  }))
);
const TestReviewScreen = lazy(() =>
  import("../../features/self-learning/components/TestReviewScreen").then((m) => ({
    default: m.TestReviewScreen,
  }))
);
import {
  getSubjects,
  createSubject,
  getMaterials,
  uploadMaterial,
  deleteMaterial,
  getStorageQuota,
  listTests,
  generateTest,
  deleteTest,
  submitTest,
  getTestResult,
  regenerateTest,
  getSubjectMastery,
} from "../../features/self-learning/self-learning-api";
import type {
  SelfLearningSubject,
  SelfLearningMaterial,
  SelfLearningTest,
  StorageQuota,
  SubjectCreatePayload,
  SubjectMasteryOut,
  TestGeneratePayload,
  TestResultOut,
} from "../../features/self-learning/types";

function InstitutionalResourceCard({
  resource,
  recommended = false,
}: {
  resource: LearningResource;
  recommended?: boolean;
}) {
  const toast = useToast();

  const download = async () => {
    try {
      await downloadLearningResource(resource.id);
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Download failed.", "error");
    }
  };

  return (
    <Card>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-brand-700">
            {recommended ? "Recommended" : resource.resourceType ?? "Resource"}
          </p>
          <h2 className="mt-1 text-lg font-semibold">{resource.title}</h2>
        </div>
        {typeof resource.score === "number" ? (
          <span className="rounded-full bg-brand-50 px-2.5 py-1 text-xs font-semibold text-brand-700">
            Score {resource.score}
          </span>
        ) : null}
      </div>

      {recommended && resource.reason ? (
        <p className="mt-2 text-sm text-brand-700" aria-label="Recommendation reason">
          Recommended because: {resource.reason}
        </p>
      ) : null}

      {resource.description ? (
        <p className="mt-3 text-sm leading-6 text-muted">{resource.description}</p>
      ) : null}

      {resource.textContent ? (
        <details
          className="mt-5 rounded-xl border border-line p-4"
          onToggle={(event) => {
            if (event.currentTarget.open) {
              void logLearningResourceView(resource.id).catch(() =>
                toast.push("Activity could not be recorded.", "error")
              );
            }
          }}
        >
          <summary className="cursor-pointer font-semibold">Read notes</summary>
          <p className="mt-3 whitespace-pre-wrap text-sm leading-7">{resource.textContent}</p>
        </details>
      ) : resource.externalUrl && /^https?:\/\//i.test(resource.externalUrl) ? (
        <a
          href={resource.externalUrl}
          onClick={() =>
            void logLearningResourceView(resource.id).catch(() =>
              toast.push("Activity could not be recorded.", "error")
            )
          }
          target="_blank"
          rel="noreferrer"
          className="mt-5 inline-flex rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-on-primary hover:bg-primary-hover transition"
        >
          Open resource
        </a>
      ) : (
        <Button className="mt-5" onClick={() => void download()}>
          Download
        </Button>
      )}
    </Card>
  );
}

export function StudentLearningPage() {
  const toast = useToast();

  // Self-Learning state
  const [subjects, setSubjects] = useState<SelfLearningSubject[]>([]);
  const [activeSubject, setActiveSubject] = useState<SelfLearningSubject | null>(null);
  const [materials, setMaterials] = useState<SelfLearningMaterial[]>([]);
  const [quota, setQuota] = useState<StorageQuota | null>(null);
  const [tests, setTests] = useState<SelfLearningTest[]>([]);
  const [mastery, setMastery] = useState<SubjectMasteryOut | null>(null);

  // Active view mode: workspace tabs vs test runner vs test review
  type TabType = "materials" | "tests" | "mastery" | "institutional";
  const [activeTab, setActiveTab] = useState<TabType>("materials");
  const [preselectedTopic, setPreselectedTopic] = useState<string | null>(null);

  // Runner & Review state
  const [activeRunningTest, setActiveRunningTest] = useState<SelfLearningTest | null>(null);
  const [activeReviewResult, setActiveReviewResult] = useState<TestResultOut | null>(null);
  const [reviewedTestId, setReviewedTestId] = useState<string | null>(null);

  // Loading & error states
  const [loadingInitial, setLoadingInitial] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [loadingSubjectData, setLoadingSubjectData] = useState(false);
  const [subjectError, setSubjectError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);

  // Institutional resources state
  const resources = useResources();
  const recommendations = useRecommendations();
  const [activityPage, setActivityPage] = useState(0);
  const activity = useLearningActivity(activityPage * 25);
  const [search, setSearch] = useState("");

  // Load subjects & quota on mount
  const refreshSubjects = useCallback(async () => {
    setLoadError(null);
    setLoadingInitial(true);
    try {
      const [subs, q] = await Promise.all([getSubjects(), getStorageQuota()]);
      setSubjects(subs);
      setQuota(q);
      if (subs.length > 0 && !activeSubject) {
        setActiveSubject(subs[0] ?? null);
      }
    } catch (err) {
      setLoadError(
        err instanceof Error
          ? err.message
          : "Could not load Self-Directed Learning Hub."
      );
    } finally {
      setLoadingInitial(false);
    }
  }, [activeSubject]);

  useEffect(() => {
    void refreshSubjects();
  }, [refreshSubjects]);

  // Load subject-specific data when active subject changes
  const loadSubjectData = useCallback(async (subjectId: string) => {
    setSubjectError(null);
    setLoadingSubjectData(true);
    try {
      const [mats, tsts, mst] = await Promise.all([
        getMaterials(subjectId),
        listTests(subjectId),
        getSubjectMastery(subjectId).catch(() => null),
      ]);
      setMaterials(mats);
      setTests(tsts);
      setMastery(mst);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Could not load subject data.";
      setSubjectError(message);
      toast.push(message, "error");
    } finally {
      setLoadingSubjectData(false);
    }
  }, [toast]);

  useEffect(() => {
    if (activeSubject) {
      void loadSubjectData(activeSubject.id);
    }
  }, [activeSubject, loadSubjectData]);

  // Action handlers
  const handleCreateSubject = async (payload: SubjectCreatePayload) => {
    try {
      const newSub = await createSubject(payload);
      setSubjects((prev) => [newSub, ...prev]);
      setActiveSubject(newSub);
      toast.push(`Subject "${newSub.name}" created successfully!`, "success");
    } catch (err) {
      toast.push(err instanceof Error ? err.message : "Failed to create subject.", "error");
      throw err;
    }
  };

  const handleUploadMaterial = async (file: File, title?: string) => {
    if (!activeSubject) return;
    setIsUploading(true);
    try {
      const mat = await uploadMaterial(activeSubject.id, file, title);
      setMaterials((prev) => [mat, ...prev]);
      const updatedQuota = await getStorageQuota();
      setQuota(updatedQuota);
      toast.push(`Uploaded "${mat.file_name}" and discovered topics!`, "success");
    } catch (err) {
      toast.push(err instanceof Error ? err.message : "Upload failed.", "error");
      throw err;
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteMaterial = async (materialId: string) => {
    try {
      await deleteMaterial(materialId);
      setMaterials((prev) => prev.filter((m) => m.id !== materialId));
      const updatedQuota = await getStorageQuota();
      setQuota(updatedQuota);
      toast.push("Study material removed.", "success");
    } catch (err) {
      toast.push(err instanceof Error ? err.message : "Delete failed.", "error");
      throw err;
    }
  };

  const handleGenerateTest = async (payload: TestGeneratePayload) => {
    if (!activeSubject) return;
    setIsGenerating(true);
    try {
      const newTest = await generateTest({
        ...payload,
        subject_id: activeSubject.id,
      });
      setTests((prev) => [newTest, ...prev]);
      toast.push(`Generated test with ${newTest.total_questions} questions!`, "success");
    } catch (err) {
      toast.push(err instanceof Error ? err.message : "Generation failed.", "error");
      throw err;
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDeleteTest = async (testId: string) => {
    try {
      await deleteTest(testId);
      setTests((prev) => prev.filter((t) => t.id !== testId));
      toast.push("Test deleted.", "success");
    } catch (err) {
      toast.push(err instanceof Error ? err.message : "Failed to delete test.", "error");
      throw err;
    }
  };

  const handleStartTest = (test: SelfLearningTest) => {
    setActiveRunningTest(test);
    setActiveReviewResult(null);
  };

  const handleSubmitTest = async (answers: Record<string, string>, timeTakenSeconds: number) => {
    if (!activeRunningTest) return;
    setIsSubmitting(true);
    try {
      const result = await submitTest(activeRunningTest.id, answers, timeTakenSeconds);
      setReviewedTestId(activeRunningTest.id);
      setActiveReviewResult(result);
      setActiveRunningTest(null);

      // Refresh tests and mastery
      if (activeSubject) {
        void loadSubjectData(activeSubject.id);
      }
      toast.push(
        `Test submitted! Score: ${result.score}/${result.total_questions} (${result.percentage}%)`,
        "success"
      );
    } catch (err) {
      toast.push(err instanceof Error ? err.message : "Failed to submit test.", "error");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleViewResult = async (test: SelfLearningTest) => {
    try {
      const result = await getTestResult(test.id);
      setReviewedTestId(test.id);
      setActiveReviewResult(result);
      setActiveRunningTest(null);
    } catch (err) {
      toast.push(err instanceof Error ? err.message : "No results found for this test.", "error");
    }
  };

  const handleRegenerateSmartTest = async (mode: "weak_focus" | "balanced" | "challenge") => {
    if (!reviewedTestId) return;
    setIsRegenerating(true);
    try {
      const regenerated = await regenerateTest(reviewedTestId, {
        mode,
        count: 10,
      });
      setTests((prev) => [regenerated, ...prev]);
      setActiveReviewResult(null);
      setActiveRunningTest(regenerated);
      toast.push(
        `Smart regenerated test ready (${mode.replace("_", " ")} mode)!`,
        "success"
      );
    } catch (err) {
      toast.push(err instanceof Error ? err.message : "Regeneration failed.", "error");
    } finally {
      setIsRegenerating(false);
    }
  };

  const handleSmartRegenerateGaps = async (weakTopics: string[]) => {
    if (!activeSubject) return;
    setIsRegenerating(true);
    try {
      let generated: SelfLearningTest;
      if (tests.length > 0 && tests[0]) {
        generated = await regenerateTest(tests[0].id, {
          mode: "weak_focus",
          count: 10,
        });
      } else {
        generated = await generateTest({
          subject_id: activeSubject.id,
          count: 10,
          difficulty: "medium",
          topics: weakTopics.length > 0 ? weakTopics : undefined,
          title: `Smart Gap Remediation (${weakTopics.slice(0, 2).join(", ") || activeSubject.name})`,
        });
      }
      setTests((prev) => [generated, ...prev]);
      setActiveRunningTest(generated);
      toast.push("1-Click Smart Remediation test ready! Focusing on your knowledge gaps.", "success");
    } catch (err) {
      toast.push(err instanceof Error ? err.message : "Smart regeneration failed.", "error");
    } finally {
      setIsRegenerating(false);
    }
  };

  const visibleResources = (resources.data ?? []).filter((r) =>
    `${r.title} ${r.description ?? ""}`.toLowerCase().includes(search.toLowerCase())
  );

  // If Test Runner is active
  if (activeRunningTest) {
    return (
      <div className="page-container py-6">
        <Suspense fallback={<SectionLoader label="Preparing assessment runner…" />}>
          <TestRunner
            test={activeRunningTest}
            onSubmit={handleSubmitTest}
            onCancel={() => setActiveRunningTest(null)}
            isSubmitting={isSubmitting}
          />
        </Suspense>
      </div>
    );
  }

  // If Test Review is active
  if (activeReviewResult) {
    return (
      <div className="page-container py-6">
        <button
          type="button"
          onClick={() => setActiveReviewResult(null)}
          className="mb-4 inline-flex items-center gap-2 text-sm font-semibold text-muted hover:text-text"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to Subject Workspace</span>
        </button>

        <Suspense fallback={<SectionLoader label="Rendering graded solution review…" />}>
          <TestReviewScreen
            result={activeReviewResult}
            onRegenerateSmartTest={handleRegenerateSmartTest}
            onBackToDashboard={() => setActiveReviewResult(null)}
            isRegenerating={isRegenerating}
          />
        </Suspense>
      </div>
    );
  }

  if (loadingInitial) {
    return (
      <div className="page-container">
        <SectionLoader label="Initializing Self-Directed Learning Hub…" />
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="page-container space-y-4">
        <PageHeader
          eyebrow="Gemini RAG & LangGraph Studio"
          title="AI Self-Learning & Adaptive Assessment Studio"
        />
        <InlineError
          message={loadError}
          onRetry={() => void refreshSubjects()}
        />
      </div>
    );
  }

  return (
    <div className="page-container space-y-6">
      {/* Workspace Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-line pb-4">
        <div>
          <PageHeader
            eyebrow="Gemini RAG & LangGraph Studio"
            title="AI Self-Learning & Adaptive Assessment Studio"
            description="Ingest syllabus handouts (.pdf, .docx, .pptx), generate Bloom's Taxonomy tests with LaTeX numerical proofs, and track topic mastery via radar analytics."
          />
        </div>

        {/* Subject Switcher + Add Subject Modal */}
        <div className="flex items-center gap-3">
          <SubjectSwitcher
            subjects={subjects}
            activeSubject={activeSubject}
            onSelectSubject={(sub) => setActiveSubject(sub)}
            onCreateSubject={handleCreateSubject}
            isLoading={loadingSubjectData}
          />
        </div>
      </div>

      {/* Primary Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-line pb-1 overflow-x-auto">
        <button
          type="button"
          onClick={() => setActiveTab("materials")}
          className={`flex items-center gap-2 px-4 py-2.5 text-sm font-semibold rounded-xl transition ${
            activeTab === "materials"
              ? "bg-primary-soft text-primary-ink"
              : "text-muted hover:text-ink hover:bg-panel"
          }`}
        >
          <FolderOpen className="h-4 w-4" />
          <span>Subject Ingestion Vault ({materials.length})</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("tests")}
          className={`flex items-center gap-2 px-4 py-2.5 text-sm font-semibold rounded-xl transition ${
            activeTab === "tests"
              ? "bg-primary-soft text-primary-ink"
              : "text-muted hover:text-ink hover:bg-panel"
          }`}
        >
          <FileQuestion className="h-4 w-4" />
          <span>Bloom&apos;s Test Generator ({tests.length})</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("mastery")}
          className={`flex items-center gap-2 px-4 py-2.5 text-sm font-semibold rounded-xl transition ${
            activeTab === "mastery"
              ? "bg-primary-soft text-primary-ink"
              : "text-muted hover:text-ink hover:bg-panel"
          }`}
        >
          <BarChart2 className="h-4 w-4" />
          <span>Diagnostic &amp; Mastery Profiler</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab("institutional")}
          className={`flex items-center gap-2 px-4 py-2.5 text-sm font-semibold rounded-xl transition ${
            activeTab === "institutional"
              ? "bg-primary-soft text-primary-ink"
              : "text-muted hover:text-ink hover:bg-panel"
          }`}
        >
          <Library className="h-4 w-4" />
          <span>Institutional Resources</span>
        </button>
      </div>

      {/* Active Tab Contents */}
      {!activeSubject && activeTab !== "institutional" ? (
        <Card className="py-12 text-center">
          <BookOpen className="h-12 w-12 mx-auto mb-3 text-brand-600 opacity-60" />
          <h3 className="text-lg font-bold">No Subject Selected</h3>
          <p className="text-sm text-muted mt-1 max-w-md mx-auto">
            Choose or create a subject in the header dropdown to begin uploading study materials and generating personalized assessments.
          </p>
        </Card>
      ) : loadingSubjectData ? (
        <SectionLoader label="Loading subject workspace data…" />
      ) : subjectError && activeTab !== "institutional" && activeSubject ? (
        <InlineError
          message={subjectError}
          onRetry={() => void loadSubjectData(activeSubject.id)}
        />
      ) : (
        <div>
          <Suspense fallback={<SectionLoader label="Loading learning workspace module…" />}>
            {activeTab === "materials" && (
              <MaterialLibraryTab
                materials={materials}
                quota={quota}
                onUpload={handleUploadMaterial}
                onDeleteMaterial={handleDeleteMaterial}
                isUploading={isUploading}
              />
            )}

            {activeTab === "tests" && (
              <PracticeTestsTab
                tests={tests}
                materials={materials}
                onGenerateTest={handleGenerateTest}
                onStartTest={handleStartTest}
                onViewResult={handleViewResult}
                onDeleteTest={handleDeleteTest}
                isGenerating={isGenerating}
                preselectedTopic={preselectedTopic}
                onClearPreselectedTopic={() => setPreselectedTopic(null)}
              />
            )}

            {activeTab === "mastery" && (
              <MasteryAnalyticsTab
                mastery={mastery}
                tests={tests}
                onTakeTestForTopic={(topic) => {
                  setPreselectedTopic(topic);
                  setActiveTab("tests");
                }}
                onSmartRegenerateGaps={handleSmartRegenerateGaps}
                isRegenerating={isRegenerating}
              />
            )}
          </Suspense>

          {activeTab === "institutional" && (
            <div className="space-y-8">
              <section aria-labelledby="recommendations-heading">
                <h2 id="recommendations-heading" className="mb-4 text-xl font-bold">
                  Recommended for you
                </h2>
                {recommendations.data?.length ? (
                  <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                    {recommendations.data.map((resource) => (
                      <InstitutionalResourceCard key={resource.id} resource={resource} recommended />
                    ))}
                  </div>
                ) : (
                  <Card>
                    <p className="text-sm text-muted">
                      No personalized recommendations are available yet.
                    </p>
                  </Card>
                )}
              </section>

              <section aria-labelledby="all-resources-heading">
                <h2 id="all-resources-heading" className="mb-4 text-xl font-bold">
                  All available resources
                </h2>
                <label className="mb-4 block text-sm font-medium">
                  Find a resource
                  <input
                    className="mt-2 w-full rounded-xl border border-line bg-panel p-3"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search titles and descriptions"
                  />
                </label>
                {visibleResources.length ? (
                  <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                    {visibleResources.map((resource) => (
                      <InstitutionalResourceCard key={resource.id} resource={resource} />
                    ))}
                  </div>
                ) : (
                  <Card>
                    <p className="text-sm text-muted">
                      No resources are published for your current sections.
                    </p>
                  </Card>
                )}
              </section>

              <section aria-label="Learning activity and progress">
                <h2 className="mb-4 text-xl font-bold">Your learning activity</h2>
                <Card>
                  <p className="mb-3 text-sm text-muted">
                    Recent resource views and downloads help personalize recommendations.
                  </p>
                  {activity.isLoading ? <SectionLoader label="Loading learning activity…" /> : null}
                  {activity.error ? (
                    <InlineError
                      message="Activity history could not be loaded."
                      onRetry={() => void activity.refetch()}
                      isRetrying={activity.isFetching}
                    />
                  ) : null}
                  <ul className="space-y-2 text-sm">
                    {(activity.data ?? []).map((item) => (
                      <li key={item.id} className="flex justify-between gap-3 border-b border-line pb-2">
                        <span>
                          {item.action} ·{" "}
                          {resources.data?.find((r) => r.id === item.resource_id)?.title ?? "Resource"}
                        </span>
                        <time>{new Date(item.created_at).toLocaleString()}</time>
                      </li>
                    ))}
                  </ul>
                  <div className="mt-3 flex gap-3 items-center">
                    <Button
                      variant="secondary"
                      disabled={activityPage === 0}
                      onClick={() => setActivityPage((p) => Math.max(0, p - 1))}
                    >
                      Previous
                    </Button>
                    <span className="text-sm">Page {activityPage + 1}</span>
                    <Button
                      variant="secondary"
                      disabled={(activity.data?.length ?? 0) < 25}
                      onClick={() => setActivityPage((p) => p + 1)}
                    >
                      Next
                    </Button>
                  </div>
                </Card>
              </section>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
