import { apiDownload, apiRequest } from "../../lib/api-client";
import {
  academicYear,
  audit,
  booking,
  campaign,
  course,
  department,
  enrollment,
  facility,
  facilityBlock,
  feature,
  job,
  list,
  notificationTemplate,
  permission,
  program,
  reportingOverview,
  role,
  schedule,
  section,
  semester,
  serviceHealth,
  serviceRegistry,
  setting,
  snapshot,
  studentProfile,
  teacherProfile,
  teachingAssignment,
  ticket,
  user
} from "./normalizers";
import type {
  AcademicYear,
  AdminUser,
  AuditEvent,
  Booking,
  Course,
  Department,
  Enrollment,
  Facility,
  FacilityBlock,
  FeatureFlag,
  NotificationCampaign,
  NotificationTemplate,
  Permission,
  PlatformJob,
  PlatformSetting,
  Program,
  ReportSnapshot,
  ReportingOverview,
  Role,
  Schedule,
  Section,
  Semester,
  ServiceHealth,
  ServiceRegistry,
  StudentProfile,
  SupportTicket,
  TeacherProfile,
  TeachingAssignment
} from "./types";

// Identity
export async function listUsers(): Promise<AdminUser[]> {
  const response = await apiRequest<unknown>("/api/v1/identity/users?limit=200");
  return list(response).map(user);
}

export async function createUser(input: {
  email: string;
  full_name: string;
  password: string;
  role: string;
}): Promise<AdminUser> {
  return user(
    await apiRequest<unknown>("/api/v1/identity/users", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

export async function updateUser(
  userId: string,
  input: {
    full_name?: string;
    is_active?: boolean;
    is_verified?: boolean;
    roles?: string[];
  }
): Promise<AdminUser> {
  return user(
    await apiRequest<unknown>(`/api/v1/identity/users/${userId}`, {
      method: "PATCH",
      body: JSON.stringify(input)
    })
  );
}

export async function deactivateUser(userId: string): Promise<AdminUser> {
  return user(
    await apiRequest<unknown>(`/api/v1/identity/users/${userId}`, {
      method: "DELETE"
    })
  );
}

export async function listRoles(): Promise<Role[]> {
  return list(await apiRequest<unknown>("/api/v1/identity/roles")).map(role);
}

export async function listPermissions(): Promise<Permission[]> {
  return list(await apiRequest<unknown>("/api/v1/identity/permissions")).map(permission);
}

export async function createRole(input: {
  name: string;
  description?: string;
  permissions: string[];
}): Promise<Role> {
  return role(
    await apiRequest<unknown>("/api/v1/identity/roles", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

// Academic. These routes reflect the Sprint 2 domain model and are reconciled
// against the actual local Sprint 2 service during merge.
export async function listDepartments(): Promise<Department[]> {
  return list(await apiRequest<unknown>("/api/v1/academic/departments")).map(department);
}

export async function createDepartment(input: {
  code: string;
  name: string;
}): Promise<Department> {
  return department(
    await apiRequest<unknown>("/api/v1/academic/departments", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

export async function listPrograms(): Promise<Program[]> {
  return list(await apiRequest<unknown>("/api/v1/academic/programs")).map(program);
}

export async function createProgram(input: {
  code: string;
  name: string;
  department_id: string;
}): Promise<Program> {
  return program(
    await apiRequest<unknown>("/api/v1/academic/programs", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

export async function listAcademicYears(): Promise<AcademicYear[]> {
  return list(await apiRequest<unknown>("/api/v1/academic/academic-years")).map(academicYear);
}

export async function createAcademicYear(input: {
  name: string;
  starts_on: string;
  ends_on: string;
}): Promise<AcademicYear> {
  return academicYear(
    await apiRequest<unknown>("/api/v1/academic/academic-years", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

export async function listSemesters(): Promise<Semester[]> {
  return list(await apiRequest<unknown>("/api/v1/academic/semesters")).map(semester);
}

export async function createSemester(input: {
  name: string;
  academic_year_id: string;
  starts_on: string;
  ends_on: string;
}): Promise<Semester> {
  return semester(
    await apiRequest<unknown>("/api/v1/academic/semesters", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

export async function listCourses(): Promise<Course[]> {
  return list(await apiRequest<unknown>("/api/v1/academic/courses")).map(course);
}

export async function createCourse(input: {
  code: string;
  title: string;
  department_id?: string;
  credit_hours?: number;
}): Promise<Course> {
  return course(
    await apiRequest<unknown>("/api/v1/academic/courses", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

export async function listSections(): Promise<Section[]> {
  return list(await apiRequest<unknown>("/api/v1/academic/sections")).map(section);
}

export async function createSection(input: {
  name: string;
  course_id: string;
  semester_id: string;
  program_id?: string;
  capacity: number;
}): Promise<Section> {
  return section(
    await apiRequest<unknown>("/api/v1/academic/sections", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

export async function listStudentProfiles(): Promise<StudentProfile[]> {
  return list(await apiRequest<unknown>("/api/v1/academic/student-profiles")).map(studentProfile);
}

export async function createStudentProfile(input: {
  identity_user_id: string;
  student_id: string;
  program_id?: string;
  batch?: string;
}): Promise<StudentProfile> {
  return studentProfile(
    await apiRequest<unknown>("/api/v1/academic/student-profiles", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

export async function listTeacherProfiles(): Promise<TeacherProfile[]> {
  return list(await apiRequest<unknown>("/api/v1/academic/teacher-profiles")).map(teacherProfile);
}

export async function createTeacherProfile(input: {
  identity_user_id: string;
  employee_id: string;
  department_id?: string;
}): Promise<TeacherProfile> {
  return teacherProfile(
    await apiRequest<unknown>("/api/v1/academic/teacher-profiles", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

export async function listEnrollments(): Promise<Enrollment[]> {
  return list(await apiRequest<unknown>("/api/v1/academic/enrollments")).map(enrollment);
}

export async function createEnrollment(input: {
  student_user_id: string;
  section_id: string;
}): Promise<Enrollment> {
  return enrollment(
    await apiRequest<unknown>("/api/v1/academic/enrollments", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

export async function listTeachingAssignments(): Promise<TeachingAssignment[]> {
  return list(await apiRequest<unknown>("/api/v1/academic/teacher-assignments")).map(teachingAssignment);
}

export async function createTeachingAssignment(input: {
  teacher_user_id: string;
  section_id: string;
}): Promise<TeachingAssignment> {
  return teachingAssignment(
    await apiRequest<unknown>("/api/v1/academic/teacher-assignments", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

// Scheduling
export async function listSchedules(): Promise<Schedule[]> {
  return list(await apiRequest<unknown>("/api/v1/scheduling/schedules?limit=200")).map(schedule);
}

export async function createSchedule(input: {
  section_id: string;
  teacher_user_id?: string;
  room_id?: string;
  weekday: number;
  starts_at: string;
  ends_at: string;
  effective_from: string;
  effective_to: string;
  timezone_name?: string;
}): Promise<Schedule> {
  return schedule(
    await apiRequest<unknown>("/api/v1/scheduling/schedules", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

export async function cancelSchedule(
  scheduleId: string,
  reason?: string
): Promise<Schedule> {
  return schedule(
    await apiRequest<unknown>(`/api/v1/scheduling/schedules/${scheduleId}/cancel`, {
      method: "POST",
      body: JSON.stringify({ reason: reason || null })
    })
  );
}

export async function createScheduleOverride(
  scheduleId: string,
  input: {
    occurrence_date: string;
    kind: "CANCELLED" | "RESCHEDULED";
    starts_at?: string;
    ends_at?: string;
    room_id?: string;
    reason?: string;
  }
) {
  return apiRequest(`/api/v1/scheduling/schedules/${scheduleId}/overrides`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

// Facility
export async function listFacilities(): Promise<Facility[]> {
  return list(await apiRequest<unknown>("/api/v1/facilities/facilities?limit=200")).map(facility);
}

export async function createFacility(input: {
  code: string;
  name: string;
  kind: string;
  description?: string;
  building?: string;
  floor?: string;
  capacity: number;
  is_bookable: boolean;
  metadata?: Record<string, unknown>;
}): Promise<Facility> {
  return facility(
    await apiRequest<unknown>("/api/v1/facilities/facilities", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

export async function updateFacility(
  facilityId: string,
  input: {
    name?: string;
    kind?: string;
    building?: string;
    floor?: string;
    capacity?: number;
    is_active?: boolean;
    is_bookable?: boolean;
  }
): Promise<Facility> {
  return facility(
    await apiRequest<unknown>(`/api/v1/facilities/facilities/${facilityId}`, {
      method: "PATCH",
      body: JSON.stringify(input)
    })
  );
}

export async function listBookings(status?: string): Promise<Booking[]> {
  const suffix = status ? `?status=${encodeURIComponent(status)}&limit=200` : "?limit=200";
  return list(await apiRequest<unknown>(`/api/v1/facilities/bookings${suffix}`)).map(booking);
}

export async function decideBooking(
  bookingId: string,
  decision: "approve" | "reject",
  note?: string
): Promise<Booking> {
  return booking(
    await apiRequest<unknown>(
      `/api/v1/facilities/bookings/${bookingId}/${decision}`,
      {
        method: "POST",
        body: JSON.stringify({ note: note || null })
      }
    )
  );
}

export async function listFacilityBlocks(): Promise<FacilityBlock[]> {
  return list(await apiRequest<unknown>("/api/v1/facilities/blocks")).map(facilityBlock);
}

export async function createFacilityBlock(input: {
  facility_id: string;
  starts_at: string;
  ends_at: string;
  reason: string;
}): Promise<FacilityBlock> {
  return facilityBlock(
    await apiRequest<unknown>("/api/v1/facilities/blocks", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

export async function cancelFacilityBlock(blockId: string): Promise<FacilityBlock> {
  return facilityBlock(
    await apiRequest<unknown>(`/api/v1/facilities/blocks/${blockId}/cancel`, {
      method: "POST"
    })
  );
}

// Notification administration
export async function listNotificationTemplates(): Promise<NotificationTemplate[]> {
  return list(
    await apiRequest<unknown>("/api/v1/notifications/admin/templates")
  ).map(notificationTemplate);
}

export async function createNotificationTemplate(input: {
  code: string;
  title_template: string;
  body_template: string;
  default_channels: Array<"IN_APP" | "EMAIL">;
  category: string;
  enabled: boolean;
}): Promise<NotificationTemplate> {
  return notificationTemplate(
    await apiRequest<unknown>("/api/v1/notifications/admin/templates", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

export async function listNotificationCampaigns(): Promise<NotificationCampaign[]> {
  return list(
    await apiRequest<unknown>("/api/v1/notifications/admin/campaigns?limit=200")
  ).map(campaign);
}

export async function createNotificationCampaign(input: {
  target: {
    kind: "ROLE" | "SECTION" | "DIRECT";
    role?: "admin" | "teacher" | "student";
    section_id?: string;
    recipients?: Array<{ user_id: string; email?: string }>;
  };
  template_code?: string;
  title?: string;
  body?: string;
  category: string;
  priority: "LOW" | "NORMAL" | "HIGH" | "URGENT";
  channels: Array<"IN_APP" | "EMAIL">;
  data?: Record<string, unknown>;
}): Promise<NotificationCampaign> {
  return campaign(
    await apiRequest<unknown>("/api/v1/notifications/admin/campaigns", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

// Reporting
export async function getReportingOverview(): Promise<ReportingOverview> {
  return reportingOverview(
    await apiRequest<unknown>("/api/v1/reporting/dashboard/overview")
  );
}

export async function getMetricRows(
  metric: "attendance" | "assessments" | "facilities" | "notifications" | "scheduling" | "enrollment"
): Promise<Record<string, unknown>[]> {
  const response = await apiRequest<Record<string, unknown>>(
    `/api/v1/reporting/metrics/${metric}`
  );
  return Array.isArray(response.rows)
    ? response.rows.filter(
        (row): row is Record<string, unknown> =>
          Boolean(row && typeof row === "object" && !Array.isArray(row))
      )
    : [];
}

export async function listReportSnapshots(): Promise<ReportSnapshot[]> {
  return list(await apiRequest<unknown>("/api/v1/reporting/reports/snapshots")).map(snapshot);
}

export async function createReportSnapshot(
  reportType: string,
  filters: Record<string, unknown> = {}
): Promise<ReportSnapshot> {
  return snapshot(
    await apiRequest<unknown>("/api/v1/reporting/reports/snapshots", {
      method: "POST",
      body: JSON.stringify({ report_type: reportType, filters })
    })
  );
}

export async function downloadReportCsv(reportType: string) {
  const result = await apiDownload(`/api/v1/reporting/reports/${reportType}.csv`);
  const url = URL.createObjectURL(result.blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = result.filename ?? `${reportType}-report.csv`;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

// Platform
export async function listPlatformServices(): Promise<ServiceRegistry[]> {
  return list(await apiRequest<unknown>("/api/v1/platform/admin/services")).map(serviceRegistry);
}

export async function runHealthSweep(): Promise<ServiceHealth[]> {
  return list(
    await apiRequest<unknown>("/api/v1/platform/admin/services/health", {
      method: "POST"
    })
  ).map(serviceHealth);
}

export async function upsertPlatformService(
  serviceName: string,
  input: {
    service_name: string;
    base_url: string;
    health_path: string;
    ready_path: string;
    enabled: boolean;
    critical: boolean;
    timeout_seconds: number;
  }
): Promise<ServiceRegistry> {
  return serviceRegistry(
    await apiRequest<unknown>(
      `/api/v1/platform/admin/services/${encodeURIComponent(serviceName)}`,
      {
        method: "PUT",
        body: JSON.stringify(input)
      }
    )
  );
}

export async function listPlatformSettings(): Promise<PlatformSetting[]> {
  return list(await apiRequest<unknown>("/api/v1/platform/admin/settings")).map(setting);
}

export async function upsertPlatformSetting(
  key: string,
  input: {
    value: Record<string, unknown>;
    is_public: boolean;
    description?: string;
  }
): Promise<PlatformSetting> {
  return setting(
    await apiRequest<unknown>(
      `/api/v1/platform/admin/settings/${encodeURIComponent(key)}`,
      {
        method: "PUT",
        body: JSON.stringify(input)
      }
    )
  );
}

export async function listFeatureFlags(): Promise<FeatureFlag[]> {
  return list(await apiRequest<unknown>("/api/v1/platform/features")).map(feature);
}

export async function upsertFeatureFlag(
  key: string,
  input: {
    enabled: boolean;
    config: Record<string, unknown>;
    description?: string;
  }
): Promise<FeatureFlag> {
  return feature(
    await apiRequest<unknown>(
      `/api/v1/platform/admin/features/${encodeURIComponent(key)}`,
      {
        method: "PUT",
        body: JSON.stringify(input)
      }
    )
  );
}

export async function listPlatformJobs(): Promise<PlatformJob[]> {
  return list(await apiRequest<unknown>("/api/v1/platform/admin/jobs")).map(job);
}

export async function createPlatformJob(input: {
  job_type: "IMPORT" | "EXPORT" | "HEALTH_SWEEP" | "REINDEX";
  target_service?: string;
  resource_type?: string;
  parameters?: Record<string, unknown>;
  payload?: Record<string, unknown>;
}): Promise<PlatformJob> {
  return job(
    await apiRequest<unknown>("/api/v1/platform/admin/jobs", {
      method: "POST",
      body: JSON.stringify(input)
    })
  );
}

export async function listAuditEvents(limit = 200): Promise<AuditEvent[]> {
  return list(
    await apiRequest<unknown>(`/api/v1/platform/admin/audit?limit=${limit}`)
  ).map(audit);
}

export async function listSupportTickets(): Promise<SupportTicket[]> {
  return list(await apiRequest<unknown>("/api/v1/platform/support/tickets")).map(ticket);
}

export async function updateSupportTicket(
  ticketId: string,
  input: {
    status?: string;
    priority?: string;
    assigned_to_user_id?: string | null;
  }
): Promise<SupportTicket> {
  return ticket(
    await apiRequest<unknown>(
      `/api/v1/platform/support/tickets/${ticketId}`,
      {
        method: "PATCH",
        body: JSON.stringify(input)
      }
    )
  );
}

export async function addSupportMessage(
  ticketId: string,
  body: string,
  isInternal = false
) {
  return apiRequest(`/api/v1/platform/support/tickets/${ticketId}/messages`, {
    method: "POST",
    body: JSON.stringify({ body, is_internal: isInternal })
  });
}
