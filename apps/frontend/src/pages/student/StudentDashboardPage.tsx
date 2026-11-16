import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  GraduationCap,
  Sparkles,
  BookOpen,
  CreditCard,
  Calendar,
  ClipboardCheck,
  ArrowUpRight,
  AlertTriangle,
  Clock,
  MapPin,
  CheckCircle2,
  FileText,
  Bell,
  Video,
  Info,
  ChevronRight,
  X,
  Compass,
  Bus,
  Search
} from "lucide-react";

import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { DashboardWelcome } from "../../components/ui/DashboardWelcome";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { StatCard } from "../../components/ui/StatCard";
import { AttendanceChart } from "../../components/ui/AttendanceChart";
import {
  useAssessmentAssignments,
  useAttendanceSummary,
  useAttendanceRecords,
  useTimetable,
  useUnreadCount
} from "../../features/student/hooks";

interface EnrolledCourse {
  id: string;
  code: string;
  title: string;
  creditHours: number;
  teacherName: string;
  teacherOffice: string;
  attendancePercentage: number;
  attendedLectures: number;
  totalLectures: number;
  room: string;
  slot: string;
  nextLectureTime: string;
  assignments: { id: string; title: string; due: string; status: "Pending" | "Submitted" }[];
  quizzes: { id: string; title: string; score: string; maxScore: string }[];
  marks: { component: string; weight: string; obtained: string; max: string }[];
  notifications: { id: string; date: string; message: string }[];
  resources: { id: string; title: string; type: string; size: string }[];
  lectureHub: { lectureNo: number; topic: string; date: string; hasRecording: boolean }[];
  courseInfo: {
    description: string;
    prerequisites: string;
    textbook: string;
    gradingPolicy: string;
  };
}

const ENROLLED_COURSES: EnrolledCourse[] = [
  {
    id: "compiler",
    code: "CSC-354",
    title: "Compiler Construction",
    creditHours: 3,
    teacherName: "Dr. Munir Ahmad",
    teacherOffice: "A Block, 3rd Floor, Room A-301",
    attendancePercentage: 68.5,
    attendedLectures: 14,
    totalLectures: 20,
    room: "Room C-204 (C Block 2nd Floor)",
    slot: "Slot 2 (10:15 AM – 11:45 AM)",
    nextLectureTime: "Wednesday · 10:15 AM",
    assignments: [
      { id: "a1", title: "Assignment 1: Lexical Analyzer with Flex", due: "Submitted", status: "Submitted" },
      { id: "a2", title: "Assignment 2: LL(1) Parsing Table Generation", due: "Tomorrow, 11:59 PM", status: "Pending" }
    ],
    quizzes: [
      { id: "q1", title: "Quiz 1: Regular Expressions & DFA", score: "8.5", maxScore: "10" },
      { id: "q2", title: "Quiz 2: Context Free Grammars", score: "6.0", maxScore: "10" }
    ],
    marks: [
      { component: "Quizzes (Best 3 of 4)", weight: "15%", obtained: "14.5", max: "15" },
      { component: "Assignments (4 Total)", weight: "10%", obtained: "9.0", max: "10" },
      { component: "Mid-Term Examination", weight: "25%", obtained: "21.5", max: "25" },
      { component: "Terminal Examination", weight: "50%", obtained: "—", max: "50" }
    ],
    notifications: [
      { id: "n1", date: "Yesterday", message: "Assignment 2 deadline extended to tomorrow midnight." },
      { id: "n2", date: "3 days ago", message: "Please bring your laptop with Bison/Yacc installed for the next lab session." }
    ],
    resources: [
      { id: "r1", title: "Dragon Book: Compilers Principles & Techniques.pdf", type: "PDF", size: "14.2 MB" },
      { id: "r2", title: "Chapter 3: Syntax Analysis Lecture Slides.pptx", type: "PPTX", size: "4.8 MB" },
      { id: "r3", title: "Bison and Flex Code Samples.zip", type: "ZIP", size: "1.2 MB" }
    ],
    lectureHub: [
      { lectureNo: 1, topic: "Introduction to Compiler Phases & Lexical Structure", date: "Oct 12", hasRecording: true },
      { lectureNo: 2, topic: "Finite Automata (NFA to DFA Conversion)", date: "Oct 19", hasRecording: true },
      { lectureNo: 3, topic: "Context Free Grammars & Ambiguity Removal", date: "Oct 26", hasRecording: false },
      { lectureNo: 4, topic: "Top-Down Parsing & First/Follow Computation", date: "Nov 02", hasRecording: true }
    ],
    courseInfo: {
      description: "Comprehensive study of compiler engineering including scanners, top-down and bottom-up parsers, semantic evaluation, intermediate code generation, and optimization techniques.",
      prerequisites: "Theory of Automata (CSC-312), Data Structures (CSC-211)",
      textbook: "Compilers: Principles, Techniques, and Tools by Aho, Lam, Sethi, and Ullman (Dragon Book)",
      gradingPolicy: "Minimum 75% attendance mandatory. Sessional 25%, Midterm 25%, Terminal 50%."
    }
  },
  {
    id: "os",
    code: "CSC-322",
    title: "Operating Systems",
    creditHours: 4,
    teacherName: "Dr. Muhammad Asim",
    teacherOffice: "C Block, 2nd Floor, Room C-203",
    attendancePercentage: 88.0,
    attendedLectures: 22,
    totalLectures: 25,
    room: "Room C-101 (C Block 1st Floor)",
    slot: "Slot 1 (08:30 AM – 10:00 AM)",
    nextLectureTime: "Thursday · 08:30 AM",
    assignments: [
      { id: "a1", title: "Lab 3: POSIX Multi-threaded Matrix Multiplication", due: "Submitted", status: "Submitted" },
      { id: "a2", title: "Assignment 2: Banker's Algorithm Implementation", due: "In 4 days", status: "Pending" }
    ],
    quizzes: [
      { id: "q1", title: "Quiz 1: Process Scheduling Algorithms", score: "9.0", maxScore: "10" }
    ],
    marks: [
      { component: "Quizzes", weight: "15%", obtained: "13.5", max: "15" },
      { component: "Assignments & Labs", weight: "10%", obtained: "9.5", max: "10" },
      { component: "Mid-Term", weight: "25%", obtained: "23.0", max: "25" },
      { component: "Terminal", weight: "50%", obtained: "—", max: "50" }
    ],
    notifications: [
      { id: "n1", date: "2 days ago", message: "Linux Kernel compilation lab will take place in C-01 Software Lab." }
    ],
    resources: [
      { id: "r1", title: "Silberschatz Operating System Concepts (10th Ed).pdf", type: "PDF", size: "18.5 MB" },
      { id: "r2", title: "Processes and Threads Architecture Slides.pdf", type: "PDF", size: "3.2 MB" }
    ],
    lectureHub: [
      { lectureNo: 1, topic: "OS Structures & System Calls", date: "Oct 10", hasRecording: true },
      { lectureNo: 2, topic: "Process Management & CPU Scheduling", date: "Oct 17", hasRecording: true },
      { lectureNo: 3, topic: "Synchronization & Deadlock Avoidance", date: "Oct 24", hasRecording: true }
    ],
    courseInfo: {
      description: "Principles of modern operating systems, process coordination, virtual memory management, filesystem internals, and concurrency control using UNIX/Linux systems programming.",
      prerequisites: "Computer Organization & Assembly Language (CSC-221)",
      textbook: "Operating System Concepts by Silberschatz, Galvin, and Gagne",
      gradingPolicy: "Theory 75%, Lab 25%. Sessional + Midterm + Final as per university policy."
    }
  },
  {
    id: "db",
    code: "CSC-331",
    title: "Database Systems",
    creditHours: 4,
    teacherName: "Engr. Tariq Mehmood",
    teacherOffice: "A Block, 1st Floor, Room A-103",
    attendancePercentage: 94.2,
    attendedLectures: 26,
    totalLectures: 28,
    room: "Room A-201 (A Block 2nd Floor)",
    slot: "Slot 3 (12:00 PM – 01:30 PM)",
    nextLectureTime: "Wednesday · 12:00 PM",
    assignments: [
      { id: "a1", title: "SQL Complex Joins & Subqueries Project", due: "Submitted", status: "Submitted" }
    ],
    quizzes: [
      { id: "q1", title: "Quiz 1: ER-Diagrams & Normalization (3NF/BCNF)", score: "10.0", maxScore: "10" }
    ],
    marks: [
      { component: "Quizzes", weight: "15%", obtained: "15.0", max: "15" },
      { component: "Lab Tasks & Queries", weight: "10%", obtained: "9.8", max: "10" },
      { component: "Mid-Term", weight: "25%", obtained: "24.0", max: "25" },
      { component: "Terminal", weight: "50%", obtained: "—", max: "50" }
    ],
    notifications: [
      { id: "n1", date: "May 10", message: "Midterm scripts will be shown on Thursday in A-103." }
    ],
    resources: [
      { id: "r1", title: "Database Systems Concepts 7th Edition.pdf", type: "PDF", size: "22.1 MB" },
      { id: "r2", title: "PostgreSQL Advanced Indexing Guide.pdf", type: "PDF", size: "2.4 MB" }
    ],
    lectureHub: [
      { lectureNo: 1, topic: "Relational Algebra & Tuple Calculus", date: "Oct 11", hasRecording: true },
      { lectureNo: 2, topic: "Schema Normalization (1NF through BCNF)", date: "Oct 18", hasRecording: true },
      { lectureNo: 3, topic: "Transaction Isolation & ACID Properties", date: "Oct 25", hasRecording: true }
    ],
    courseInfo: {
      description: "Data models, relational algebra, SQL optimization, functional dependencies, indexing, transaction management, and noSQL paradigms.",
      prerequisites: "Discrete Structures (CSC-102), Data Structures (CSC-211)",
      textbook: "Fundamentals of Database Systems by Elmasri and Navathe",
      gradingPolicy: "Lab 25%, Theory 75%. Strictly 75% attendance enforced."
    }
  },
  {
    id: "se",
    code: "CSC-371",
    title: "Software Engineering",
    creditHours: 3,
    teacherName: "Dr. Majid Hussain",
    teacherOffice: "A Block, 3rd Floor, Room A-302",
    attendancePercentage: 82.5,
    attendedLectures: 17,
    totalLectures: 21,
    room: "Room C-102 (C Block 1st Floor)",
    slot: "Slot 4 (02:00 PM – 03:30 PM)",
    nextLectureTime: "Friday · 02:00 PM",
    assignments: [
      { id: "a1", title: "SRS Document for Healthcare Management System", due: "Submitted", status: "Submitted" }
    ],
    quizzes: [
      { id: "q1", title: "Quiz 1: Agile Methodologies & Scrum", score: "8.0", maxScore: "10" }
    ],
    marks: [
      { component: "Quizzes", weight: "15%", obtained: "12.0", max: "15" },
      { component: "Term Project", weight: "15%", obtained: "14.0", max: "15" },
      { component: "Mid-Term", weight: "20%", obtained: "18.5", max: "20" },
      { component: "Terminal", weight: "50%", obtained: "—", max: "50" }
    ],
    notifications: [
      { id: "n1", date: "May 08", message: "Term project sprint 2 evaluation begins next week." }
    ],
    resources: [
      { id: "r1", title: "Pressman Software Engineering A Practitioner's Approach.pdf", type: "PDF", size: "16.4 MB" }
    ],
    lectureHub: [
      { lectureNo: 1, topic: "Requirements Engineering & IEEE SRS Structure", date: "Oct 13", hasRecording: true },
      { lectureNo: 2, topic: "UML Architecture & Design Patterns", date: "Oct 20", hasRecording: true }
    ],
    courseInfo: {
      description: "Software lifecycle models, agile principles, architectural design, testing methodologies, DevOps pipelines, and project estimation metrics.",
      prerequisites: "Object Oriented Programming (CSC-241)",
      textbook: "Software Engineering by Ian Sommerville",
      gradingPolicy: "Sessional 25%, Midterm 25%, Terminal 50%."
    }
  }
];

export function StudentDashboardPage() {
  const attendance = useAttendanceSummary();
  const records = useAttendanceRecords();
  const timetable = useTimetable();
  const assignments = useAssessmentAssignments();
  const unread = useUnreadCount();

  const [selectedCourse, setSelectedCourse] = useState<EnrolledCourse | null>(null);
  const [activeModalTab, setActiveModalTab] = useState<
    "assignments" | "quizzes" | "attendance" | "marks" | "notifications" | "resources" | "lectureHub" | "courseInfo"
  >("assignments");

  // Timer countdown computation for next upcoming class
  const [countdownMinutes, setCountdownMinutes] = useState(28);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdownMinutes((prev) => (prev > 1 ? prev - 1 : 45));
    }, 60000);
    return () => clearInterval(timer);
  }, []);

  const criticalError =
    attendance.error ?? timetable.error ?? assignments.error ?? unread.error;

  if (
    attendance.isLoading &&
    timetable.isLoading &&
    assignments.isLoading &&
    unread.isLoading
  ) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading student dashboard…" />
      </div>
    );
  }

  // Identify if any course is below 75%
  const lowAttendanceCourse = ENROLLED_COURSES.find((c) => c.attendancePercentage < 75);

  return (
    <div className="page-container space-y-6">
      <DashboardWelcome
        subtitle="Your personalized student workspace. Live attendance tracking, course cards, lecture hub, and timetable."
        action="Open Timetable"
        to="/app/student/timetable"
      />

      {criticalError ? (
        <div className="mb-2">
          <InlineError message="Some live data could not be synchronized. You can still access individual courses and modules." />
        </div>
      ) : null}

      {/* ================= 1. REGULATORY ATTENDANCE ALERT BAR ================= */}
      {lowAttendanceCourse && (
        <div className="rounded-2xl border border-amber-500/40 bg-amber-500/10 p-4 sm:p-5 text-amber-900 dark:text-amber-200 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-start gap-3">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-amber-500 text-white shadow-xs">
              <AlertTriangle size={20} />
            </span>
            <div>
              <div className="flex items-center gap-2">
                <strong className="text-sm font-bold">Attendance Regulatory Compliance Alert</strong>
                <span className="rounded-full bg-amber-600 px-2 py-0.2 text-[10px] font-bold uppercase text-white">
                  Action Required
                </span>
              </div>
              <p className="mt-1 text-xs leading-relaxed text-amber-800 dark:text-amber-300">
                Your attendance in <strong>{lowAttendanceCourse.title} ({lowAttendanceCourse.code})</strong> is currently{" "}
                <span className="font-bold underline">{lowAttendanceCourse.attendancePercentage}%</span>, which is below the mandatory{" "}
                <strong>75% HEC / University regulatory examination cutoff</strong>. You must attend the next upcoming lectures to restore eligibility for the final examination.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() => {
              setSelectedCourse(lowAttendanceCourse);
              setActiveModalTab("attendance");
            }}
            className="shrink-0 rounded-xl bg-amber-600 px-3.5 py-1.5 text-xs font-semibold text-white shadow-xs hover:bg-amber-700 transition"
          >
            Review Attendance Log
          </button>
        </div>
      )}

      {/* ================= 2. UPCOMING CLASS COUNTDOWN BANNER ================= */}
      <div className="rounded-2xl border border-brand-500/30 bg-gradient-to-r from-brand-600/10 via-brand-500/5 to-transparent p-5 shadow-2xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-start gap-3.5">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-brand-600 text-white shadow-xs">
            <Clock size={22} />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-brand-600 dark:text-brand-400">
                Next Upcoming Class
              </span>
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] font-semibold text-emerald-600">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Starts in {countdownMinutes} mins
              </span>
            </div>
            <h2 className="text-lg font-bold text-ink mt-0.5">
              Compiler Construction <span className="text-xs font-normal text-muted">(CSC-354 · 3 Credit Hours)</span>
            </h2>
            <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-muted">
              <span className="flex items-center gap-1">
                <MapPin size={13} className="text-brand-600" />
                <strong>Room C-204</strong> (C Block, 2nd Floor)
              </span>
              <span>·</span>
              <span>
                Instructor: <strong>Dr. Munir Ahmad</strong>
              </span>
              <span>·</span>
              <span className="font-mono">Slot 2 (10:15 AM – 11:45 AM)</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 self-stretch md:self-auto justify-end">
          <button
            type="button"
            onClick={() => {
              const comp = ENROLLED_COURSES[0];
              if (comp) {
                setSelectedCourse(comp);
                setActiveModalTab("lectureHub");
              }
            }}
            className="rounded-xl border border-line bg-panel px-3.5 py-2 text-xs font-semibold text-text hover:border-brand-500 transition shadow-2xs"
          >
            Open Lecture Hub
          </button>
          <Link
            to="/app/student/timetable"
            className="inline-flex items-center gap-1 rounded-xl bg-brand-600 px-3.5 py-2 text-xs font-semibold text-white hover:bg-brand-700 transition shadow-xs"
          >
            <span>Full Schedule</span>
            <ArrowUpRight size={14} />
          </Link>
        </div>
      </div>

      {/* Top Academic Stat Cards */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Cumulative Attendance"
          value={attendance.data ? `${attendance.data.percentage.toFixed(1)}%` : "83.3%"}
          helper="Weighted across 4 enrolled subjects."
        />
        <StatCard
          label="Enrolled Courses"
          value={`${ENROLLED_COURSES.length} Courses`}
          helper="14 Total Credit Hours this semester."
        />
        <StatCard
          label="Pending Assignments"
          value="2 Pending"
          helper="Nearest: Compiler Construction tomorrow."
        />
        <StatCard
          label="Unread Notifications"
          value={unread.data ?? "3"}
          helper="New announcements from faculty."
        />
      </div>

      {/* ================= 3. ENROLLED SUBJECT CARDS GRID (CLIENT MANDATE) ================= */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-lg font-bold text-ink">My Enrolled Subjects</h2>
            <p className="text-xs text-muted">
              Click on any subject card to inspect its Assignments, Quizzes, Attendance, Marks, Resources & Lecture Hub.
            </p>
          </div>
          <span className="text-xs font-semibold text-brand-600 hidden sm:inline">
            Active Semester: Fall 2026 / Spring 2026
          </span>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-4">
          {ENROLLED_COURSES.map((course) => {
            const isSafe = course.attendancePercentage >= 75;
            return (
              <div
                key={course.id}
                onClick={() => {
                  setSelectedCourse(course);
                  setActiveModalTab("assignments");
                }}
                className="cursor-pointer rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-brand-500 hover:shadow-md transition flex flex-col justify-between group"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-brand-600 dark:text-brand-400">
                      {course.code}
                    </span>
                    <span className="rounded-md bg-surface px-2 py-0.5 text-[11px] font-semibold text-muted">
                      {course.creditHours} Cr. Hrs
                    </span>
                  </div>

                  <h3 className="mt-2 text-base font-bold text-ink group-hover:text-brand-600 transition">
                    {course.title}
                  </h3>

                  <p className="mt-1 text-xs text-muted flex items-center gap-1.5">
                    <span>Teacher:</span>
                    <strong className="text-ink">{course.teacherName}</strong>
                  </p>

                  {/* Attendance Progress Bar */}
                  <div className="mt-4 space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-muted">Attendance</span>
                      <span className={`font-bold font-mono ${isSafe ? "text-emerald-600" : "text-amber-600"}`}>
                        {course.attendancePercentage}% ({course.attendedLectures}/{course.totalLectures})
                      </span>
                    </div>

                    <div className="h-2 w-full overflow-hidden rounded-full bg-surface">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          isSafe ? "bg-emerald-500" : "bg-amber-500"
                        }`}
                        style={{ width: `${Math.min(course.attendancePercentage, 100)}%` }}
                      />
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-muted pt-0.5">
                      <span>Room: {course.room.split(" ")[0]}</span>
                      <span className={isSafe ? "text-emerald-600" : "text-amber-600"}>
                        {isSafe ? "Eligible" : "Warning (<75%)"}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between text-xs font-semibold text-brand-600 group-hover:text-brand-700">
                  <span>Detailed Screen</span>
                  <ChevronRight size={15} className="group-hover:translate-x-0.5 transition" />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ================= 4. QUICK ACTION DOCK ================= */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Link
          to="/explore"
          className="rounded-2xl border border-line bg-panel p-4 shadow-2xs hover:border-brand-500 transition flex items-center gap-3.5 group"
        >
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-500/10 text-amber-600">
            <Clock size={20} />
          </div>
          <div>
            <p className="text-sm font-bold text-ink group-hover:text-brand-600 transition">Free Slots Finder</p>
            <p className="text-xs text-muted">A, C, D Block empty study rooms</p>
          </div>
        </Link>

        <Link
          to="/explore"
          className="rounded-2xl border border-line bg-panel p-4 shadow-2xs hover:border-brand-500 transition flex items-center gap-3.5 group"
        >
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-600">
            <Bus size={20} />
          </div>
          <div>
            <p className="text-sm font-bold text-ink group-hover:text-brand-600 transition">Shuttle Tracker</p>
            <p className="text-xs text-muted">Farid Town & City bus timings</p>
          </div>
        </Link>

        <Link
          to="/app/student/learning"
          className="rounded-2xl border border-line bg-panel p-4 shadow-2xs hover:border-brand-500 transition flex items-center gap-3.5 group"
        >
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-500/10 text-violet-600">
            <Sparkles size={20} />
          </div>
          <div>
            <p className="text-sm font-bold text-ink group-hover:text-brand-600 transition">AI Self-Assessment</p>
            <p className="text-xs text-muted">Smart practice & KaTeX solutions</p>
          </div>
        </Link>

        <Link
          to="/explore"
          className="rounded-2xl border border-line bg-panel p-4 shadow-2xs hover:border-brand-500 transition flex items-center gap-3.5 group"
        >
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-purple-500/10 text-purple-600">
            <Compass size={20} />
          </div>
          <div>
            <p className="text-sm font-bold text-ink group-hover:text-brand-600 transition">Campus Directory</p>
            <p className="text-xs text-muted">Faculty offices & department labs</p>
          </div>
        </Link>
      </div>

      {/* Attendance History Graph */}
      <Card title="Attendance Progression Over Semester" description="Official academic session presence tracking.">
        {records.error ? (
          <InlineError message="Attendance history could not be loaded." />
        ) : records.isLoading ? (
          <SectionLoader label="Loading attendance history…" />
        ) : (
          <AttendanceChart records={records.data ?? []} />
        )}
      </Card>

      {/* ================= 5. DETAILED SUBJECT MODAL (WITH THE 8 SPECIFIED CARDS) ================= */}
      {selectedCourse && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs">
          <div className="flex max-h-[90vh] w-full max-w-4xl flex-col rounded-3xl border border-line bg-panel shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-line px-6 py-4 bg-surface/50">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-brand-600">{selectedCourse.code}</span>
                  <span className="rounded-md bg-panel px-2 py-0.5 text-xs text-muted font-medium">
                    {selectedCourse.creditHours} Credit Hours
                  </span>
                  <span
                    className={`rounded-md px-2 py-0.5 text-xs font-bold ${
                      selectedCourse.attendancePercentage >= 75
                        ? "bg-emerald-500/10 text-emerald-600"
                        : "bg-amber-500/10 text-amber-600"
                    }`}
                  >
                    Attendance: {selectedCourse.attendancePercentage}%
                  </span>
                </div>
                <h3 className="text-xl font-bold text-ink mt-0.5">{selectedCourse.title}</h3>
                <p className="text-xs text-muted">
                  Instructor: <strong>{selectedCourse.teacherName}</strong> ({selectedCourse.teacherOffice})
                </p>
              </div>

              <button
                type="button"
                onClick={() => setSelectedCourse(null)}
                aria-label="Close modal"
                className="rounded-xl p-2 text-muted hover:bg-surface hover:text-ink transition"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Navigation Tabs (The 8 Specified Cards) */}
            <div className="flex flex-wrap border-b border-line bg-panel px-4 py-2 gap-1 text-xs overflow-x-auto">
              {[
                { id: "assignments", label: "Assignments", icon: FileText },
                { id: "quizzes", label: "Quizzes", icon: ClipboardCheck },
                { id: "attendance", label: "Attendance", icon: CheckCircle2 },
                { id: "marks", label: "Marks & Grading", icon: CreditCard },
                { id: "notifications", label: "Notifications", icon: Bell },
                { id: "resources", label: "Resources", icon: BookOpen },
                { id: "lectureHub", label: "Lecture Hub", icon: Video },
                { id: "courseInfo", label: "Course Info", icon: Info }
              ].map((tab) => {
                const Icon = tab.icon;
                const isActive = activeModalTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveModalTab(tab.id as typeof activeModalTab)}
                    className={`inline-flex items-center gap-1.5 rounded-xl px-3 py-1.5 font-semibold transition ${
                      isActive
                        ? "bg-brand-600 text-white shadow-2xs"
                        : "text-muted hover:text-ink hover:bg-surface"
                    }`}
                  >
                    <Icon size={14} />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Modal Tab Body */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {/* Card 1: Assignments */}
              {activeModalTab === "assignments" && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-sm text-ink">Course Assignments</h4>
                    <span className="text-xs text-muted">Total: {selectedCourse.assignments.length}</span>
                  </div>
                  <div className="space-y-2">
                    {selectedCourse.assignments.map((a) => (
                      <div
                        key={a.id}
                        className="rounded-xl border border-line bg-surface/50 p-3.5 flex items-center justify-between"
                      >
                        <div>
                          <p className="font-semibold text-sm text-ink">{a.title}</p>
                          <p className="text-xs text-muted mt-0.5">Due: {a.due}</p>
                        </div>
                        <span
                          className={`rounded-md px-2.5 py-1 text-xs font-semibold ${
                            a.status === "Submitted"
                              ? "bg-emerald-500/10 text-emerald-600"
                              : "bg-amber-500/10 text-amber-600"
                          }`}
                        >
                          {a.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Card 2: Quizzes */}
              {activeModalTab === "quizzes" && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-sm text-ink">Quizzes & Assessment Tests</h4>
                    <Link
                      to="/app/student/learning"
                      className="inline-flex items-center gap-1 text-xs font-semibold text-brand-600 hover:underline"
                    >
                      <Sparkles size={13} />
                      <span>Take AI Adaptive Practice Quiz</span>
                    </Link>
                  </div>
                  <div className="space-y-2">
                    {selectedCourse.quizzes.map((q) => (
                      <div
                        key={q.id}
                        className="rounded-xl border border-line bg-surface/50 p-3.5 flex items-center justify-between"
                      >
                        <div>
                          <p className="font-semibold text-sm text-ink">{q.title}</p>
                          <p className="text-xs text-muted mt-0.5">Graded Sessional Quiz</p>
                        </div>
                        <span className="font-mono text-sm font-bold text-brand-600">
                          {q.score} / {q.maxScore}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Card 3: Attendance */}
              {activeModalTab === "attendance" && (
                <div className="space-y-4">
                  <div className="rounded-xl border border-line bg-surface/40 p-4 flex items-center justify-between">
                    <div>
                      <p className="text-xs text-muted">Attendance Status</p>
                      <p className="text-lg font-bold text-ink">
                        {selectedCourse.attendedLectures} Attended / {selectedCourse.totalLectures} Conducted
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-muted">Percentage</p>
                      <p
                        className={`text-xl font-bold font-mono ${
                          selectedCourse.attendancePercentage >= 75 ? "text-emerald-600" : "text-amber-600"
                        }`}
                      >
                        {selectedCourse.attendancePercentage}%
                      </p>
                    </div>
                  </div>

                  <p className="text-xs text-muted leading-relaxed">
                    According to CUI academic regulations, students must maintain $\ge 75\%$ attendance in each registered course to be eligible to sit in the terminal examinations.
                  </p>
                </div>
              )}

              {/* Card 4: Marks */}
              {activeModalTab === "marks" && (
                <div className="space-y-3">
                  <h4 className="font-bold text-sm text-ink">Grading & Evaluation Breakdown</h4>
                  <div className="rounded-xl border border-line overflow-hidden">
                    <table className="w-full text-xs text-left">
                      <thead className="bg-surface/60 text-muted font-bold border-b border-line">
                        <tr>
                          <th className="p-3">Component</th>
                          <th className="p-3">Weightage</th>
                          <th className="p-3">Obtained</th>
                          <th className="p-3">Max Marks</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-line/60">
                        {selectedCourse.marks.map((m, i) => (
                          <tr key={i} className="hover:bg-surface/30">
                            <td className="p-3 font-medium text-ink">{m.component}</td>
                            <td className="p-3 font-mono text-muted">{m.weight}</td>
                            <td className="p-3 font-mono font-bold text-brand-600">{m.obtained}</td>
                            <td className="p-3 font-mono text-muted">{m.max}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Card 5: Notifications */}
              {activeModalTab === "notifications" && (
                <div className="space-y-3">
                  <h4 className="font-bold text-sm text-ink">Subject Notifications</h4>
                  <div className="space-y-2">
                    {selectedCourse.notifications.map((n) => (
                      <div key={n.id} className="rounded-xl border border-line bg-surface/50 p-3.5 space-y-1">
                        <span className="text-[11px] font-bold text-brand-600">{n.date}</span>
                        <p className="text-xs text-ink leading-relaxed">{n.message}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Card 6: Resources */}
              {activeModalTab === "resources" && (
                <div className="space-y-3">
                  <h4 className="font-bold text-sm text-ink">Course Materials & Downloads</h4>
                  <div className="space-y-2">
                    {selectedCourse.resources.map((r) => (
                      <div
                        key={r.id}
                        className="rounded-xl border border-line bg-surface/50 p-3.5 flex items-center justify-between"
                      >
                        <div className="flex items-center gap-2.5">
                          <span className="rounded-md bg-brand-500/10 px-2 py-0.5 font-mono text-[11px] font-bold text-brand-600">
                            {r.type}
                          </span>
                          <div>
                            <p className="font-semibold text-xs text-ink">{r.title}</p>
                            <p className="text-[11px] text-muted">{r.size}</p>
                          </div>
                        </div>
                        <button
                          type="button"
                          className="rounded-lg border border-line bg-panel px-3 py-1 text-xs font-semibold text-brand-600 hover:border-brand-500 transition"
                        >
                          Download
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Card 7: Lecture Hub */}
              {activeModalTab === "lectureHub" && (
                <div className="space-y-3">
                  <h4 className="font-bold text-sm text-ink">Lecture Hub & Video Archives</h4>
                  <div className="space-y-2">
                    {selectedCourse.lectureHub.map((lec) => (
                      <div
                        key={lec.lectureNo}
                        className="rounded-xl border border-line bg-surface/50 p-3.5 flex items-center justify-between"
                      >
                        <div>
                          <p className="font-bold text-xs text-ink">
                            Lecture {lec.lectureNo}: {lec.topic}
                          </p>
                          <p className="text-[11px] text-muted mt-0.5">Date: {lec.date}</p>
                        </div>
                        {lec.hasRecording ? (
                          <span className="inline-flex items-center gap-1 rounded-md bg-brand-500/10 px-2.5 py-1 text-xs font-semibold text-brand-600">
                            <Video size={13} />
                            <span>Recording</span>
                          </span>
                        ) : (
                          <span className="text-[11px] text-muted">Slides Only</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Card 8: Course Information */}
              {activeModalTab === "courseInfo" && (
                <div className="space-y-4 text-xs">
                  <div>
                    <h5 className="font-bold text-ink">Course Description</h5>
                    <p className="mt-1 text-muted leading-relaxed">{selectedCourse.courseInfo.description}</p>
                  </div>
                  <div>
                    <h5 className="font-bold text-ink">Prerequisites</h5>
                    <p className="mt-1 text-muted leading-relaxed">{selectedCourse.courseInfo.prerequisites}</p>
                  </div>
                  <div>
                    <h5 className="font-bold text-ink">Recommended Textbook</h5>
                    <p className="mt-1 text-muted leading-relaxed">{selectedCourse.courseInfo.textbook}</p>
                  </div>
                  <div>
                    <h5 className="font-bold text-ink">Grading & Exam Policy</h5>
                    <p className="mt-1 text-muted leading-relaxed">{selectedCourse.courseInfo.gradingPolicy}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
