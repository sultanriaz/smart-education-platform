import { apiRequest } from "../../lib/api-client";
import {
  extractList,
  normalizeAnnouncement,
  normalizeAssignment,
  normalizeAttendanceEntry,
  normalizeAttendanceSession,
  normalizeBank,
  normalizeBooking,
  normalizeFacility,
  normalizeQuestion,
  normalizeResource,
  normalizeRosterMember,
  normalizeSection,
  normalizeAttempt,
  normalizeQuiz,
  normalizeTimetable
} from "./normalizers";
import type {
  AttendanceEntry,
  AttendanceSession,
  QuestionBank,
  RosterMember,
  TeacherAnnouncement,
  TeacherAssignment,
  TeacherAttempt,
  TeacherBooking,
  TeacherFacility,
  TeacherLearningResource,
  TeacherQuestion,
  TeacherQuiz,
  TeacherSection,
  TeacherTimetableItem
} from "./types";

function dateOnly(value: Date) {
  return value.toISOString().slice(0, 10);
}

export function defaultTimetableWindow() {
  const start = new Date();
  start.setHours(0, 0, 0, 0);
  const day = start.getDay();
  const diffToMonday = day === 0 ? -6 : 1 - day;
  start.setDate(start.getDate() + diffToMonday);

  const end = new Date(start);
  end.setDate(start.getDate() + 13);

  return {
    startDate: dateOnly(start),
    endDate: dateOnly(end)
  };
}

// Academic
export async function getTeacherSections(): Promise<TeacherSection[]> {
  const response = await apiRequest<unknown>(
    "/api/v1/academic/sections"
  );
  return extractList(response).map(normalizeSection);
}

export async function getSectionRoster(sectionId: string): Promise<RosterMember[]> {
  const members: RosterMember[] = [];
  for (let offset = 0; ; offset += 100) {
    const response = await apiRequest<unknown>(
      `/api/v1/academic/sections/${encodeURIComponent(sectionId)}/roster?limit=100&offset=${offset}`
    );
    const batch = extractList(response).map(normalizeRosterMember);
    members.push(...batch);
    if (batch.length < 100) break;
    if (offset >= 10000) throw new Error("Roster exceeds the configured safe pagination limit.");
  }
  return members;
}

// Attendance
export async function getSectionAttendanceSessions(
  sectionId: string
): Promise<AttendanceSession[]> {
  const response = await apiRequest<unknown>(
    `/api/v1/attendance/sessions?section_id=${encodeURIComponent(sectionId)}`
  );
  return extractList(response).map(normalizeAttendanceSession);
}

export async function createAttendanceSession(input: {
  section_id: string;
  session_date: string;
  schedule_occurrence_id?: string;
  starts_at?: string;
  ends_at?: string;
}): Promise<AttendanceSession> {
  const response = await apiRequest<unknown>("/api/v1/attendance/sessions", {
    method: "POST",
    body: JSON.stringify(input)
  });
  return normalizeAttendanceSession(response);
}

export async function getSessionAttendance(
  sessionId: string
): Promise<AttendanceEntry[]> {
  const records: AttendanceEntry[] = [];
  for (let offset = 0; ; offset += 100) {
    const response = await apiRequest<unknown>(
      `/api/v1/attendance/sessions/${encodeURIComponent(sessionId)}/records?limit=100&offset=${offset}`
    );
    const batch = extractList(response).map(normalizeAttendanceEntry);
    records.push(...batch);
    if (batch.length < 100) break;
    if (offset >= 10000) throw new Error("Attendance records exceed the safe pagination limit.");
  }
  return records;
}

export async function saveBulkAttendance(
  sessionId: string,
  records: AttendanceEntry[]
): Promise<AttendanceEntry[]> {
  const response = await apiRequest<unknown>(
    `/api/v1/attendance/sessions/${sessionId}/records`,
    {
      method: "PUT",
      body: JSON.stringify({
        records: records.map((record) => ({
          student_user_id: record.studentUserId,
          status: record.status,
          notes: record.notes ?? null
        }))
      })
    }
  );
  return extractList(response).map(normalizeAttendanceEntry);
}

export async function correctAttendanceRecord(
  sessionId: string,
  studentUserId: string,
  input: { status: AttendanceEntry["status"]; notes?: string | null; reason: string }
): Promise<AttendanceEntry> {
  const response = await apiRequest<unknown>(
    `/api/v1/attendance/sessions/${sessionId}/records/${studentUserId}`,
    {
      method: "PATCH",
      body: JSON.stringify(input)
    }
  );
  return normalizeAttendanceEntry(response);
}

export async function finalizeAttendanceSession(sessionId: string): Promise<void> {
  await apiRequest(`/api/v1/attendance/sessions/${sessionId}/finalize`, {
    method: "POST"
  });
}

// Scheduling
export async function getTeacherTimetable(
  startDate?: string,
  endDate?: string
): Promise<TeacherTimetableItem[]> {
  const fallback = defaultTimetableWindow();
  const params = new URLSearchParams({
    start_date: startDate ?? fallback.startDate,
    end_date: endDate ?? fallback.endDate
  });
  const response = await apiRequest<unknown>(
    `/api/v1/scheduling/timetable/me?${params.toString()}`
  );
  return extractList(response).map(normalizeTimetable);
}

// Learning
export async function getTeacherResources(): Promise<TeacherLearningResource[]> {
  const response = await apiRequest<unknown>("/api/v1/learning/resources");
  return extractList(response).map(normalizeResource);
}

export async function createLearningResource(input: {
  title: string;
  description?: string;
  resource_type: "FILE" | "LINK" | "VIDEO" | "NOTE";
  category_id?: string | null;
  tags: string[];
  targets: Array<{ target_type: "SECTION" | "COURSE"; target_id: string }>;
}): Promise<TeacherLearningResource> {
  const response = await apiRequest<unknown>("/api/v1/learning/resources", {
    method: "POST",
    body: JSON.stringify(input)
  });
  return normalizeResource(response);
}

export async function addLearningContentVersion(
  resourceId: string,
  input: {
    text_content?: string;
    external_url?: string;
    change_note?: string;
  }
): Promise<void> {
  await apiRequest(`/api/v1/learning/resources/${resourceId}/versions`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export async function uploadLearningFile(
  resourceId: string,
  file: File,
  changeNote?: string
): Promise<void> {
  const form = new FormData();
  form.append("file", file);
  if (changeNote) form.append("change_note", changeNote);

  await apiRequest(`/api/v1/learning/resources/${resourceId}/upload`, {
    method: "POST",
    body: form
  });
}

export async function publishLearningResource(resourceId: string): Promise<void> {
  await apiRequest(`/api/v1/learning/resources/${resourceId}/publish`, {
    method: "POST"
  });
}

export async function archiveLearningResource(resourceId: string): Promise<void> {
  await apiRequest(`/api/v1/learning/resources/${resourceId}/archive`, {
    method: "POST"
  });
}

// Assessment
export async function getTeacherBanks(): Promise<QuestionBank[]> {
  const response = await apiRequest<unknown>(
    "/api/v1/assessments/teachers/me/banks"
  );
  return extractList(response).map(normalizeBank);
}

export async function getTeacherQuestions(bankId?: string): Promise<TeacherQuestion[]> {
  const suffix = bankId ? `?bank_id=${encodeURIComponent(bankId)}` : "";
  const response = await apiRequest<unknown>(
    `/api/v1/assessments/teachers/me/questions${suffix}`
  );
  return extractList(response).map(normalizeQuestion);
}

export async function createQuestionBank(input: {
  name: string;
  course_id?: string | null;
}): Promise<QuestionBank> {
  const response = await apiRequest<unknown>("/api/v1/assessments/banks", {
    method: "POST",
    body: JSON.stringify(input)
  });
  return normalizeBank(response);
}

export async function createQuestion(input: {
  bank_id: string;
  question_type: string;
  prompt: string;
  points: number;
  correct_text?: string | null;
  explanation?: string | null;
  choices: Array<{ text: string; is_correct: boolean }>;
}): Promise<TeacherQuestion> {
  const response = await apiRequest<unknown>("/api/v1/assessments/questions", {
    method: "POST",
    body: JSON.stringify(input)
  });
  return normalizeQuestion(response);
}

export async function getTeacherQuizzes(): Promise<TeacherQuiz[]> {
  const response = await apiRequest<unknown>(
    "/api/v1/assessments/teachers/me/quizzes"
  );
  return extractList(response).map(normalizeQuiz);
}

export async function createQuiz(input: {
  title: string;
  description?: string;
  course_id: string;
  duration_minutes?: number | null;
  pass_percent: number;
}): Promise<TeacherQuiz> {
  const response = await apiRequest<unknown>("/api/v1/assessments/quizzes", {
    method: "POST",
    body: JSON.stringify(input)
  });
  return normalizeQuiz(response);
}

export async function addQuestionToQuiz(
  quizId: string,
  input: { question_id: string; position: number; points_override?: number | null }
): Promise<void> {
  await apiRequest(`/api/v1/assessments/quizzes/${quizId}/questions`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export async function publishQuiz(quizId: string): Promise<void> {
  await apiRequest(`/api/v1/assessments/quizzes/${quizId}/publish`, {
    method: "POST"
  });
}

export async function getTeacherAssignments(): Promise<TeacherAssignment[]> {
  const response = await apiRequest<unknown>(
    "/api/v1/assessments/teachers/me/assignments"
  );
  return extractList(response).map(normalizeAssignment);
}

export async function assignQuiz(
  quizId: string,
  input: {
    section_id: string;
    opens_at: string;
    due_at: string;
    attempt_limit: number;
  }
): Promise<TeacherAssignment> {
  const response = await apiRequest<unknown>(
    `/api/v1/assessments/quizzes/${quizId}/assignments`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
  return normalizeAssignment(response);
}

export async function getAssignmentAttempts(
  assignmentId: string
): Promise<TeacherAttempt[]> {
  const response = await apiRequest<unknown>(
    `/api/v1/assessments/teachers/me/assignments/${assignmentId}/attempts`
  );
  return extractList(response).map(normalizeAttempt);
}

export async function gradeAttempt(input: {
  attemptId: string;
  answerId: string;
  score: number;
  feedback?: string;
  reason: string;
}): Promise<TeacherAttempt> {
  const response = await apiRequest<unknown>(
    `/api/v1/assessments/attempts/${input.attemptId}/grade`,
    {
      method: "POST",
      body: JSON.stringify({
        answer_id: input.answerId,
        score: input.score,
        feedback: input.feedback ?? null,
        reason: input.reason
      })
    }
  );
  return normalizeAttempt(response);
}

// Facilities
export async function getTeacherFacilities(): Promise<TeacherFacility[]> {
  const response = await apiRequest<unknown>("/api/v1/facilities/facilities");
  return extractList(response).map(normalizeFacility);
}

export async function getTeacherBookings(): Promise<TeacherBooking[]> {
  const response = await apiRequest<unknown>("/api/v1/facilities/bookings");
  return extractList(response).map(normalizeBooking);
}

export async function createTeacherBooking(input: {
  facility_id: string;
  purpose: string;
  starts_at: string;
  ends_at: string;
  attendees: number;
}): Promise<TeacherBooking> {
  const response = await apiRequest<unknown>("/api/v1/facilities/bookings", {
    method: "POST",
    body: JSON.stringify(input)
  });
  return normalizeBooking(response);
}

export async function cancelTeacherBooking(
  bookingId: string,
  reason: string
): Promise<void> {
  await apiRequest(`/api/v1/facilities/bookings/${bookingId}/cancel`, {
    method: "POST",
    body: JSON.stringify({ reason })
  });
}

// Announcements
export async function getTeacherAnnouncements(): Promise<TeacherAnnouncement[]> {
  const response = await apiRequest<unknown>(
    "/api/v1/notifications/teacher/announcements"
  );
  return extractList(response).map(normalizeAnnouncement);
}

export async function createTeacherAnnouncement(input: {
  section_id: string;
  title: string;
  body: string;
  category: string;
  priority: "LOW" | "NORMAL" | "HIGH" | "URGENT";
  channels: Array<"IN_APP" | "EMAIL">;
}): Promise<TeacherAnnouncement> {
  const response = await apiRequest<unknown>(
    "/api/v1/notifications/teacher/announcements",
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
  return normalizeAnnouncement(response);
}
