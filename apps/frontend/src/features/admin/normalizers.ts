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

export const record = (value: unknown): Record<string, unknown> =>
  value && typeof value === "object" && !Array.isArray(value)
    ? (value as Record<string, unknown>)
    : {};

export function list(value: unknown): unknown[] {
  if (Array.isArray(value)) return value;
  const r = record(value);
  for (const key of [
    "items", "results", "data", "rows", "users", "roles", "permissions",
    "departments", "programs", "academic_years", "semesters", "courses",
    "sections", "enrollments", "assignments", "bookings", "facilities",
    "templates", "campaigns", "snapshots", "services", "jobs", "tickets"
  ]) {
    if (Array.isArray(r[key])) return r[key] as unknown[];
  }
  return [];
}

const s = (value: unknown, fallback = "") =>
  typeof value === "string" ? value : fallback;
const n = (value: unknown, fallback = 0) =>
  typeof value === "number" && Number.isFinite(value) ? value : fallback;
const b = (value: unknown, fallback = false) =>
  typeof value === "boolean" ? value : fallback;
const ns = (value: unknown) => (typeof value === "string" ? value : null);
const stringArray = (value: unknown) =>
  Array.isArray(value) ? value.filter((x): x is string => typeof x === "string") : [];

export function user(value: unknown): AdminUser {
  const r = record(value);
  return {
    id: s(r.id),
    email: s(r.email),
    fullName: s(r.full_name ?? r.fullName ?? r.name),
    isActive: b(r.is_active ?? r.isActive, true),
    isVerified: b(r.is_verified ?? r.isVerified, false),
    roles: Array.isArray(r.roles)
      ? r.roles.map((role) =>
          typeof role === "string" ? role : s(record(role).name)
        ).filter(Boolean)
      : [],
    createdAt: s(r.created_at ?? r.createdAt) || undefined
  };
}

export function role(value: unknown): Role {
  const r = record(value);
  return {
    id: s(r.id),
    name: s(r.name),
    description: ns(r.description),
    permissions: Array.isArray(r.permissions)
      ? r.permissions.map((permission) =>
          typeof permission === "string" ? permission : s(record(permission).code)
        ).filter(Boolean)
      : []
  };
}

export function permission(value: unknown): Permission {
  const r = record(value);
  return { id: s(r.id), code: s(r.code), description: ns(r.description) };
}

export function department(value: unknown): Department {
  const r = record(value);
  return { id: s(r.id), code: s(r.code), name: s(r.name), status: s(r.status) || undefined };
}

export function program(value: unknown): Program {
  const r = record(value);
  return {
    id: s(r.id),
    code: s(r.code),
    name: s(r.name),
    departmentId: s(r.department_id),
    status: s(r.status) || undefined
  };
}

export function academicYear(value: unknown): AcademicYear {
  const r = record(value);
  return {
    id: s(r.id),
    name: s(r.name ?? r.label),
    startsOn: s(r.starts_on ?? r.start_date),
    endsOn: s(r.ends_on ?? r.end_date),
    status: s(r.status) || undefined
  };
}

export function semester(value: unknown): Semester {
  const r = record(value);
  return {
    id: s(r.id),
    name: s(r.name),
    academicYearId: s(r.academic_year_id),
    startsOn: s(r.starts_on ?? r.start_date),
    endsOn: s(r.ends_on ?? r.end_date),
    status: s(r.status) || undefined
  };
}

export function course(value: unknown): Course {
  const r = record(value);
  return {
    id: s(r.id),
    code: s(r.code),
    title: s(r.title ?? r.name),
    departmentId: s(r.department_id) || undefined,
    creditHours: typeof (r.credits ?? r.credit_hours) === "number" ? Number(r.credits ?? r.credit_hours) : null,
    status: s(r.status) || undefined
  };
}

export function section(value: unknown): Section {
  const r = record(value);
  return {
    id: s(r.id),
    name: s(r.name ?? r.code),
    courseId: s(r.course_id),
    semesterId: s(r.semester_id),
    programId: s(r.program_id) || undefined,
    capacity: typeof r.capacity === "number" ? r.capacity : null,
    status: s(r.status) || undefined
  };
}

export function studentProfile(value: unknown): StudentProfile {
  const r = record(value);
  return {
    id: s(r.id),
    identityUserId: s(r.external_user_id ?? r.identity_user_id ?? r.user_id),
    studentId: s(r.student_number ?? r.student_id ?? r.registration_number),
    programId: s(r.program_id) || undefined,
    batch: s(r.batch ?? r.cohort) || undefined,
    status: s(r.status) || undefined
  };
}

export function teacherProfile(value: unknown): TeacherProfile {
  const r = record(value);
  return {
    id: s(r.id),
    identityUserId: s(r.external_user_id ?? r.identity_user_id ?? r.user_id),
    employeeId: s(r.employee_number ?? r.employee_id ?? r.staff_id),
    departmentId: s(r.department_id) || undefined,
    status: s(r.status) || undefined
  };
}

export function enrollment(value: unknown): Enrollment {
  const r = record(value);
  return {
    id: s(r.id),
    studentUserId: s(r.student_profile_id ?? r.student_user_id ?? r.external_user_id ?? r.identity_user_id ?? r.user_id),
    sectionId: s(r.section_id),
    status: s(r.status, "ACTIVE")
  };
}

export function teachingAssignment(value: unknown): TeachingAssignment {
  const r = record(value);
  return {
    id: s(r.id),
    teacherUserId: s(r.teacher_profile_id ?? r.teacher_user_id ?? r.external_user_id ?? r.identity_user_id ?? r.user_id),
    sectionId: s(r.section_id),
    status: s(r.status) || undefined
  };
}

export function schedule(value: unknown): Schedule {
  const r = record(value);
  return {
    id: s(r.id),
    sectionId: s(r.section_id),
    courseId: ns(r.course_id),
    semesterId: ns(r.semester_id),
    teacherUserId: s(r.teacher_user_id),
    roomId: ns(r.room_id),
    weekday: n(r.weekday),
    startsAt: s(r.starts_at),
    endsAt: s(r.ends_at),
    effectiveFrom: s(r.effective_from),
    effectiveTo: s(r.effective_to),
    timezoneName: s(r.timezone_name),
    status: s(r.status),
    version: n(r.version)
  };
}

export function facility(value: unknown): Facility {
  const r = record(value);
  return {
    id: s(r.id),
    code: s(r.code),
    name: s(r.name),
    kind: s(r.kind ?? r.facility_type),
    building: ns(r.building),
    floor: ns(r.floor),
    capacity: n(r.capacity),
    isActive: b(r.is_active, true),
    isBookable: b(r.is_bookable, true)
  };
}

export function booking(value: unknown): Booking {
  const r = record(value);
  return {
    id: s(r.id),
    facilityId: s(r.facility_id),
    requesterUserId: s(r.requester_user_id),
    purpose: s(r.purpose),
    startsAt: s(r.starts_at),
    endsAt: s(r.ends_at),
    attendees: n(r.attendees),
    status: s(r.status),
    reviewNote: ns(r.review_note)
  };
}

export function facilityBlock(value: unknown): FacilityBlock {
  const r = record(value);
  return {
    id: s(r.id),
    facilityId: s(r.facility_id),
    startsAt: s(r.starts_at),
    endsAt: s(r.ends_at),
    reason: s(r.reason),
    status: s(r.status)
  };
}

export function notificationTemplate(value: unknown): NotificationTemplate {
  const r = record(value);
  return {
    id: s(r.id),
    code: s(r.code),
    titleTemplate: s(r.title_template),
    bodyTemplate: s(r.body_template),
    defaultChannels: stringArray(r.default_channels),
    category: s(r.category),
    enabled: b(r.enabled)
  };
}

export function campaign(value: unknown): NotificationCampaign {
  const r = record(value);
  return {
    id: s(r.id),
    targetKind: s(r.target_kind),
    targetValue: record(r.target_value),
    title: ns(r.title),
    body: ns(r.body),
    category: s(r.category),
    channels: stringArray(r.channels),
    status: s(r.status),
    recipientCount: n(r.recipient_count),
    scheduledFor: ns(r.scheduled_for),
    expiresAt: ns(r.expires_at),
    createdAt: s(r.created_at)
  };
}

export function reportingOverview(value: unknown): ReportingOverview {
  const r = record(value);
  return {
    activeEnrollments: n(r.active_enrollments),
    attendanceRecords: n(r.attendance_records),
    attendancePercentage: typeof r.attendance_percentage === "number" ? r.attendance_percentage : null,
    gradedAttempts: n(r.graded_attempts),
    assessmentAveragePercent: typeof r.assessment_average_percent === "number" ? r.assessment_average_percent : null,
    assessmentPassRate: typeof r.assessment_pass_rate === "number" ? r.assessment_pass_rate : null,
    facilityBookings: n(r.facility_bookings),
    approvedFacilityBookings: n(r.approved_facility_bookings),
    notificationDeliveries: n(r.notification_deliveries),
    notificationSuccessRate: typeof r.notification_success_rate === "number" ? r.notification_success_rate : null,
    scheduleChanges: n(r.schedule_changes)
  };
}

export function snapshot(value: unknown): ReportSnapshot {
  const r = record(value);
  return {
    id: s(r.id),
    reportType: s(r.report_type),
    filters: record(r.filters),
    payload: record(r.payload),
    generatedByUserId: s(r.generated_by_user_id),
    createdAt: s(r.created_at)
  };
}

export function serviceRegistry(value: unknown): ServiceRegistry {
  const r = record(value);
  return {
    id: s(r.id),
    serviceName: s(r.service_name),
    baseUrl: s(r.base_url),
    healthPath: s(r.health_path, "/health"),
    readyPath: s(r.ready_path, "/ready"),
    enabled: b(r.enabled, true),
    critical: b(r.critical, false),
    timeoutSeconds: n(r.timeout_seconds, 3)
  };
}

export function serviceHealth(value: unknown): ServiceHealth {
  const r = record(value);
  return {
    serviceName: s(r.service_name),
    status: s(r.status),
    healthOk: b(r.health_ok),
    readyOk: b(r.ready_ok),
    latencyMs: typeof r.latency_ms === "number" ? r.latency_ms : null,
    detail: ns(r.detail)
  };
}

export function setting(value: unknown): PlatformSetting {
  const r = record(value);
  return {
    key: s(r.key),
    value: record(r.value),
    isPublic: b(r.is_public),
    description: ns(r.description),
    updatedAt: s(r.updated_at)
  };
}

export function feature(value: unknown): FeatureFlag {
  const r = record(value);
  return {
    key: s(r.key),
    enabled: b(r.enabled),
    config: record(r.config),
    description: ns(r.description),
    updatedAt: s(r.updated_at)
  };
}

export function job(value: unknown): PlatformJob {
  const r = record(value);
  return {
    id: s(r.id),
    jobType: s(r.job_type),
    targetService: ns(r.target_service),
    resourceType: ns(r.resource_type),
    status: s(r.status),
    parameters: record(r.parameters),
    result: record(r.result),
    error: ns(r.error),
    attempts: n(r.attempts),
    createdAt: s(r.created_at)
  };
}

export function ticket(value: unknown): SupportTicket {
  const r = record(value);
  return {
    id: s(r.id),
    ticketNumber: s(r.ticket_number),
    createdByUserId: s(r.created_by_user_id),
    assignedToUserId: ns(r.assigned_to_user_id),
    subject: s(r.subject),
    description: s(r.description),
    category: s(r.category),
    priority: s(r.priority),
    status: s(r.status),
    createdAt: s(r.created_at),
    updatedAt: s(r.updated_at)
  };
}

export function audit(value: unknown): AuditEvent {
  const r = record(value);
  return {
    id: s(r.id),
    sourceService: s(r.source_service),
    actorUserId: ns(r.actor_user_id),
    action: s(r.action),
    entityType: ns(r.entity_type),
    entityId: ns(r.entity_id),
    correlationId: ns(r.correlation_id),
    metadata: record(r.metadata),
    occurredAt: s(r.occurred_at)
  };
}
