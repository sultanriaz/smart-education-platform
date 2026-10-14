import { zonedInstant } from "../../lib/zoned-iso";
import type {
  AttendanceEntry,
  AttendanceSession,
  QuestionBank,
  RosterMember,
  TeacherAnnouncement,
  TeacherAssignment,
  TeacherAttempt,
  TeacherAttemptAnswer,
  TeacherBooking,
  TeacherFacility,
  TeacherLearningResource,
  TeacherQuestion,
  TeacherQuiz,
  TeacherSection,
  TeacherTimetableItem
} from "./types";

export function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

export function extractList(value: unknown): unknown[] {
  if (Array.isArray(value)) return value;
  const r = asRecord(value);
  for (const key of [
    "items",
    "results",
    "data",
    "records",
    "sections",
    "students",
    "roster",
    "sessions",
    "resources",
    "quizzes",
    "assignments",
    "attempts",
    "campaigns"
  ]) {
    if (Array.isArray(r[key])) return r[key] as unknown[];
  }
  return [];
}

const str = (value: unknown, fallback = "") =>
  typeof value === "string" ? value : fallback;
const num = (value: unknown, fallback = 0) =>
  typeof value === "number" && Number.isFinite(value) ? value : fallback;
const bool = (value: unknown, fallback = false) =>
  typeof value === "boolean" ? value : fallback;
const nullableStr = (value: unknown) =>
  typeof value === "string" ? value : null;

export function normalizeSection(value: unknown): TeacherSection {
  const r = asRecord(value);
  const section = asRecord(r.section);
  const course = asRecord(r.course);
  return {
    id: str(r.id ?? r.section_id ?? section.id),
    name: str(r.name ?? r.section_name ?? section.name ?? r.code, "Section"),
    courseId: str(r.course_id ?? course.id) || undefined,
    courseCode: str(r.course_code ?? course.code) || undefined,
    courseTitle: str(r.course_title ?? r.course_name ?? course.title ?? course.name) || undefined,
    semesterId: str(r.semester_id) || undefined,
    capacity:
      typeof (r.capacity ?? section.capacity) === "number"
        ? Number(r.capacity ?? section.capacity)
        : null
  };
}

export function normalizeRosterMember(value: unknown): RosterMember {
  const r = asRecord(value);
  const student = asRecord(r.student);
  return {
    userId: str(r.external_user_id ?? r.student_user_id ?? r.user_id ?? student.identity_user_id ?? student.user_id ?? r.id),
    studentId: str(r.student_number ?? r.student_id ?? r.registration_number ?? student.student_id ?? student.registration_number) || undefined,
    name: str(r.full_name ?? r.name ?? student.full_name ?? student.name) || undefined,
    email: str(r.email ?? student.email) || undefined,
    enrollmentStatus: str(r.status ?? r.enrollment_status) || undefined
  };
}

export function normalizeAttendanceSession(value: unknown): AttendanceSession {
  const r = asRecord(value);
  return {
    id: str(r.id ?? r.session_id),
    sectionId: str(r.section_id),
    sessionDate: str(r.session_date ?? r.date),
    startsAt: nullableStr(r.starts_at ?? r.start_time),
    endsAt: nullableStr(r.ends_at ?? r.end_time),
    status: str(r.status, "OPEN"),
    locked: bool(r.locked ?? r.is_locked, false)
  };
}

export function normalizeAttendanceEntry(value: unknown): AttendanceEntry {
  const r = asRecord(value);
  return {
    id: str(r.id ?? r.record_id) || undefined,
    studentUserId: str(r.student_user_id ?? r.user_id),
    studentName: str(r.student_name ?? r.full_name) || undefined,
    status: str(r.status, "PRESENT") as AttendanceEntry["status"],
    notes: nullableStr(r.notes)
  };
}

export function normalizeTimetable(value: unknown): TeacherTimetableItem {
  const r = asRecord(value);
  const date = str(r.occurrence_date ?? r.date);
  const startTime = str(r.starts_at ?? r.start_time);
  const endTime = str(r.ends_at ?? r.end_time);
  return {
    id: str(r.occurrence_id ?? r.id ?? r.schedule_id),
    sectionId: str(r.section_id),
    courseId: str(r.course_id) || undefined,
    roomId: nullableStr(r.room_id),
    date,
    startsAt: date && startTime && !startTime.includes("T") ? zonedInstant(date, startTime, str(r.timezone_name) || "UTC") : startTime,
    endsAt: date && endTime && !endTime.includes("T") ? zonedInstant(date, endTime, str(r.timezone_name) || "UTC") : endTime,
    title: str(r.course_title ?? r.course_code ?? r.title, "Scheduled class"),
    source: str(r.source) || undefined
  };
}

export function normalizeResource(value: unknown): TeacherLearningResource {
  const r = asRecord(value);
  return {
    id: str(r.id ?? r.resource_id),
    title: str(r.title, "Untitled resource"),
    description: nullableStr(r.description),
    resourceType: str(r.resource_type ?? r.type, "NOTE"),
    status: str(r.status, "DRAFT"),
    categoryId: nullableStr(r.category_id),
    tags: Array.isArray(r.tags) ? r.tags.filter((x): x is string => typeof x === "string") : [],
    targets: extractList(r.targets).map((target) => {
      const t = asRecord(target);
      return {
        target_type: str(t.target_type ?? t.type, "SECTION") as "SECTION" | "COURSE",
        target_id: str(t.target_id ?? t.id)
      };
    }),
    versions: extractList(r.versions).map((version) => {
      const v = asRecord(version);
      return {
        id: str(v.id),
        versionNumber: num(v.version_number),
        textContent: nullableStr(v.text_content),
        externalUrl: nullableStr(v.external_url),
        originalFilename: nullableStr(v.original_filename),
        changeNote: nullableStr(v.change_note),
        createdAt: str(v.created_at) || undefined
      };
    }),
    createdAt: str(r.created_at) || undefined,
    updatedAt: str(r.updated_at) || undefined
  };
}

export function normalizeBank(value: unknown): QuestionBank {
  const r = asRecord(value);
  return {
    id: str(r.id),
    name: str(r.name, "Question bank"),
    courseId: nullableStr(r.course_id)
  };
}

export function normalizeQuestion(value: unknown): TeacherQuestion {
  const r = asRecord(value);
  return {
    id: str(r.id),
    bankId: str(r.bank_id),
    questionType: str(r.question_type, "SHORT_TEXT"),
    prompt: str(r.prompt, "Question"),
    points: num(r.points, 1),
    correctText: nullableStr(r.correct_text),
    explanation: nullableStr(r.explanation),
    choices: extractList(r.choices).map((choice) => {
      const c = asRecord(choice);
      return {
        id: str(c.id),
        text: str(c.text),
        isCorrect: typeof c.is_correct === "boolean" ? c.is_correct : undefined
      };
    })
  };
}

export function normalizeQuiz(value: unknown): TeacherQuiz {
  const r = asRecord(value);
  return {
    id: str(r.id),
    title: str(r.title, "Quiz"),
    description: nullableStr(r.description),
    courseId: str(r.course_id),
    status: str(r.status, "DRAFT"),
    durationMinutes: typeof r.duration_minutes === "number" ? r.duration_minutes : null,
    passPercent: num(r.pass_percent, 50),
    questionCount:
      typeof r.question_count === "number"
        ? r.question_count
        : Array.isArray(r.questions)
          ? r.questions.length
          : undefined
  };
}

export function normalizeAssignment(value: unknown): TeacherAssignment {
  const r = asRecord(value);
  return {
    id: str(r.id ?? r.assignment_id),
    quizId: str(r.quiz_id),
    quizTitle: str(r.quiz_title ?? r.title) || undefined,
    sectionId: str(r.section_id),
    opensAt: str(r.opens_at),
    dueAt: str(r.due_at),
    attemptLimit: num(r.attempt_limit, 1)
  };
}

export function normalizeAttemptAnswer(value: unknown): TeacherAttemptAnswer {
  const r = asRecord(value);
  return {
    id: str(r.id ?? r.answer_id),
    questionId: str(r.question_id),
    prompt: str(r.prompt) || undefined,
    questionType: str(r.question_type) || undefined,
    points: typeof r.points === "number" ? r.points : undefined,
    textAnswer: nullableStr(r.text_answer),
    selectedChoiceId: nullableStr(r.selected_choice_id),
    autoScore: typeof r.auto_score === "number" ? r.auto_score : null,
    manualScore: typeof r.manual_score === "number" ? r.manual_score : null,
    feedback: nullableStr(r.feedback)
  };
}

export function normalizeAttempt(value: unknown): TeacherAttempt {
  const r = asRecord(value);
  return {
    id: str(r.id ?? r.attempt_id),
    assignmentId: str(r.assignment_id),
    studentUserId: str(r.student_user_id),
    attemptNumber: num(r.attempt_number, 1),
    status: str(r.status, "UNKNOWN"),
    score: typeof r.score === "number" ? r.score : null,
    maxScore: typeof r.max_score === "number" ? r.max_score : null,
    percent: typeof r.percent === "number" ? r.percent : null,
    passed: typeof r.passed === "boolean" ? r.passed : null,
    startedAt: str(r.started_at),
    submittedAt: nullableStr(r.submitted_at),
    gradedAt: nullableStr(r.graded_at),
    answers: extractList(r.answers).map(normalizeAttemptAnswer)
  };
}

export function normalizeFacility(value: unknown): TeacherFacility {
  const r = asRecord(value);
  return {
    id: str(r.id ?? r.facility_id),
    name: str(r.name, "Facility"),
    code: str(r.code) || undefined,
    type: str(r.facility_type ?? r.type) || undefined,
    capacity: typeof r.capacity === "number" ? r.capacity : null,
    building: nullableStr(r.building),
    isBookable: bool(r.is_bookable ?? r.bookable, true)
  };
}

export function normalizeBooking(value: unknown): TeacherBooking {
  const r = asRecord(value);
  return {
    id: str(r.id ?? r.booking_id),
    facilityId: str(r.facility_id),
    purpose: str(r.purpose),
    startsAt: str(r.starts_at),
    endsAt: str(r.ends_at),
    attendees: num(r.attendees, 1),
    status: str(r.status, "UNKNOWN")
  };
}

export function normalizeAnnouncement(value: unknown): TeacherAnnouncement {
  const r = asRecord(value);
  const target = asRecord(r.target_value);
  return {
    id: str(r.id),
    sectionId: str(target.section_id ?? r.section_id) || undefined,
    title: str(r.title, "Announcement"),
    body: str(r.body),
    category: str(r.category) || undefined,
    channels: Array.isArray(r.channels) ? r.channels.filter((x): x is string => typeof x === "string") : [],
    recipientCount: num(r.recipient_count),
    status: str(r.status, "UNKNOWN"),
    createdAt: str(r.created_at)
  };
}
