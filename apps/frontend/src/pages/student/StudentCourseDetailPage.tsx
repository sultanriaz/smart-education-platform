import { useEffect, useId, useMemo, useRef, useState, type ChangeEvent } from "react";
import {
  Award,
  Bell,
  BellOff,
  BookOpen,
  CalendarClock,
  CheckSquare,
  ClipboardList,
  Download,
  FileText,
  FolderOpen,
  Info,
  MessageSquare,
  MessagesSquare,
  Send,
  Upload,
  UserCheck,
  type LucideIcon,
} from "lucide-react";
import { Link, useParams } from "react-router-dom";
import { StudentPortalHeader } from "../../components/student/StudentPortalHeader";
import { getCourseById, type EnrolledCourse } from "../../features/student/courses-data";

type CourseSectionKey =
  | "notifications"
  | "attendance"
  | "marks"
  | "gdb"
  | "assignments"
  | "mdb"
  | "lecture_hub"
  | "quizzes"
  | "resources"
  | "course_info";

interface SectionCardMeta {
  key: CourseSectionKey;
  label: string;
  icon: LucideIcon;
  toneClass: string;
}

const SECTION_CARDS: SectionCardMeta[] = [
  {
    key: "notifications",
    label: "Notifications",
    icon: Bell,
    toneClass: "bg-primary-soft text-primary-ink",
  },
  {
    key: "attendance",
    label: "Attendance",
    icon: CheckSquare,
    toneClass: "bg-success-soft text-success-ink",
  },
  {
    key: "marks",
    label: "Marks",
    icon: Award,
    toneClass: "bg-warning-soft text-warning-ink",
  },
  {
    key: "gdb",
    label: "GDB",
    icon: MessageSquare,
    toneClass: "bg-accent-soft text-accent-ink",
  },
  {
    key: "assignments",
    label: "Assignments",
    icon: FileText,
    toneClass: "bg-secondary-soft text-secondary-ink",
  },
  {
    key: "mdb",
    label: "MDB",
    icon: MessagesSquare,
    toneClass: "bg-primary-soft text-primary-ink",
  },
  {
    key: "lecture_hub",
    label: "Lecture Hub",
    icon: BookOpen,
    toneClass: "bg-secondary-soft text-secondary-ink",
  },
  {
    key: "quizzes",
    label: "Quizzes",
    icon: ClipboardList,
    toneClass: "bg-warning-soft text-warning-ink",
  },
  {
    key: "resources",
    label: "Resources",
    icon: FolderOpen,
    toneClass: "bg-accent-soft text-accent-ink",
  },
  {
    key: "course_info",
    label: "Course Info",
    icon: Info,
    toneClass: "bg-success-soft text-success-ink",
  },
];

type AttendanceTypeFilter = "All" | "Class" | "Lab";
type AttendanceStatusFilter = "All" | "PRESENT" | "ABSENT" | "LATE" | "EXCUSED";

function triggerTextDownload(filename: string, contents: string) {
  const blob = new Blob([contents], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function getAttendanceRingStats(
  records: EnrolledCourse["attendanceLedger"],
  sessionType: "Class" | "Lab"
) {
  const filtered = records.filter((item) => item.sessionType === sessionType);
  const total = filtered.length;
  const attended = filtered.filter(
    (item) => item.status === "PRESENT" || item.status === "LATE"
  ).length;
  const percentage = total > 0 ? Math.round((attended / total) * 100) : 0;
  return { total, attended, percentage };
}

function getStatusBadgeClasses(status: string): string {
  switch (status) {
    case "PRESENT":
    case "Graded":
    case "Completed":
    case "Submitted":
    case "Open":
      return "bg-success-soft text-success-ink";
    case "ABSENT":
    case "Closed":
      return "bg-danger-soft text-danger-ink";
    case "LATE":
    case "Pending":
    case "Upcoming":
      return "bg-warning-soft text-warning-ink";
    default:
      return "bg-primary-soft text-primary-ink";
  }
}

interface AttendanceRingProps {
  title: string;
  percentage: number;
  detailText: string;
  hasSessions: boolean;
  toneClass: string;
}

function AttendanceRing({
  title,
  percentage,
  detailText,
  hasSessions,
  toneClass,
}: AttendanceRingProps) {
  const radius = 34;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = hasSessions
    ? circumference - (percentage / 100) * circumference
    : circumference;

  return (
    <div className="flex items-center gap-4 rounded-2xl border border-line bg-surface p-4">
      <div className="relative h-22 w-22 shrink-0">
        <svg viewBox="0 0 88 88" className="h-full w-full -rotate-90">
          <circle
            cx="44"
            cy="44"
            r={radius}
            fill="none"
            strokeWidth="8"
            className="stroke-subtle"
          />
          <circle
            cx="44"
            cy="44"
            r={radius}
            fill="none"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className={`${toneClass} stroke-current transition-all`}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-base font-bold text-ink">
            {hasSessions ? `${percentage}%` : "N/A"}
          </span>
        </div>
      </div>

      <div className="min-w-0">
        <p className="text-sm font-bold text-ink">{title}</p>
        <p className="mt-1 text-xs font-medium text-muted">{detailText}</p>
      </div>
    </div>
  );
}

interface CourseworkCardItem {
  id: string;
  title: string;
  uploadedDate: string;
  dueDate: string;
  status: string;
  maxPoints: number;
  obtainedScore?: number;
  detailLine?: string;
}

interface CourseworkSectionProps {
  heading: string;
  emptyLabel: string;
  items: CourseworkCardItem[];
  allowUpload?: boolean;
  uploadedFiles?: Record<string, string>;
  onUploadFile?: (itemId: string, filename: string) => void;
  courseTitle: string;
}

function CourseworkSection({
  heading,
  emptyLabel,
  items,
  allowUpload = false,
  uploadedFiles = {},
  onUploadFile,
  courseTitle,
}: CourseworkSectionProps) {
  const fileInputId = useId();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const targetItemIdRef = useRef<string | null>(null);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  function handleOpenUpload(itemId: string) {
    targetItemIdRef.current = itemId;
    fileInputRef.current?.click();
  }

  function handleFilePicked(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    const activeItemId = targetItemIdRef.current;
    if (!file || !activeItemId || !onUploadFile) {
      return;
    }
    onUploadFile(activeItemId, file.name);
    setActionNotice(`Uploaded "${file.name}" successfully.`);
    targetItemIdRef.current = null;
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-base font-bold text-ink">{heading}</h3>
        <span className="rounded-full bg-subtle px-2.5 py-0.5 text-xs font-semibold text-muted">
          {items.length} total
        </span>
      </div>

      {allowUpload && (
        <input
          ref={fileInputRef}
          id={fileInputId}
          type="file"
          onChange={handleFilePicked}
          className="sr-only"
          aria-label="Select assignment file to upload"
        />
      )}

      {actionNotice && (
        <div
          role="status"
          className="rounded-xl bg-success-soft px-3.5 py-2 text-xs font-semibold text-success-ink"
        >
          {actionNotice}
        </div>
      )}

      {items.length === 0 ? (
        <div className="rounded-2xl border border-line bg-surface p-6 text-center text-sm text-muted">
          {emptyLabel}
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => {
            const uploadedName = uploadedFiles[item.id];
            const effectiveStatus = uploadedName ? "Submitted" : item.status;

            return (
              <div
                key={item.id}
                className="flex flex-col justify-between gap-3 rounded-2xl border border-line bg-surface p-4 sm:flex-row sm:items-center"
              >
                <div className="space-y-1.5">
                  <div className="flex flex-wrap items-center gap-2">
                    <h4 className="text-sm font-bold text-ink">{item.title}</h4>
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold ${getStatusBadgeClasses(
                        effectiveStatus
                      )}`}
                    >
                      {effectiveStatus}
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted">
                    <span>Uploaded: {item.uploadedDate}</span>
                    <span>Due Date: {item.dueDate}</span>
                    <span>
                      Marks:{" "}
                      {item.status === "Graded" && item.obtainedScore !== undefined
                        ? `${item.obtainedScore}/${item.maxPoints}`
                        : `${item.maxPoints} pts`}
                    </span>
                  </div>

                  {item.detailLine && (
                    <p className="text-xs text-muted">{item.detailLine}</p>
                  )}

                  {uploadedName && (
                    <p className="text-xs font-semibold text-success-ink">
                      Submitted file: {uploadedName}
                    </p>
                  )}
                </div>

                <div className="flex flex-wrap items-center gap-2 shrink-0">
                  <button
                    type="button"
                    onClick={() => {
                      const safeName = item.title.toLowerCase().replace(/[^a-z0-9]+/g, "-");
                      triggerTextDownload(
                        `${safeName}.txt`,
                        `${courseTitle}\n${item.title}\nUploaded: ${item.uploadedDate}\nDue Date: ${item.dueDate}\nMax Points: ${item.maxPoints}\n`
                      );
                      setActionNotice(`Downloaded brief for "${item.title}".`);
                    }}
                    className="inline-flex min-h-10 items-center gap-1.5 rounded-xl border border-line bg-panel px-3 py-2 text-xs font-semibold text-ink transition hover:border-primary/40 hover:text-primary-ink"
                  >
                    <Download className="h-3.5 w-3.5" aria-hidden="true" />
                    Download
                  </button>

                  {allowUpload && (
                    <button
                      type="button"
                      onClick={() => handleOpenUpload(item.id)}
                      aria-label={`${uploadedName ? "Re-upload" : "Upload"} submission for ${item.title}`}
                      className="inline-flex min-h-10 items-center gap-1.5 rounded-xl bg-primary px-3.5 py-2 text-xs font-semibold text-on-primary transition hover:bg-primary-hover"
                    >
                      <Upload className="h-3.5 w-3.5" aria-hidden="true" />
                      {uploadedName ? "Re-upload" : "Upload"}
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

interface PdfMaterialListProps {
  heading: string;
  materials: EnrolledCourse["lectureHub"]["materials"];
  recordings?: EnrolledCourse["lectureHub"]["recordings"];
  courseTitle: string;
}

function PdfMaterialList({
  heading,
  materials,
  recordings,
  courseTitle,
}: PdfMaterialListProps) {
  const [downloadMessage, setDownloadMessage] = useState<string | null>(null);

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-base font-bold text-ink">{heading}</h3>
        <span className="rounded-full bg-subtle px-2.5 py-0.5 text-xs font-semibold text-muted">
          {materials.length} files
        </span>
      </div>

      {downloadMessage && (
        <div
          role="status"
          className="rounded-xl bg-primary-soft px-3.5 py-2 text-xs font-semibold text-primary-ink"
        >
          {downloadMessage}
        </div>
      )}

      {materials.length === 0 ? (
        <div className="rounded-2xl border border-line bg-surface p-6 text-center text-sm text-muted">
          No files uploaded yet.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          {materials.map((doc) => (
            <div
              key={doc.id}
              className="flex items-center justify-between gap-3 rounded-2xl border border-line bg-surface p-4"
            >
              <div className="flex min-w-0 items-center gap-3">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-danger-soft text-danger-ink">
                  <FileText className="h-5 w-5" aria-hidden="true" />
                </div>
                <div className="min-w-0">
                  <p className="truncate text-sm font-bold text-ink">{doc.title}</p>
                  <p className="mt-0.5 text-xs text-muted">
                    {doc.format} • {doc.size} • {doc.uploadDate}
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => {
                  const safeName = doc.title.toLowerCase().replace(/[^a-z0-9]+/g, "-");
                  triggerTextDownload(
                    `${safeName}.txt`,
                    `${courseTitle}\nDocument: ${doc.title}\nCategory: ${doc.category}\nUploaded: ${doc.uploadDate}\n`
                  );
                  setDownloadMessage(`Downloaded "${doc.title}".`);
                }}
                aria-label={`Download ${doc.title}`}
                className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-line bg-panel text-ink transition hover:border-primary/40 hover:bg-primary-soft hover:text-primary-ink"
              >
                <Download className="h-4 w-4" aria-hidden="true" />
              </button>
            </div>
          ))}
        </div>
      )}

      {recordings && recordings.length > 0 && (
        <div className="space-y-2 pt-2">
          <h4 className="text-xs font-bold tracking-wider text-muted uppercase">
            Recorded Lectures
          </h4>
          <div className="space-y-2">
            {recordings.map((rec) => (
              <div
                key={rec.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-line bg-surface px-4 py-3 text-xs"
              >
                <div className="font-semibold text-ink">
                  Lecture {rec.lectureNo}: {rec.title}
                </div>
                <div className="text-muted">
                  {rec.date} • {rec.duration}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Student Course Detail screen matching the redesign spec:
 * Top student header + centered course card + compact 10-card menu strip +
 * inline detail panel rendered directly below on the same screen.
 */
export function StudentCourseDetailPage() {
  const { courseId = "" } = useParams<{ courseId: string }>();
  const course = useMemo(() => getCourseById(courseId), [courseId]);

  const [activeSection, setActiveSection] = useState<CourseSectionKey>("notifications");
  const [typeFilter, setTypeFilter] = useState<AttendanceTypeFilter>("All");
  const [statusFilter, setStatusFilter] = useState<AttendanceStatusFilter>("All");
  const [uploadedAssignments, setUploadedAssignments] = useState<Record<string, string>>({});
  const [discussionDrafts, setDiscussionDrafts] = useState<Record<string, string>>({});
  const [discussionReplies, setDiscussionReplies] = useState<
    Record<string, { id: string; author: string; text: string; time: string }[]>
  >({});

  useEffect(() => {
    setActiveSection("notifications");
    setTypeFilter("All");
    setStatusFilter("All");
  }, [course?.id]);

  if (!course) {
    return (
      <div className="mx-auto w-full max-w-5xl space-y-6 pb-8 sm:px-4 sm:pt-4">
        <StudentPortalHeader backTo="/app/student" backLabel="Back to Registered Courses" />
        <div className="mx-4 rounded-2xl border border-line bg-panel p-8 text-center sm:mx-0">
          <h2 className="text-lg font-bold text-ink">Course not found</h2>
          <p className="mt-1 text-sm text-muted">
            Please return to your registered courses list and select a valid course.
          </p>
          <Link
            to="/app/student"
            className="mt-4 inline-flex min-h-11 items-center rounded-xl bg-primary px-4 py-2 text-sm font-semibold text-on-primary"
          >
            Back to Courses
          </Link>
        </div>
      </div>
    );
  }

  const compactCode = course.code.replace(/\s+/g, "");
  const classStats = getAttendanceRingStats(course.attendanceLedger, "Class");
  const labStats = getAttendanceRingStats(course.attendanceLedger, "Lab");

  const filteredAttendance = course.attendanceLedger.filter((record) => {
    const matchesType = typeFilter === "All" || record.sessionType === typeFilter;
    const matchesStatus = statusFilter === "All" || record.status === statusFilter;
    return matchesType && matchesStatus;
  });

  const combinedMarksRows = [
    ...course.coursework.quizzes.map((q) => ({
      id: q.id,
      type: "Quiz",
      title: q.title,
      obtained: q.obtainedScore,
      total: q.maxPoints,
      status: q.status,
    })),
    ...course.coursework.assignments
      .filter((a) => a.obtainedScore !== undefined)
      .map((a) => ({
        id: a.id,
        type: "Assignment",
        title: a.title,
        obtained: a.obtainedScore ?? 0,
        total: a.maxPoints,
        status: a.status,
      })),
    ...course.coursework.exams.map((e) => ({
      id: e.id,
      type: "Exam",
      title: e.title,
      obtained: e.obtainedScore,
      total: e.maxPoints,
      status: e.status,
    })),
  ];

  function handleAddDiscussionReply(boardKey: string) {
    const trimmed = (discussionDrafts[boardKey] ?? "").trim();
    if (!trimmed) {
      return;
    }
    setDiscussionReplies((prev) => ({
      ...prev,
      [boardKey]: [
        ...(prev[boardKey] ?? []),
        {
          id: `reply-${Date.now()}`,
          author: "You (SP23-BCS-155)",
          text: trimmed,
          time: "Just now",
        },
      ],
    }));
    setDiscussionDrafts((prev) => ({ ...prev, [boardKey]: "" }));
  }

  return (
    <div className="mx-auto w-full max-w-5xl space-y-5 pb-10 sm:px-4 sm:pt-4">
      <StudentPortalHeader backTo="/app/student" backLabel="Back to Registered Courses" />

      <div className="space-y-5 px-4 sm:px-0">
        {/* Centered Course Summary Card */}
        <section
          aria-label="Course summary"
          className="rounded-2xl border border-line bg-panel p-5 text-center shadow-sm sm:p-6"
        >
          <h2 className="text-xl font-bold tracking-tight text-ink sm:text-2xl">
            {course.title}
          </h2>

          <div className="mt-2.5 flex flex-wrap items-center justify-center gap-2">
            <span className="inline-flex items-center rounded-full bg-primary-soft px-3 py-1 text-xs font-bold text-primary-ink">
              # {compactCode}
            </span>
            <span className="inline-flex items-center rounded-full bg-subtle px-3 py-1 text-xs font-semibold text-muted">
              {course.creditHours} Credit Hours
            </span>
          </div>

          <div className="mt-2.5 flex justify-center">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-line bg-surface px-3 py-1 text-xs font-semibold text-ink">
              <UserCheck className="h-3.5 w-3.5 text-primary-ink" aria-hidden="true" />
              {course.teacher.name}
            </span>
          </div>
        </section>

        {/* Compact Wrapping Grid for all 10 Course Actions */}
        <nav aria-label="Course sections">
          <div className="grid grid-cols-3 gap-2 sm:grid-cols-5 sm:gap-2.5">
            {SECTION_CARDS.map((card) => {
              const Icon = card.icon;
              const isSelected = activeSection === card.key;

              return (
                <button
                  key={card.key}
                  type="button"
                  onClick={() => setActiveSection(card.key)}
                  aria-pressed={isSelected}
                  className={`flex min-h-18 flex-col items-center justify-center gap-1.5 rounded-2xl border px-2 py-2.5 text-center transition ${
                    isSelected
                      ? "border-primary bg-primary-soft/60 shadow-sm"
                      : "border-line bg-panel hover:border-primary/40 hover:bg-surface"
                  }`}
                >
                  <span
                    className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-xl ${card.toneClass}`}
                  >
                    <Icon className="h-4 w-4" aria-hidden="true" />
                  </span>
                  <span className="text-[11px] font-bold leading-tight text-ink sm:text-xs">
                    {card.label}
                  </span>
                </button>
              );
            })}
          </div>
        </nav>

        {/* Inline Active Section Content Panel */}
        <section
          aria-live="polite"
          className="rounded-2xl border border-line bg-panel p-5 shadow-sm sm:p-6"
        >
          {activeSection === "notifications" && (
            <div className="space-y-4">
              <div className="flex items-center justify-between gap-2">
                <h3 className="text-base font-bold text-ink">Notifications</h3>
                <span className="rounded-full bg-subtle px-2.5 py-0.5 text-xs font-semibold text-muted">
                  {course.overview.announcements.length}
                </span>
              </div>

              {course.overview.announcements.length === 0 ? (
                <div className="flex flex-col items-center justify-center rounded-2xl border border-line bg-surface px-4 py-10 text-center">
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-subtle text-muted">
                    <BellOff className="h-6 w-6" aria-hidden="true" />
                  </div>
                  <p className="mt-3 text-sm font-bold text-ink">No Notifications</p>
                  <p className="mt-1 text-xs text-muted">
                    New course updates from {course.teacher.name} will appear here.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {course.overview.announcements.map((item) => (
                    <article
                      key={item.id}
                      className="rounded-2xl border border-line bg-surface p-4"
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <h4 className="text-sm font-bold text-ink">{item.title}</h4>
                        <span className="text-xs font-medium text-muted">{item.date}</span>
                      </div>
                      <p className="mt-1.5 text-xs leading-relaxed text-muted">
                        {item.content}
                      </p>
                    </article>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeSection === "attendance" && (
            <div className="space-y-5">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h3 className="text-base font-bold text-ink">Attendance</h3>
                <span className="rounded-full bg-primary-soft px-3 py-0.5 text-xs font-bold text-primary-ink">
                  Overall: {course.attendance.percentage}%
                </span>
              </div>

              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <AttendanceRing
                  title="Class Attendance"
                  percentage={classStats.percentage}
                  hasSessions={classStats.total > 0}
                  detailText={
                    classStats.total > 0
                      ? `${classStats.attended} / ${classStats.total} classes attended`
                      : "No class sessions recorded"
                  }
                  toneClass={
                    classStats.percentage >= 75 ? "text-success" : "text-danger"
                  }
                />

                <AttendanceRing
                  title="Lab Attendance"
                  percentage={labStats.percentage}
                  hasSessions={labStats.total > 0}
                  detailText={
                    labStats.total > 0
                      ? `${labStats.attended} / ${labStats.total} labs attended`
                      : "No lab sessions for this course"
                  }
                  toneClass={
                    labStats.percentage >= 75 ? "text-primary" : "text-warning"
                  }
                />
              </div>

              {/* Filter Controls */}
              <div className="flex flex-col gap-3 rounded-2xl border border-line bg-surface p-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex flex-wrap items-center gap-1.5">
                  <span className="mr-1 text-xs font-bold text-muted">Attendance Type:</span>
                  {(["All", "Class", "Lab"] as AttendanceTypeFilter[]).map((option) => (
                    <button
                      key={option}
                      type="button"
                      onClick={() => setTypeFilter(option)}
                      aria-pressed={typeFilter === option}
                      className={`min-h-9 rounded-lg px-3 py-1 text-xs font-semibold transition ${
                        typeFilter === option
                          ? "bg-primary text-on-primary"
                          : "bg-panel text-muted hover:text-ink"
                      }`}
                    >
                      {option}
                    </button>
                  ))}
                </div>

                <div className="flex flex-wrap items-center gap-1.5">
                  <span className="mr-1 text-xs font-bold text-muted">Status:</span>
                  {(
                    [
                      { value: "All", label: "All" },
                      { value: "PRESENT", label: "Present" },
                      { value: "ABSENT", label: "Absent" },
                      { value: "LATE", label: "Late" },
                      { value: "EXCUSED", label: "Excused" },
                    ] as { value: AttendanceStatusFilter; label: string }[]
                  ).map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      onClick={() => setStatusFilter(option.value)}
                      aria-pressed={statusFilter === option.value}
                      className={`min-h-9 rounded-lg px-2.5 py-1 text-xs font-semibold transition ${
                        statusFilter === option.value
                          ? "bg-primary text-on-primary"
                          : "bg-panel text-muted hover:text-ink"
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* 4-column Attendance Log Table */}
              <div className="overflow-x-auto rounded-2xl border border-line">
                <table className="w-full text-left text-[11px] sm:text-xs">
                  <thead className="bg-surface text-[10px] font-bold tracking-wider text-muted uppercase sm:text-[11px]">
                    <tr>
                      <th className="px-2.5 py-2.5 sm:px-4 sm:py-3">Type</th>
                      <th className="px-2.5 py-2.5 sm:px-4 sm:py-3">Status</th>
                      <th className="px-2.5 py-2.5 sm:px-4 sm:py-3">Start Time</th>
                      <th className="px-2.5 py-2.5 sm:px-4 sm:py-3">End Time</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-line bg-panel">
                    {filteredAttendance.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="px-4 py-8 text-center text-muted">
                          No attendance records match the selected filter.
                        </td>
                      </tr>
                    ) : (
                      filteredAttendance.map((entry) => (
                        <tr key={entry.id}>
                          <td className="px-2.5 py-2.5 sm:px-4 sm:py-3">
                            <p className="font-bold text-ink">{entry.sessionType}</p>
                            <p className="text-[10px] text-muted sm:text-[11px]">{entry.date}</p>
                          </td>
                          <td className="px-2.5 py-2.5 sm:px-4 sm:py-3">
                            <span
                              className={`inline-flex rounded-full px-2 py-0.5 text-[10px] font-bold sm:px-2.5 sm:text-[11px] ${getStatusBadgeClasses(
                                entry.status
                              )}`}
                            >
                              {entry.status}
                            </span>
                          </td>
                          <td className="whitespace-nowrap px-2.5 py-2.5 font-medium text-ink sm:px-4 sm:py-3">
                            {entry.startTime}
                          </td>
                          <td className="whitespace-nowrap px-2.5 py-2.5 font-medium text-ink sm:px-4 sm:py-3">
                            {entry.endTime}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {activeSection === "marks" && (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h3 className="text-base font-bold text-ink">Marks</h3>
                <div className="flex items-center gap-2">
                  <span className="rounded-full bg-primary-soft px-3 py-1 text-xs font-bold text-primary-ink">
                    Score: {course.standing.scorePercentage}%
                  </span>
                  <span className="rounded-full bg-success-soft px-3 py-1 text-xs font-bold text-success-ink">
                    Grade: {course.standing.estimatedGrade}
                  </span>
                </div>
              </div>

              <div className="space-y-2.5">
                {combinedMarksRows.map((row) => (
                  <div
                    key={row.id}
                    className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-line bg-surface p-4"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="rounded-md bg-subtle px-2 py-0.5 text-[11px] font-bold text-muted">
                          {row.type}
                        </span>
                        <h4 className="text-sm font-bold text-ink">{row.title}</h4>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold ${getStatusBadgeClasses(
                          row.status
                        )}`}
                      >
                        {row.status}
                      </span>
                      <span className="text-sm font-bold text-ink">
                        {row.obtained !== undefined
                          ? `${row.obtained} / ${row.total}`
                          : `Pending (${row.total})`}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeSection === "assignments" && (
            <CourseworkSection
              heading="Assignments"
              emptyLabel="No assignments posted yet."
              allowUpload
              uploadedFiles={uploadedAssignments}
              onUploadFile={(itemId, filename) =>
                setUploadedAssignments((prev) => ({ ...prev, [itemId]: filename }))
              }
              courseTitle={course.title}
              items={course.coursework.assignments.map((item) => ({
                id: item.id,
                title: item.title,
                uploadedDate: item.uploadedDate,
                dueDate: item.dueDate,
                status: item.status,
                maxPoints: item.maxPoints,
                obtainedScore: item.obtainedScore,
                detailLine: `Weightage: ${item.weight}`,
              }))}
            />
          )}

          {activeSection === "quizzes" && (
            <CourseworkSection
              heading="Quizzes"
              emptyLabel="No quizzes posted yet."
              courseTitle={course.title}
              items={course.coursework.quizzes.map((item) => ({
                id: item.id,
                title: item.title,
                uploadedDate: item.uploadedDate,
                dueDate: item.dueDate,
                status: item.status,
                maxPoints: item.maxPoints,
                obtainedScore: item.obtainedScore,
                detailLine: `Topics: ${item.topics}`,
              }))}
            />
          )}

          {activeSection === "lecture_hub" && (
            <PdfMaterialList
              heading="Lecture Hub"
              materials={course.lectureHub.materials.filter(
                (m) => m.category === "Slides" || m.category === "Handout"
              )}
              recordings={course.lectureHub.recordings}
              courseTitle={course.title}
            />
          )}

          {activeSection === "resources" && (
            <PdfMaterialList
              heading="Resources"
              materials={course.lectureHub.materials}
              courseTitle={course.title}
            />
          )}

          {activeSection === "course_info" && (
            <div className="space-y-6">
              <div>
                <h3 className="text-base font-bold text-ink">Course Info</h3>
                <dl className="mt-3 divide-y divide-line rounded-2xl border border-line bg-surface">
                  {[
                    { label: "Course Name", value: course.title },
                    { label: "Course Code", value: compactCode },
                    { label: "Credit Hours", value: `${course.creditHours} Credit Hours` },
                    { label: "Section", value: course.section },
                    { label: "Teacher", value: course.teacher.name },
                    { label: "Office", value: course.teacher.office },
                    { label: "Semester", value: course.semester },
                  ].map((row) => (
                    <div
                      key={row.label}
                      className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 text-xs sm:text-sm"
                    >
                      <dt className="font-semibold text-muted">{row.label}</dt>
                      <dd className="font-bold text-ink">{row.value}</dd>
                    </div>
                  ))}
                </dl>

                <p className="mt-3 text-xs leading-relaxed text-muted sm:text-sm">
                  {course.overview.description}
                </p>
              </div>

              <div>
                <div className="flex items-center justify-between gap-2">
                  <h4 className="text-sm font-bold text-ink">Syllabus Topics</h4>
                  <span className="text-xs font-semibold text-muted">
                    {course.overview.syllabus.length} topics
                  </span>
                </div>
                <ol className="mt-3 grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                  {course.overview.syllabus.map((topic, index) => (
                    <li
                      key={topic}
                      className="flex items-center gap-3 rounded-xl border border-line bg-surface px-3.5 py-2.5 text-xs font-medium text-ink"
                    >
                      <span className="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary-soft text-xs font-bold text-primary-ink">
                        {index + 1}
                      </span>
                      <span>{topic}</span>
                    </li>
                  ))}
                </ol>
              </div>
            </div>
          )}

          {activeSection === "gdb" && (
            <div className="space-y-4">
              <h3 className="text-base font-bold text-ink">
                Graded Discussion Board (GDB)
              </h3>
              {course.coursework.gdb.map((item) => {
                const replies = discussionReplies[item.id] ?? [];
                return (
                  <div
                    key={item.id}
                    className="space-y-3 rounded-2xl border border-line bg-surface p-4"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h4 className="text-sm font-bold text-ink">{item.title}</h4>
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-[11px] font-bold ${getStatusBadgeClasses(
                          item.status
                        )}`}
                      >
                        {item.status}
                      </span>
                    </div>
                    <p className="text-xs leading-relaxed text-muted">{item.topic}</p>
                    <div className="flex items-center gap-1.5 text-xs text-muted">
                      <CalendarClock className="h-3.5 w-3.5" aria-hidden="true" />
                      Due: {item.dueDate}
                    </div>

                    {replies.length > 0 && (
                      <div className="space-y-2 border-t border-line pt-3">
                        {replies.map((reply) => (
                          <div
                            key={reply.id}
                            className="rounded-xl border border-line bg-panel px-3 py-2 text-xs"
                          >
                            <div className="flex items-center justify-between text-[11px] text-muted">
                              <strong className="text-ink">{reply.author}</strong>
                              <span>{reply.time}</span>
                            </div>
                            <p className="mt-1 text-ink">{reply.text}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    {item.status === "Open" && (
                      <div className="flex gap-2 pt-1">
                        <input
                          type="text"
                          value={discussionDrafts[item.id] ?? ""}
                          onChange={(e) =>
                            setDiscussionDrafts((prev) => ({
                              ...prev,
                              [item.id]: e.target.value,
                            }))
                          }
                          placeholder="Write your GDB response..."
                          aria-label="GDB response"
                          className="flex-1 rounded-xl border border-line bg-panel px-3 py-2 text-xs text-ink placeholder:text-muted"
                        />
                        <button
                          type="button"
                          onClick={() => handleAddDiscussionReply(item.id)}
                          className="inline-flex min-h-10 items-center gap-1.5 rounded-xl bg-primary px-3.5 py-2 text-xs font-semibold text-on-primary hover:bg-primary-hover"
                        >
                          <Send className="h-3.5 w-3.5" aria-hidden="true" />
                          Post
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          {activeSection === "mdb" && (
            <div className="space-y-4">
              <h3 className="text-base font-bold text-ink">
                Moderated Discussion Board (MDB)
              </h3>
              {course.coursework.mdb.map((item) => {
                const replies = discussionReplies[item.id] ?? [];
                return (
                  <div
                    key={item.id}
                    className="space-y-3 rounded-2xl border border-line bg-surface p-4"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h4 className="text-sm font-bold text-ink">{item.title}</h4>
                      <span className="text-xs font-semibold text-muted">
                        {item.postsCount + replies.length} posts • {item.lastUpdated}
                      </span>
                    </div>
                    <p className="text-xs leading-relaxed text-muted">{item.prompt}</p>

                    {replies.length > 0 && (
                      <div className="space-y-2 border-t border-line pt-3">
                        {replies.map((reply) => (
                          <div
                            key={reply.id}
                            className="rounded-xl border border-line bg-panel px-3 py-2 text-xs"
                          >
                            <div className="flex items-center justify-between text-[11px] text-muted">
                              <strong className="text-ink">{reply.author}</strong>
                              <span>{reply.time}</span>
                            </div>
                            <p className="mt-1 text-ink">{reply.text}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    <div className="flex gap-2 pt-1">
                      <input
                        type="text"
                        value={discussionDrafts[item.id] ?? ""}
                        onChange={(e) =>
                          setDiscussionDrafts((prev) => ({
                            ...prev,
                            [item.id]: e.target.value,
                          }))
                        }
                        placeholder="Ask a question or post on MDB..."
                        aria-label="MDB comment"
                        className="flex-1 rounded-xl border border-line bg-panel px-3 py-2 text-xs text-ink placeholder:text-muted"
                      />
                      <button
                        type="button"
                        onClick={() => handleAddDiscussionReply(item.id)}
                        className="inline-flex min-h-10 items-center gap-1.5 rounded-xl bg-primary px-3.5 py-2 text-xs font-semibold text-on-primary hover:bg-primary-hover"
                      >
                        <Send className="h-3.5 w-3.5" aria-hidden="true" />
                        Post
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
