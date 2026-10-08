import type {
  AssessmentAssignment,
  AssessmentAssignmentDetail,
  AssessmentAttempt,
  AssessmentQuestion,
  AssessmentResult,
  AttendanceRecord,
  AttendanceSummary,
  Booking,
  Facility,
  LearningResource,
  NotificationItem,
  NotificationPreferences,
  TimetableItem
} from "./types";

export function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};
}

export function extractList(value: unknown): unknown[] {
  if (Array.isArray(value)) return value;
  const record = asRecord(value);
  for (const key of ["items", "results", "data", "records", "resources", "notifications", "bookings", "assignments"]) {
    const candidate = record[key];
    if (Array.isArray(candidate)) return candidate;
  }
  return [];
}

function str(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

function num(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function bool(value: unknown, fallback = false): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function nullableStr(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}

export function normalizeAttendanceSummary(value: unknown): AttendanceSummary {
  const r = asRecord(asRecord(value).totals ?? value);
  return {
    present: num(r.present_sessions ?? r.present ?? r.present_count),
    absent: num(r.absent_sessions ?? r.absent ?? r.absent_count),
    late: num(r.late_sessions ?? r.late ?? r.late_count),
    excused: num(r.excused_sessions ?? r.excused ?? r.excused_count),
    totalConsidered: num(
      r.total_considered_sessions ?? r.total_considered ?? r.total_sessions
    ),
    percentage: num(
      r.attendance_percentage ?? r.percentage ?? r.percent
    )
  };
}

export function normalizeAttendanceRecord(value: unknown): AttendanceRecord {
  const r = asRecord(value);
  return {
    id: str(r.id ?? r.record_id ?? `${r.attendance_session_id ?? "session"}:${r.student_user_id ?? "student"}`),
    sessionId: str(r.attendance_session_id ?? r.session_id) || undefined,
    sectionId: str(r.section_id) || undefined,
    courseId: str(r.course_id) || undefined,
    courseLabel: str(r.course_name ?? r.course_code ?? r.course_title) || undefined,
    sessionDate: str(r.session_date ?? r.date) || undefined,
    status: str(r.status, "UNKNOWN"),
    notes: nullableStr(r.notes)
  };
}

export function normalizeTimetableItem(value: unknown): TimetableItem {
  const r = asRecord(value);
  const date = str(r.occurrence_date ?? r.date);
  const at = (value: unknown) => { const time = str(value); return date && time && !time.includes("T") ? `${date}T${time}` : time; };
  return {
    id: str(r.id ?? r.occurrence_id ?? r.schedule_id ?? `${r.section_id}:${r.starts_at}`),
    title: str(r.title ?? r.course_name ?? r.course_code ?? r.section_name, "Scheduled class"),
    sectionId: str(r.section_id) || undefined,
    courseId: str(r.course_id) || undefined,
    roomLabel: str(r.room_name ?? r.room_code ?? r.facility_name ?? r.room_id) || undefined,
    startsAt: at(r.starts_at ?? r.start_time ?? r.start),
    endsAt: at(r.ends_at ?? r.end_time ?? r.end),
    status: str(r.status) || undefined
  };
}

export function normalizeLearningResource(value: unknown): LearningResource {
  const wrapper = asRecord(value);
  const r = wrapper.resource ? asRecord(wrapper.resource) : wrapper;
  const versions = extractList(r.versions).map(asRecord);
  const latest = versions.sort((a, b) => num(b.version_number) - num(a.version_number))[0] ?? {};
  return {
    id: str(r.id ?? r.resource_id),
    title: str(r.title, "Untitled resource"),
    description: nullableStr(r.description),
    resourceType: str(r.resource_type ?? r.type) || undefined,
    courseId: str(r.course_id) || undefined,
    sectionId: str(r.section_id) || undefined,
    publishedAt: nullableStr(r.published_at),
    downloadPath: nullableStr(r.download_url ?? r.download_path),
    externalUrl: nullableStr(latest.external_url ?? r.url ?? r.external_url),
    textContent: nullableStr(latest.text_content),
    score: typeof wrapper.score === "number" ? wrapper.score : null
  };
}

export function normalizeAssignment(value: unknown): AssessmentAssignment {
  const r = asRecord(value);
  return {
    id: str(r.id ?? r.assignment_id),
    quizId: str(r.quiz_id),
    title: str(r.title ?? r.quiz_title, "Assessment"),
    description: nullableStr(r.description),
    sectionId: str(r.section_id) || undefined,
    opensAt: str(r.opens_at),
    dueAt: str(r.due_at),
    attemptLimit: num(r.attempt_limit, 1),
    attemptsUsed: num(r.attempts_used ?? r.attempt_count),
    activeAttemptId: str(r.active_attempt_id) || undefined,
    status: str(r.status) || undefined
  };
}

export function normalizeResult(value: unknown): AssessmentResult {
  const r = asRecord(value);
  return {
    attemptId: str(r.attempt_id ?? r.id),
    assignmentId: str(r.assignment_id) || undefined,
    quizId: str(r.quiz_id) || undefined,
    title: str(r.title ?? r.quiz_title) || undefined,
    score: typeof r.score === "number" ? r.score : null,
    maxScore: typeof r.max_score === "number" ? r.max_score : null,
    percent: typeof r.percent === "number" ? r.percent : null,
    passed: typeof r.passed === "boolean" ? r.passed : null,
    status: str(r.status, "UNKNOWN"),
    submittedAt: nullableStr(r.submitted_at),
    gradedAt: nullableStr(r.graded_at)
  };
}

export function normalizeFacility(value: unknown): Facility {
  const r = asRecord(value);
  return {
    id: str(r.id ?? r.facility_id),
    name: str(r.name, "Facility"),
    code: str(r.code) || undefined,
    facilityType: str(r.facility_type ?? r.type) || undefined,
    building: nullableStr(r.building),
    floor: nullableStr(r.floor),
    capacity: typeof r.capacity === "number" ? r.capacity : null,
    isBookable: bool(r.is_bookable ?? r.bookable, true)
  };
}

export function normalizeBooking(value: unknown): Booking {
  const r = asRecord(value);
  return {
    id: str(r.id ?? r.booking_id),
    facilityId: str(r.facility_id),
    facilityName: str(r.facility_name) || undefined,
    startsAt: str(r.starts_at),
    endsAt: str(r.ends_at),
    purpose: nullableStr(r.purpose ?? r.reason),
    status: str(r.status, "UNKNOWN")
  };
}

export function normalizeNotification(value: unknown): NotificationItem {
  const r = asRecord(value);
  return {
    id: str(r.id ?? r.notification_id),
    title: str(r.title, "Notification"),
    message: str(r.message ?? r.body ?? r.content),
    category: nullableStr(r.category),
    readAt: nullableStr(r.read_at),
    createdAt: str(r.created_at ?? r.sent_at)
  };
}

export function normalizePreferences(value: unknown): NotificationPreferences {
  const r = asRecord(value);
  return {
    emailEnabled:
      typeof r.email_enabled === "boolean" ? r.email_enabled : undefined,
    inAppEnabled:
      typeof r.in_app_enabled === "boolean" ? r.in_app_enabled : undefined,
    mutedCategories: Array.isArray(r.muted_categories)
      ? r.muted_categories.filter((item): item is string => typeof item === "string")
      : []
  };
}


export function normalizeQuestion(value: unknown): AssessmentQuestion {
  const r = asRecord(value);
  const choices = extractList(r.choices).map((choice) => {
    const c = asRecord(choice);
    return {
      id: str(c.id ?? c.choice_id),
      text: str(c.text ?? c.label)
    };
  });

  return {
    id: str(r.id ?? r.question_id),
    prompt: str(r.prompt ?? r.text, "Question"),
    questionType: str(r.question_type ?? r.type, "SHORT_TEXT"),
    points: num(r.points, 1),
    choices
  };
}

export function normalizeAssignmentDetail(value: unknown): AssessmentAssignmentDetail {
  const r = asRecord(value);
  const base = normalizeAssignment(r);
  const quiz = asRecord(r.quiz);
  const questionSource =
    Array.isArray(r.questions) ? r.questions :
    Array.isArray(quiz.questions) ? quiz.questions :
    [];

  return {
    ...base,
    title: str(r.title ?? quiz.title ?? r.quiz_title, base.title),
    description:
      nullableStr(r.description ?? quiz.description) ?? base.description ?? null,
    durationMinutes:
      typeof (r.duration_minutes ?? quiz.duration_minutes) === "number"
        ? Number(r.duration_minutes ?? quiz.duration_minutes)
        : null,
    questions: questionSource.map(normalizeQuestion)
  };
}

export function normalizeAttempt(value: unknown): AssessmentAttempt {
  const r = asRecord(value);
  return {
    id: str(r.id ?? r.attempt_id),
    assignmentId: str(r.assignment_id),
    status: str(r.status, "IN_PROGRESS"),
    attemptNumber:
      typeof r.attempt_number === "number" ? r.attempt_number : undefined,
    answers: extractList(r.answers).map(value => {
      const answer = asRecord(value);
      return { questionId: str(answer.question_id), selectedChoiceId: str(answer.selected_choice_id) || undefined, textAnswer: typeof answer.text_answer === "string" ? answer.text_answer : undefined };
    })
  };
}
