import { apiDownload, apiRequest } from "../../lib/api-client";
import {
  extractList,
  normalizeAssignment,
  normalizeAssignmentDetail,
  normalizeAttempt,
  normalizeAttendanceRecord,
  normalizeAttendanceSummary,
  normalizeBooking,
  normalizeFacility,
  normalizeLearningResource,
  normalizeNotification,
  normalizePreferences,
  normalizeResult,
  normalizeTimetableItem
} from "./normalizers";
import type {
  AssessmentAssignment,
  AssessmentAssignmentDetail,
  AssessmentAttempt,
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

export type AttendanceFilters = {
  dateFrom?: string;
  dateTo?: string;
  courseId?: string;
  sectionId?: string;
  offset?: number;
  limit?: number;
};

function attendanceQuery(filters: AttendanceFilters = {}): string {
  const params = new URLSearchParams();
  if (filters.dateFrom) params.set("date_from", filters.dateFrom);
  if (filters.dateTo) params.set("date_to", filters.dateTo);
  if (filters.courseId) params.set("course_id", filters.courseId);
  if (filters.sectionId) params.set("section_id", filters.sectionId);
  params.set("limit", String(filters.limit ?? 50));
  params.set("offset", String(filters.offset ?? 0));
  return params.toString();
}

export async function getAttendanceSummary(filters: AttendanceFilters = {}): Promise<AttendanceSummary> {
  const response = await apiRequest<unknown>(
    `/api/v1/attendance/students/me/attendance/summary?${attendanceQuery(filters)}`
  );
  return normalizeAttendanceSummary(response);
}

export async function getAttendanceRecords(filters: AttendanceFilters = {}): Promise<AttendanceRecord[]> {
  const response = await apiRequest<unknown>(
    `/api/v1/attendance/students/me/attendance?${attendanceQuery(filters)}`
  );
  return extractList(response).map(normalizeAttendanceRecord);
}

export async function getMyTimetable(): Promise<TimetableItem[]> {
  const start = new Date();
  const end = new Date(start);
  end.setDate(start.getDate() + 13);
  const dateOnly = (value: Date) => `${value.getFullYear()}-${String(value.getMonth()+1).padStart(2,"0")}-${String(value.getDate()).padStart(2,"0")}`;
  const params = new URLSearchParams({ start_date: dateOnly(start), end_date: dateOnly(end) });
  const response = await apiRequest<unknown>(
    `/api/v1/scheduling/timetable/me?${params}`
  );
  return extractList(response).map(normalizeTimetableItem);
}

export async function getMyResources(): Promise<LearningResource[]> {
  const response = await apiRequest<unknown>(
    "/api/v1/learning/students/me/resources"
  );
  return extractList(response).map(normalizeLearningResource);
}

export type LearningActivity = { id: string; resource_id: string; action: string; created_at: string };
export async function getLearningActivity(offset=0, limit=25): Promise<LearningActivity[]> {
  const data = await apiRequest<unknown>(`/api/v1/learning/students/me/activity?offset=${offset}&limit=${limit}`);
  return extractList(data).filter((x): x is LearningActivity =>
    Boolean(x && typeof x === "object" && !Array.isArray(x) && "action" in x));
}
export async function logLearningResourceView(resourceId: string): Promise<void> {
  await apiRequest(`/api/v1/learning/resources/${encodeURIComponent(resourceId)}`);
}

export async function getRecommendations(): Promise<LearningResource[]> {
  const response = await apiRequest<unknown>(
    "/api/v1/learning/students/me/recommendations"
  );
  return extractList(response).map(normalizeLearningResource);
}

export async function getAssessmentAssignments(): Promise<AssessmentAssignment[]> {
  const response = await apiRequest<unknown>(
    "/api/v1/assessments/students/me/assignments"
  );
  return extractList(response).map(normalizeAssignment);
}

export async function getAssessmentResults(): Promise<AssessmentResult[]> {
  const response = await apiRequest<unknown>(
    "/api/v1/assessments/students/me/results"
  );
  return extractList(response).map(normalizeResult);
}


export async function getAssessmentAssignmentDetail(
  assignmentId: string
): Promise<AssessmentAssignmentDetail> {
  const response = await apiRequest<unknown>(
    `/api/v1/assessments/students/me/assignments/${assignmentId}`
  );
  return normalizeAssignmentDetail(response);
}

export async function getAttempt(attemptId: string): Promise<AssessmentAttempt> {
  const response = await apiRequest<unknown>(
    `/api/v1/assessments/attempts/${attemptId}`
  );
  return normalizeAttempt(response);
}

export async function getActiveAttempt(assignmentId: string): Promise<AssessmentAttempt | null> {
  const response = await apiRequest<unknown>(`/api/v1/assessments/students/me/assignments/${assignmentId}/active-attempt`);
  return response ? normalizeAttempt(response) : null;
}

export async function saveAttemptAnswer(
  attemptId: string,
  questionId: string,
  input: { selected_choice_id?: string; text_answer?: string }
): Promise<void> {
  await apiRequest(
    `/api/v1/assessments/attempts/${attemptId}/answers/${questionId}`,
    {
      method: "PUT",
      body: JSON.stringify(input)
    }
  );
}

export async function submitAttempt(attemptId: string): Promise<AssessmentResult> {
  const response = await apiRequest<unknown>(
    `/api/v1/assessments/attempts/${attemptId}/submit`,
    { method: "POST", body: "{}" }
  );
  return normalizeResult(response);
}

export async function startAttempt(
  assignmentId: string
): Promise<AssessmentAttempt> {
  const response = await apiRequest<unknown>(
    `/api/v1/assessments/assignments/${assignmentId}/attempts`,
    { method: "POST" }
  );
  return normalizeAttempt(response);
}

export async function getFacilities(): Promise<Facility[]> {
  const response = await apiRequest<unknown>(
    "/api/v1/facilities/facilities?bookable=true"
  );
  return extractList(response).map(normalizeFacility);
}

export async function getMyBookings(): Promise<Booking[]> {
  const response = await apiRequest<unknown>(
    "/api/v1/facilities/bookings"
  );
  return extractList(response).map(normalizeBooking);
}

export async function createBooking(input: {
  facility_id: string;
  starts_at: string;
  ends_at: string;
  purpose: string;
  attendees: number;
}): Promise<Booking> {
  const response = await apiRequest<unknown>(
    "/api/v1/facilities/bookings",
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
  return normalizeBooking(response);
}

export async function cancelBooking(input: { bookingId: string; reason: string }): Promise<void> {
  await apiRequest(
    `/api/v1/facilities/bookings/${input.bookingId}/cancel`,
    { method: "POST", body: JSON.stringify({ reason: input.reason }) }
  );
}

export type NotificationFilters = { offset?: number; limit?: number; unreadOnly?: boolean };

export async function getNotifications(filters: NotificationFilters = {}): Promise<NotificationItem[]> {
  const params = new URLSearchParams({
    offset: String(filters.offset ?? 0), limit: String(filters.limit ?? 25),
    unread_only: String(filters.unreadOnly ?? false)
  });
  const response = await apiRequest<unknown>(
    `/api/v1/notifications/notifications?${params}`
  );
  return extractList(response).map(normalizeNotification);
}

export async function getUnreadCount(): Promise<number> {
  const response = await apiRequest<Record<string, unknown>>(
    "/api/v1/notifications/notifications/unread-count"
  );
  const value = response.unread_count ?? response.count ?? response.total;
  return typeof value === "number" ? value : 0;
}

export async function markNotificationRead(notificationId: string): Promise<void> {
  await apiRequest(
    `/api/v1/notifications/notifications/${notificationId}/read`,
    { method: "POST" }
  );
}

export async function markAllNotificationsRead(): Promise<void> {
  await apiRequest(
    "/api/v1/notifications/notifications/read-all",
    { method: "POST" }
  );
}

export async function getNotificationPreferences(): Promise<NotificationPreferences> {
  const response = await apiRequest<unknown>(
    "/api/v1/notifications/preferences/me"
  );
  return normalizePreferences(response);
}

export async function updateNotificationPreferences(
  input: NotificationPreferences
): Promise<NotificationPreferences> {
  const response = await apiRequest<unknown>(
    "/api/v1/notifications/preferences/me",
    {
      method: "PATCH",
      body: JSON.stringify({
        email_enabled: input.emailEnabled,
        in_app_enabled: input.inAppEnabled,
        muted_categories: input.mutedCategories ?? []
      })
    }
  );
  return normalizePreferences(response);
}

export async function downloadLearningResource(resourceId: string) {
  const result = await apiDownload(
    `/api/v1/learning/resources/${resourceId}/download`
  );
  const url = URL.createObjectURL(result.blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = result.filename ?? `resource-${resourceId}`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
