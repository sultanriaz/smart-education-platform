import { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import {
  GraduationCap,
  ArrowLeft,
  ChevronDown,
  BookOpen,
  Calendar,
  Clock,
  MapPin,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Upload,
  Sparkles,
  Download,
  Video,
  Play,
  Pause,
  Info,
  Bell,
  Check,
  X,
  FileUp,
  Search,
  ExternalLink,
  ShieldAlert,
  HelpCircle,
  TrendingUp,
  Percent
} from "lucide-react";

import { COURSES_CATALOG, type EnrolledCourse, getCourseById } from "../../features/student/courses-data";
import { Button } from "../../components/ui/Button";

export function StudentCourseDetailPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const navigate = useNavigate();

  // Find course or default to first
  const activeCourseId = courseId || "compiler";
  const [currentCourse, setCurrentCourse] = useState<EnrolledCourse>(() => {
    return getCourseById(activeCourseId) || COURSES_CATALOG[0]!;
  });

  const [activeTab, setActiveTab] = useState<"overview" | "coursework" | "attendance" | "lectureHub">("overview");

  // Assignment Dropbox state
  const [selectedAssignmentId, setSelectedAssignmentId] = useState<string | null>(null);
  const [uploadedFileName, setUploadedFileName] = useState("");
  const [isSubmittingDropbox, setIsSubmittingDropbox] = useState(false);
  const [submissionSuccess, setSubmissionSuccess] = useState(false);

  // Leave / Excuse modal state
  const [isExcuseModalOpen, setIsExcuseModalOpen] = useState(false);
  const [excuseLectureNo, setExcuseLectureNo] = useState<number>(4);
  const [excuseReason, setExcuseReason] = useState("Medical / Illness");
  const [excuseDocName, setExcuseDocName] = useState("");
  const [excuseNotes, setExcuseNotes] = useState("");
  const [excuseSuccess, setExcuseSuccess] = useState(false);

  // Video player state
  const [selectedRecording, setSelectedRecording] = useState(currentCourse.lectureHub.recordings[0] || null);
  const [isPlaying, setIsPlaying] = useState(false);

  // Material Vault filters
  const [materialFilter, setMaterialFilter] = useState<string>("All");
  const [materialSearch, setMaterialSearch] = useState("");

  const handleCourseSwitch = (id: string) => {
    const next = getCourseById(id);
    if (next) {
      setCurrentCourse(next);
      setSelectedRecording(next.lectureHub.recordings[0] || null);
      navigate(`/app/student/courses/${next.id}`, { replace: true });
    }
  };

  // Dropbox submit handler
  const handleDropboxSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAssignmentId || !uploadedFileName) return;
    setIsSubmittingDropbox(true);

    setTimeout(() => {
      setCurrentCourse((prev) => ({
        ...prev,
        coursework: {
          ...prev.coursework,
          assignments: prev.coursework.assignments.map((a) =>
            a.id === selectedAssignmentId
              ? {
                  ...a,
                  status: "Submitted",
                  submittedFile: uploadedFileName,
                  submittedAt: "Just now"
                }
              : a
          )
        }
      }));
      setIsSubmittingDropbox(false);
      setSubmissionSuccess(true);
      setTimeout(() => {
        setSelectedAssignmentId(null);
        setSubmissionSuccess(false);
        setUploadedFileName("");
      }, 1500);
    }, 600);
  };

  // Leave excuse submit handler
  const handleExcuseSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newReq = {
      id: `lv-${Date.now()}`,
      lectureNo: excuseLectureNo,
      date: currentCourse.attendanceLedger.find((l) => l.lectureNo === excuseLectureNo)?.date || "Recent Date",
      reason: excuseReason,
      documentName: excuseDocName || "medical_attestation.pdf",
      submittedAt: "Just now",
      status: "Pending" as const,
      adminRemarks: "Awaiting teacher verification."
    };

    setCurrentCourse((prev) => ({
      ...prev,
      leaveRequests: [newReq, ...prev.leaveRequests]
    }));

    setExcuseSuccess(true);
    setTimeout(() => {
      setIsExcuseModalOpen(false);
      setExcuseSuccess(false);
      setExcuseNotes("");
      setExcuseDocName("");
    }, 1500);
  };

  // Attendance status badge coloring
  const attPct = currentCourse.attendance.percentage;
  const isGreen = attPct >= 80;
  const isAmber = attPct >= 75 && attPct < 80;
  const isRed = attPct < 75;

  const filteredMaterials = currentCourse.lectureHub.materials.filter((m) => {
    const matchesCat = materialFilter === "All" || m.category === materialFilter;
    const matchesSearch = m.title.toLowerCase().includes(materialSearch.toLowerCase());
    return matchesCat && matchesSearch;
  });

  return (
    <div className="page-container space-y-6">
      {/* ================= TOP BREADCRUMB & COURSE SWITCHER HEADER ================= */}
      <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Link
              to="/app/student"
              className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-surface px-3 py-1.5 text-xs font-semibold text-text hover:border-brand-500 transition shadow-2xs"
            >
              <ArrowLeft size={14} />
              <span>Dashboard</span>
            </Link>
            <div className="flex items-center gap-2 text-xs text-muted">
              <span>/</span>
              <span>Enrolled Courses</span>
              <span>/</span>
              <span className="font-semibold text-ink">{currentCourse.code}</span>
            </div>
          </div>

          {/* Quick Subject Switcher Dropdown */}
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-muted hidden sm:inline">Switch Course:</span>
            <select
              value={currentCourse.id}
              onChange={(e) => handleCourseSwitch(e.target.value)}
              className="rounded-xl border border-line bg-surface px-3 py-1.5 text-xs font-bold text-ink focus:outline-hidden focus:ring-2 focus:ring-brand-500 shadow-2xs"
            >
              {COURSES_CATALOG.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.code} · {c.title}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Course Banner Metadata */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pt-2 border-t border-line/60">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="font-mono text-sm font-extrabold text-brand-600 bg-brand-500/10 px-2.5 py-0.5 rounded-lg">
                {currentCourse.code}
              </span>
              <span className="text-xs font-bold text-muted bg-surface px-2.5 py-0.5 rounded-lg border border-line">
                Section: {currentCourse.section}
              </span>
              <span className="text-xs font-medium text-muted">
                {currentCourse.creditHours} Credit Hours · {currentCourse.semester}
              </span>
            </div>
            <h1 className="text-2xl font-black text-ink tracking-tight mt-1">
              {currentCourse.title}
            </h1>
            <p className="text-xs text-muted mt-0.5">
              Primary Instructor: <strong>{currentCourse.teacher.name}</strong> ({currentCourse.teacher.role}) · Office: {currentCourse.teacher.office}
            </p>
          </div>

          {/* Key Course Health Metrics */}
          <div className="flex flex-wrap items-center gap-3">
            {/* Standing Estimate */}
            <div className="rounded-xl border border-line bg-surface/50 px-3.5 py-2 text-right">
              <p className="text-[11px] font-medium text-muted uppercase tracking-wider">Current Standing</p>
              <p className="text-sm font-black font-mono text-ink">{currentCourse.standing.estimatedGrade}</p>
            </div>

            {/* Attendance Dial Badge */}
            <div
              className={`rounded-xl border px-3.5 py-2 text-right ${
                isGreen
                  ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300"
                  : isAmber
                  ? "border-amber-500/30 bg-amber-500/10 text-amber-700 dark:text-amber-300"
                  : "border-red-500/30 bg-red-500/10 text-red-700 dark:text-red-300"
              }`}
            >
              <p className="text-[11px] font-medium uppercase tracking-wider">
                {isRed ? "Regulatory Warning" : isAmber ? "Attendance Notice" : "Attendance Safe"}
              </p>
              <p className="text-sm font-black font-mono">
                {currentCourse.attendance.percentage}% ({currentCourse.attendance.attended}/{currentCourse.attendance.total})
              </p>
            </div>

            {/* AI Practice Quick Launch */}
            <Link
              to="/app/student/learning"
              className="inline-flex items-center gap-1.5 rounded-xl bg-brand-600 px-3.5 py-2.5 text-xs font-bold text-white shadow-xs hover:bg-brand-700 transition"
            >
              <Sparkles size={14} />
              <span>AI Self-Assessment</span>
            </Link>
          </div>
        </div>

        {/* Regulatory Attendance Banner (if <75%) */}
        {isRed && (
          <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-3.5 text-xs text-red-800 dark:text-red-200 flex items-center justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <ShieldAlert size={18} className="text-danger shrink-0" />
              <span>
                <strong>Examination Eligibility Alert:</strong> Your attendance ({currentCourse.attendance.percentage}%) is below the mandatory{" "}
                <strong>75% regulatory cutoff</strong>. You need to attend the next{" "}
                <strong>{currentCourse.attendance.requiredConsecutive} consecutive lectures</strong> or submit verified medical excuses to be cleared for the terminal exam.
              </span>
            </div>
            <button
              type="button"
              onClick={() => {
                setActiveTab("attendance");
                setIsExcuseModalOpen(true);
              }}
              className="shrink-0 rounded-lg bg-danger px-3 py-1 font-bold text-white text-xs hover:bg-red-700 transition"
            >
              Submit Leave Excuse
            </button>
          </div>
        )}
      </div>

      {/* ================= 4 CONSOLIDATED WORKSPACE TABS ================= */}
      <div className="flex rounded-2xl border border-line bg-panel p-1.5 text-xs sm:text-sm font-bold shadow-2xs overflow-x-auto gap-1">
        {[
          { id: "overview", label: "1. Overview & Syllabus", icon: BookOpen },
          { id: "coursework", label: "2. Coursework & Assessments", icon: FileText },
          { id: "attendance", label: "3. Attendance & Progress", icon: CheckCircle2 },
          { id: "lectureHub", label: "4. Lecture Hub & Resources", icon: Video }
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={`flex-1 min-w-[170px] inline-flex items-center justify-center gap-2 rounded-xl py-2.5 px-3 transition ${
                isActive
                  ? "bg-brand-600 text-white shadow-xs font-extrabold"
                  : "text-muted hover:text-ink hover:bg-surface"
              }`}
            >
              <Icon size={16} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* ================= TAB 1: OVERVIEW & SYLLABUS ================= */}
      {activeTab === "overview" && (
        <div className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-3">
            {/* Left: Instructor Bio Card */}
            <div className="rounded-2xl border border-line bg-panel p-6 shadow-2xs space-y-4">
              <div className="flex items-center gap-3.5">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-600 font-bold text-white shadow-xs text-base">
                  {currentCourse.teacher.avatar}
                </div>
                <div>
                  <h3 className="font-bold text-base text-ink">{currentCourse.teacher.name}</h3>
                  <p className="text-xs text-brand-600 font-medium">{currentCourse.teacher.role}</p>
                  <span className="inline-block rounded-full bg-emerald-500/10 px-2 py-0.2 text-[10px] font-semibold text-emerald-600 mt-1">
                    ● {currentCourse.teacher.status}
                  </span>
                </div>
              </div>

              <p className="text-xs text-muted leading-relaxed">{currentCourse.teacher.bio}</p>

              <div className="space-y-2 border-t border-line/60 pt-3 text-xs">
                <div className="flex items-center gap-2 text-muted">
                  <MapPin size={14} className="text-brand-600 shrink-0" />
                  <span>{currentCourse.teacher.office}</span>
                </div>
                <div className="flex items-center gap-2 text-muted">
                  <Clock size={14} className="text-brand-600 shrink-0" />
                  <span>Consultation: {currentCourse.teacher.officeHours}</span>
                </div>
                <div className="flex items-center gap-2 text-muted font-mono text-[11px]">
                  <span>{currentCourse.teacher.email}</span>
                </div>
              </div>
            </div>

            {/* Right: Course Description & Objectives */}
            <div className="lg:col-span-2 rounded-2xl border border-line bg-panel p-6 shadow-2xs space-y-4">
              <div>
                <h3 className="font-bold text-base text-ink">Course Overview & Syllabus</h3>
                <p className="text-xs text-muted mt-1 leading-relaxed">{currentCourse.overview.description}</p>
              </div>

              <div>
                <h4 className="font-bold text-xs uppercase tracking-wider text-muted mb-2">
                  Course Learning Outcomes (CLOs)
                </h4>
                <ul className="space-y-1.5 text-xs text-ink">
                  {currentCourse.overview.objectives.map((obj, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-brand-500/10 text-brand-600 font-bold text-[10px] mt-0.5">
                        {i + 1}
                      </span>
                      <span>{obj}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 pt-2 border-t border-line/60 text-xs">
                <div>
                  <h5 className="font-bold text-ink">Prerequisites</h5>
                  <p className="text-muted mt-0.5">{currentCourse.overview.prerequisites}</p>
                </div>
                <div>
                  <h5 className="font-bold text-ink">Required Textbooks</h5>
                  <p className="text-muted mt-0.5">
                    {currentCourse.overview.textbooks.map((b) => `${b.title} by ${b.author}`).join("; ")}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Grading Policy Table & Broadcast Announcements */}
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Grading Policy */}
            <div className="rounded-2xl border border-line bg-panel p-6 shadow-2xs space-y-3">
              <h3 className="font-bold text-base text-ink">Academic Grading Policy</h3>
              <p className="text-xs text-muted">HEC and CUI standardized relative grading weightage distribution.</p>

              <div className="rounded-xl border border-line overflow-hidden mt-2">
                <table className="w-full text-xs text-left">
                  <thead className="bg-surface text-muted font-bold border-b border-line">
                    <tr>
                      <th className="p-3">Evaluation Item</th>
                      <th className="p-3">Weightage</th>
                      <th className="p-3">Policy Note</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-line/60">
                    {currentCourse.overview.gradingPolicy.map((gp, i) => (
                      <tr key={i} className="hover:bg-surface/30">
                        <td className="p-3 font-semibold text-ink">{gp.item}</td>
                        <td className="p-3 font-mono font-bold text-brand-600">{gp.weight}</td>
                        <td className="p-3 text-muted">{gp.description}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Broadcast Announcements Feed */}
            <div className="rounded-2xl border border-line bg-panel p-6 shadow-2xs space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-base text-ink">Instructor Announcements Feed</h3>
                  <p className="text-xs text-muted">Official broadcasts published by {currentCourse.teacher.name}</p>
                </div>
                <Bell size={18} className="text-brand-600" />
              </div>

              <div className="space-y-3 mt-2">
                {currentCourse.overview.announcements.map((ann) => (
                  <div
                    key={ann.id}
                    className="rounded-xl border border-line bg-surface/50 p-4 space-y-1.5 hover:border-brand-500/50 transition"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-sm text-ink">{ann.title}</span>
                      {ann.isPinned && (
                        <span className="rounded-full bg-brand-500/10 px-2 py-0.5 text-[10px] font-bold text-brand-600 uppercase">
                          Pinned
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-muted leading-relaxed">{ann.content}</p>
                    <div className="flex items-center justify-between text-[11px] text-muted pt-1">
                      <span>Posted by: {ann.author}</span>
                      <span className="font-mono">{ann.date}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ================= TAB 2: COURSEWORK & ASSESSMENTS ================= */}
      {activeTab === "coursework" && (
        <div className="space-y-6">
          {/* Top Summary Banner */}
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="rounded-2xl border border-line bg-panel p-4 shadow-2xs">
              <p className="text-xs font-semibold text-muted">Assignments Total</p>
              <p className="text-xl font-bold font-mono text-ink mt-1">
                {currentCourse.coursework.assignments.filter((a) => a.status === "Graded" || a.status === "Submitted").length} /{" "}
                {currentCourse.coursework.assignments.length} Submitted
              </p>
              <p className="text-[11px] text-muted mt-0.5">Next: Assignment 2 due tomorrow.</p>
            </div>

            <div className="rounded-2xl border border-line bg-panel p-4 shadow-2xs">
              <p className="text-xs font-semibold text-muted">Quizzes Performance</p>
              <p className="text-xl font-bold font-mono text-emerald-600 mt-1">
                17.5 / 20.0 (87.5%)
              </p>
              <p className="text-[11px] text-muted mt-0.5">+1.9 marks above section mean.</p>
            </div>

            <div className="rounded-2xl border border-line bg-panel p-4 shadow-2xs">
              <p className="text-xs font-semibold text-muted">Mid-Term Result</p>
              <p className="text-xl font-bold font-mono text-brand-600 mt-1">
                21.5 / 25.0 (86.0%)
              </p>
              <p className="text-[11px] text-muted mt-0.5">Class 90th percentile.</p>
            </div>
          </div>

          {/* Assignments with Interactive Dropbox */}
          <div className="rounded-2xl border border-line bg-panel p-6 shadow-2xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-base text-ink">Course Assignments & Dropbox</h3>
                <p className="text-xs text-muted">Submit deliverables directly into the verified digital dropbox.</p>
              </div>
            </div>

            <div className="space-y-3">
              {currentCourse.coursework.assignments.map((asgn) => (
                <div
                  key={asgn.id}
                  className="rounded-2xl border border-line bg-surface/50 p-5 space-y-3 hover:border-brand-500/60 transition"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-bold text-sm text-ink">{asgn.title}</h4>
                        <span className="rounded-md bg-panel px-2 py-0.5 text-xs font-semibold text-muted border border-line">
                          Weight: {asgn.weight}
                        </span>
                      </div>
                      <p className="text-xs text-muted mt-1">Due: {asgn.dueDate}</p>
                    </div>

                    <div className="flex items-center gap-2 self-start sm:self-auto">
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-xs font-bold ${
                          asgn.status === "Graded"
                            ? "bg-emerald-500/10 text-emerald-600"
                            : asgn.status === "Submitted"
                            ? "bg-blue-500/10 text-blue-600"
                            : "bg-amber-500/10 text-amber-600"
                        }`}
                      >
                        {asgn.status}
                      </span>

                      {asgn.status === "Pending" && (
                        <button
                          type="button"
                          onClick={() => {
                            setSelectedAssignmentId(asgn.id);
                            setUploadedFileName("");
                          }}
                          className="inline-flex items-center gap-1.5 rounded-xl bg-brand-600 px-3.5 py-1.5 text-xs font-bold text-white shadow-xs hover:bg-brand-700 transition"
                        >
                          <Upload size={13} />
                          <span>Submit to Dropbox</span>
                        </button>
                      )}
                    </div>
                  </div>

                  {asgn.submittedFile && (
                    <div className="rounded-xl border border-line/70 bg-panel p-3 text-xs flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <FileText size={15} className="text-brand-600" />
                        <span className="font-mono font-medium text-ink">{asgn.submittedFile}</span>
                        <span className="text-muted">({asgn.submittedAt})</span>
                      </div>
                      {asgn.obtainedScore !== undefined && (
                        <span className="font-mono font-bold text-emerald-600">
                          Score: {asgn.obtainedScore} / {asgn.maxPoints}
                        </span>
                      )}
                    </div>
                  )}

                  {asgn.feedback && (
                    <p className="text-xs text-muted bg-surface/70 rounded-lg p-2.5 border-l-2 border-emerald-500">
                      <strong>Instructor Feedback:</strong> {asgn.feedback}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Quizzes & Marks Diff Section */}
          <div className="rounded-2xl border border-line bg-panel p-6 shadow-2xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-base text-ink">Quizzes, Exams & Score Statistics</h3>
                <p className="text-xs text-muted">Comparison against section average and topic mastery.</p>
              </div>

              <Link
                to="/app/student/learning"
                className="inline-flex items-center gap-1 text-xs font-bold text-brand-600 hover:underline"
              >
                <Sparkles size={14} />
                <span>Practice Smart Test</span>
              </Link>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {currentCourse.coursework.quizzes.map((qz) => {
                const diff = (qz.obtainedScore - qz.classAverage).toFixed(1);
                const isAbove = Number(diff) >= 0;
                return (
                  <div key={qz.id} className="rounded-xl border border-line bg-surface/50 p-4 space-y-2.5">
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-sm text-ink">{qz.title}</h4>
                      <span className="font-mono font-bold text-sm text-brand-600">
                        {qz.obtainedScore} / {qz.maxPoints}
                      </span>
                    </div>

                    <p className="text-xs text-muted">Topics: {qz.topics}</p>

                    {/* Class Comparison Bar */}
                    <div className="space-y-1 text-xs pt-1 border-t border-line/60">
                      <div className="flex justify-between text-[11px] text-muted">
                        <span>Section Mean: {qz.classAverage}</span>
                        <span className={isAbove ? "text-emerald-600 font-bold" : "text-amber-600 font-bold"}>
                          {isAbove ? `+${diff} above average` : `${diff} below average`}
                        </span>
                      </div>
                      <div className="h-1.5 w-full bg-surface rounded-full overflow-hidden">
                        <div
                          className="h-full bg-brand-600 rounded-full"
                          style={{ width: `${(qz.obtainedScore / qz.maxPoints) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* ================= TAB 3: ATTENDANCE & PROGRESS ================= */}
      {activeTab === "attendance" && (
        <div className="space-y-6">
          {/* Top Attendance KPI & Safe Margin Calculator */}
          <div className="grid gap-6 lg:grid-cols-3">
            <div className="rounded-2xl border border-line bg-panel p-6 shadow-2xs space-y-3">
              <p className="text-xs font-bold uppercase tracking-wider text-muted">Attendance Overview</p>
              <div className="flex items-baseline gap-2">
                <span className={`text-3xl font-black font-mono ${isGreen ? "text-emerald-600" : isAmber ? "text-amber-600" : "text-red-600"}`}>
                  {currentCourse.attendance.percentage}%
                </span>
                <span className="text-xs text-muted font-medium">
                  ({currentCourse.attendance.attended} of {currentCourse.attendance.total} sessions)
                </span>
              </div>

              <div className="space-y-1.5 pt-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-muted">Present:</span>
                  <span className="font-bold text-emerald-600">{currentCourse.attendance.attended}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Absent:</span>
                  <span className="font-bold text-danger">{currentCourse.attendance.absent}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Late:</span>
                  <span className="font-bold text-amber-600">{currentCourse.attendance.late}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted">Excused / Approved Leave:</span>
                  <span className="font-bold text-blue-600">{currentCourse.attendance.excused}</span>
                </div>
              </div>
            </div>

            {/* Regulatory Margin Notice */}
            <div className="lg:col-span-2 rounded-2xl border border-line bg-panel p-6 shadow-2xs flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <AlertTriangle size={18} className={isRed ? "text-danger" : "text-amber-600"} />
                  <h3 className="font-bold text-base text-ink">Regulatory Examination Threshold</h3>
                </div>
                <p className="text-xs text-muted mt-2 leading-relaxed">
                  Higher Education Commission (HEC) and university regulations mandate a minimum of{" "}
                  <strong>75% attendance</strong> to be admitted into the final terminal examination.
                </p>

                <div className="mt-4 rounded-xl border border-line bg-surface/60 p-4 space-y-1.5 text-xs">
                  <strong className="text-ink">Attendance Forecast Calculator:</strong>
                  {isRed ? (
                    <p className="text-red-700 dark:text-red-300">
                      ⚠️ You must attend the next <strong>{currentCourse.attendance.requiredConsecutive} consecutive lectures</strong> without absence to cross 75.0%.
                    </p>
                  ) : (
                    <p className="text-emerald-700 dark:text-emerald-300">
                      ✓ Your attendance meets all compliance policies. You can safely miss up to 2 future lectures while remaining above 75%.
                    </p>
                  )}
                </div>
              </div>

              <div className="pt-4 mt-4 border-t border-line/60 flex items-center justify-between">
                <span className="text-xs text-muted">Missed a class due to illness or official duty?</span>
                <button
                  type="button"
                  onClick={() => setIsExcuseModalOpen(true)}
                  className="rounded-xl bg-brand-600 px-4 py-2 text-xs font-bold text-white shadow-xs hover:bg-brand-700 transition"
                >
                  Submit Leave Excuse Request
                </button>
              </div>
            </div>
          </div>

          {/* Absence / Leave Request Status Tracker */}
          {currentCourse.leaveRequests.length > 0 && (
            <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs space-y-3">
              <h4 className="font-bold text-sm text-ink">My Submitted Leave & Medical Excuses</h4>
              <div className="space-y-2">
                {currentCourse.leaveRequests.map((lv) => (
                  <div
                    key={lv.id}
                    className="rounded-xl border border-line bg-surface/50 p-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
                  >
                    <div>
                      <p className="font-bold text-ink">
                        Lecture {lv.lectureNo} ({lv.date}) · {lv.reason}
                      </p>
                      <p className="text-muted mt-0.5">
                        Document: <span className="font-mono text-brand-600">{lv.documentName}</span> · Submitted: {lv.submittedAt}
                      </p>
                      {lv.adminRemarks && (
                        <p className="text-[11px] text-muted italic mt-0.5">Note: {lv.adminRemarks}</p>
                      )}
                    </div>
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-xs font-bold self-start sm:self-auto ${
                        lv.status === "Approved"
                          ? "bg-emerald-500/10 text-emerald-600"
                          : lv.status === "Pending"
                          ? "bg-amber-500/10 text-amber-600"
                          : "bg-red-500/10 text-danger"
                      }`}
                    >
                      {lv.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Class-by-Class Attendance Ledger Table */}
          <div className="rounded-2xl border border-line bg-panel p-6 shadow-2xs space-y-4">
            <h3 className="font-bold text-base text-ink">Class-by-Class Attendance Ledger</h3>

            <div className="rounded-xl border border-line overflow-hidden">
              <table className="w-full text-xs text-left">
                <thead className="bg-surface text-muted font-bold border-b border-line">
                  <tr>
                    <th className="p-3">Lec #</th>
                    <th className="p-3">Date & Slot</th>
                    <th className="p-3">Room</th>
                    <th className="p-3">Topic Covered</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Actions / Notes</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line/60">
                  {currentCourse.attendanceLedger.map((row) => (
                    <tr key={row.id} className="hover:bg-surface/30">
                      <td className="p-3 font-mono font-bold text-brand-600">{row.lectureNo}</td>
                      <td className="p-3">
                        <div className="font-semibold text-ink">{row.date}</div>
                        <div className="text-[11px] text-muted">{row.slot}</div>
                      </td>
                      <td className="p-3 font-mono text-muted">{row.room}</td>
                      <td className="p-3 text-ink max-w-xs">{row.topic}</td>
                      <td className="p-3">
                        <span
                          className={`rounded-md px-2 py-0.5 text-[11px] font-bold ${
                            row.status === "PRESENT"
                              ? "bg-emerald-500/10 text-emerald-600"
                              : row.status === "ABSENT"
                              ? "bg-red-500/10 text-danger"
                              : row.status === "LATE"
                              ? "bg-amber-500/10 text-amber-600"
                              : "bg-blue-500/10 text-blue-600"
                          }`}
                        >
                          {row.status}
                        </span>
                      </td>
                      <td className="p-3 text-muted">
                        {row.status === "ABSENT" ? (
                          <button
                            type="button"
                            onClick={() => {
                              setExcuseLectureNo(row.lectureNo);
                              setIsExcuseModalOpen(true);
                            }}
                            className="text-xs font-bold text-brand-600 hover:underline"
                          >
                            Submit Excuse
                          </button>
                        ) : (
                          <span>{row.notes || "—"}</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ================= TAB 4: LECTURE HUB & RESOURCES ================= */}
      {activeTab === "lectureHub" && (
        <div className="space-y-6">
          {/* Synchronized Video Lecture Player & Archives */}
          <div className="rounded-2xl border border-line bg-panel p-6 shadow-2xs space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-bold text-base text-ink">Recorded Lecture Hub & Archives</h3>
                <p className="text-xs text-muted">Watch lecture recordings and jump directly to key technical timestamps.</p>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
              {/* Video Player Preview Area */}
              <div className="lg:col-span-2 rounded-2xl border border-line bg-black/90 p-4 text-white flex flex-col justify-between aspect-video relative overflow-hidden group">
                <div className="flex items-center justify-between z-10 text-xs">
                  <span className="rounded-md bg-white/20 backdrop-blur-md px-2 py-1 font-bold">
                    Lecture {selectedRecording?.lectureNo || 1}
                  </span>
                  <span className="font-mono text-white/80">{selectedRecording?.duration || "45:00"}</span>
                </div>

                {/* Center Play Button Simulator */}
                <div className="flex flex-col items-center justify-center z-10 my-auto text-center">
                  <button
                    type="button"
                    onClick={() => setIsPlaying(!isPlaying)}
                    aria-label={isPlaying ? "Pause lecture" : "Play lecture"}
                    className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-600 text-white shadow-lg hover:scale-110 transition"
                  >
                    {isPlaying ? <Pause size={28} /> : <Play size={28} className="ml-1" />}
                  </button>
                  <p className="mt-3 text-sm font-bold text-white max-w-md">
                    {selectedRecording?.title || "Lecture Recording"}
                  </p>
                  <p className="text-xs text-white/70 mt-1">
                    {isPlaying ? "Simulating high-definition video playback…" : "Click to stream lecture archive"}
                  </p>
                </div>

                {/* Timestamps Navigation Pill Bar */}
                <div className="z-10 bg-black/60 backdrop-blur-md rounded-xl p-2.5 space-y-1 text-xs">
                  <p className="text-[11px] font-bold text-brand-300 uppercase tracking-wider">Concept Timestamps:</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedRecording?.timestamps.map((ts, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => setIsPlaying(true)}
                        className="rounded-lg bg-white/10 hover:bg-white/20 px-2 py-1 font-mono text-[11px] text-white flex items-center gap-1 transition"
                      >
                        <Clock size={11} className="text-brand-300" />
                        <span>{ts.time} - {ts.label}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Lecture Playlist Column */}
              <div className="space-y-3">
                <h4 className="font-bold text-xs uppercase tracking-wider text-muted">Available Recordings</h4>
                <div className="space-y-2">
                  {currentCourse.lectureHub.recordings.map((rec) => {
                    const isSelected = selectedRecording?.id === rec.id;
                    return (
                      <div
                        key={rec.id}
                        onClick={() => {
                          setSelectedRecording(rec);
                          setIsPlaying(false);
                        }}
                        className={`cursor-pointer rounded-xl border p-3.5 space-y-1 transition ${
                          isSelected
                            ? "border-brand-500 bg-brand-500/10 shadow-xs"
                            : "border-line bg-surface/50 hover:border-brand-500/50"
                        }`}
                      >
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-bold text-ink">Lecture {rec.lectureNo}</span>
                          <span className="font-mono text-muted">{rec.duration}</span>
                        </div>
                        <p className="text-xs text-muted line-clamp-2">{rec.title}</p>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Material Vault */}
          <div className="rounded-2xl border border-line bg-panel p-6 shadow-2xs space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <h3 className="font-bold text-base text-ink">Course Material Vault</h3>
                <p className="text-xs text-muted">Download official slides, textbooks, lab code templates, and handouts.</p>
              </div>

              {/* Material Filter Buttons */}
              <div className="flex flex-wrap gap-1.5 text-xs">
                {["All", "Slides", "Textbook", "Handout", "Code"].map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setMaterialFilter(cat)}
                    className={`rounded-lg px-2.5 py-1 font-semibold transition ${
                      materialFilter === cat
                        ? "bg-brand-600 text-white shadow-2xs"
                        : "bg-surface text-muted hover:text-ink border border-line"
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            {/* Search Material */}
            <div className="rounded-xl border border-line bg-surface p-2.5 flex items-center gap-2">
              <Search size={16} className="text-muted" />
              <input
                type="text"
                placeholder="Search handouts, slides, and textbooks by keyword..."
                value={materialSearch}
                onChange={(e) => setMaterialSearch(e.target.value)}
                className="w-full bg-transparent text-xs text-ink placeholder:text-muted focus:outline-hidden"
              />
            </div>

            {/* Material List */}
            <div className="space-y-2.5">
              {filteredMaterials.map((mat) => (
                <div
                  key={mat.id}
                  className="rounded-xl border border-line bg-surface/40 p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-brand-500/50 transition"
                >
                  <div className="flex items-center gap-3">
                    <span className="rounded-lg bg-brand-500/10 px-2.5 py-1 font-mono text-xs font-bold text-brand-600">
                      {mat.format}
                    </span>
                    <div>
                      <p className="font-bold text-xs sm:text-sm text-ink">{mat.title}</p>
                      <p className="text-[11px] text-muted mt-0.5">
                        Category: {mat.category} · Size: {mat.size} · Uploaded: {mat.uploadDate} · {mat.downloadsCount} downloads
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-start sm:self-auto">
                    <button
                      type="button"
                      onClick={() => alert(`Downloading ${mat.title} (${mat.size})...`)}
                      className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-panel px-3.5 py-1.5 text-xs font-semibold text-brand-600 hover:border-brand-500 transition shadow-2xs"
                    >
                      <Download size={13} />
                      <span>Download</span>
                    </button>

                    <Link
                      to="/app/student/learning"
                      className="inline-flex items-center gap-1 rounded-xl bg-surface px-2.5 py-1.5 text-xs font-medium text-muted hover:text-brand-600 transition"
                    >
                      <Sparkles size={12} />
                      <span>AI Notes</span>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ================= MODAL 1: DROPBOX SUBMISSION UPLOADER ================= */}
      {selectedAssignmentId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs">
          <div className="w-full max-w-lg rounded-3xl border border-line bg-panel p-6 shadow-2xl space-y-4 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-line pb-3">
              <div>
                <h3 className="font-bold text-base text-ink">Assignment Dropbox Submission</h3>
                <p className="text-xs text-muted">
                  {currentCourse.coursework.assignments.find((a) => a.id === selectedAssignmentId)?.title}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedAssignmentId(null)}
                className="text-muted hover:text-ink"
              >
                <X size={18} />
              </button>
            </div>

            {submissionSuccess ? (
              <div className="rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-5 text-center text-emerald-700 dark:text-emerald-300 space-y-2">
                <CheckCircle2 size={32} className="mx-auto text-emerald-600" />
                <p className="font-bold text-sm">Assignment Submitted Successfully!</p>
                <p className="text-xs">Your deliverable has been recorded in the academic vault.</p>
              </div>
            ) : (
              <form onSubmit={handleDropboxSubmit} className="space-y-4">
                <div className="rounded-2xl border-2 border-dashed border-line bg-surface/50 p-6 text-center space-y-2">
                  <Upload size={32} className="mx-auto text-brand-600" />
                  <p className="text-xs font-bold text-ink">Upload your solution or code archive</p>
                  <p className="text-[11px] text-muted">Supported: .cpp, .c, .py, .pdf, .zip up to 50 MB</p>
                  <input
                    type="file"
                    id="dropbox-file"
                    className="hidden"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        setUploadedFileName(e.target.files[0].name);
                      }
                    }}
                  />
                  <label
                    htmlFor="dropbox-file"
                    className="inline-block cursor-pointer rounded-xl bg-panel px-4 py-2 text-xs font-bold text-brand-600 border border-line hover:border-brand-500 transition shadow-2xs mt-2"
                  >
                    Select Local File
                  </label>
                  {uploadedFileName && (
                    <p className="mt-2 text-xs font-mono font-bold text-emerald-600">
                      Selected: {uploadedFileName}
                    </p>
                  )}
                </div>

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setSelectedAssignmentId(null)}
                    className="rounded-xl px-4 py-2 text-xs font-semibold text-muted hover:text-ink"
                  >
                    Cancel
                  </button>
                  <Button type="submit" disabled={!uploadedFileName || isSubmittingDropbox}>
                    {isSubmittingDropbox ? "Submitting…" : "Upload to Dropbox"}
                  </Button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* ================= MODAL 2: MEDICAL / LEAVE EXCUSE REQUEST ================= */}
      {isExcuseModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs">
          <div className="w-full max-w-lg rounded-3xl border border-line bg-panel p-6 shadow-2xl space-y-4 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-line pb-3">
              <div>
                <h3 className="font-bold text-base text-ink">Submit Medical / Absence Excuse</h3>
                <p className="text-xs text-muted">
                  Formal leave petition for {currentCourse.title} ({currentCourse.code})
                </p>
              </div>
              <button
                type="button"
                onClick={() => setIsExcuseModalOpen(false)}
                className="text-muted hover:text-ink"
              >
                <X size={18} />
              </button>
            </div>

            {excuseSuccess ? (
              <div className="rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-5 text-center text-emerald-700 dark:text-emerald-300 space-y-2">
                <CheckCircle2 size={32} className="mx-auto text-emerald-600" />
                <p className="font-bold text-sm">Leave Excuse Submitted!</p>
                <p className="text-xs">
                  Your request has been forwarded to {currentCourse.teacher.name} and the Academic Office for clearance.
                </p>
              </div>
            ) : (
              <form onSubmit={handleExcuseSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-ink mb-1">Select Absent Session</label>
                  <select
                    value={excuseLectureNo}
                    onChange={(e) => setExcuseLectureNo(Number(e.target.value))}
                    className="w-full rounded-xl border border-line bg-surface px-3 py-2 text-xs text-ink focus:outline-hidden"
                  >
                    {currentCourse.attendanceLedger
                      .filter((l) => l.status === "ABSENT")
                      .map((l) => (
                        <option key={l.lectureNo} value={l.lectureNo}>
                          Lecture {l.lectureNo}: {l.date} ({l.topic})
                        </option>
                      ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-ink mb-1">Reason for Absence</label>
                  <select
                    value={excuseReason}
                    onChange={(e) => setExcuseReason(e.target.value)}
                    className="w-full rounded-xl border border-line bg-surface px-3 py-2 text-xs text-ink focus:outline-hidden"
                  >
                    <option value="Medical / Illness">Medical / Severe Illness</option>
                    <option value="Official University Representation">Official University Event / Sports Gala</option>
                    <option value="Family Emergency">Family Emergency / Urgent Affair</option>
                    <option value="Bereavement">Bereavement</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-ink mb-1">Attach Supporting Medical Document / Attestation</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="file"
                      id="excuse-file"
                      className="hidden"
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          setExcuseDocName(e.target.files[0].name);
                        }
                      }}
                    />
                    <label
                      htmlFor="excuse-file"
                      className="cursor-pointer rounded-xl border border-line bg-surface px-3 py-2 text-xs font-semibold text-brand-600 hover:border-brand-500 transition"
                    >
                      Browse Document (.pdf/.jpg)
                    </label>
                    <span className="text-xs font-mono text-muted">{excuseDocName || "No file selected"}</span>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-ink mb-1">Student Remarks / Explanation</label>
                  <textarea
                    rows={3}
                    placeholder="Provide additional details for the course instructor..."
                    value={excuseNotes}
                    onChange={(e) => setExcuseNotes(e.target.value)}
                    className="w-full rounded-xl border border-line bg-surface p-2.5 text-xs text-ink focus:outline-hidden"
                  />
                </div>

                <div className="flex justify-end gap-2 pt-2 border-t border-line/60">
                  <button
                    type="button"
                    onClick={() => setIsExcuseModalOpen(false)}
                    className="rounded-xl px-4 py-2 text-xs font-semibold text-muted hover:text-ink"
                  >
                    Cancel
                  </button>
                  <Button type="submit">Submit for Approval</Button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
