export type AdminUser = {
  id: string;
  email: string;
  fullName: string;
  isActive: boolean;
  isVerified: boolean;
  roles: string[];
  createdAt?: string;
};

export type Role = {
  id: string;
  name: string;
  description?: string | null;
  permissions: string[];
};

export type Permission = {
  id: string;
  code: string;
  description?: string | null;
};

export type Department = {
  id: string;
  code: string;
  name: string;
  status?: string;
};

export type Program = {
  id: string;
  code: string;
  name: string;
  departmentId: string;
  status?: string;
};

export type AcademicYear = {
  id: string;
  name: string;
  startsOn: string;
  endsOn: string;
  status?: string;
};

export type Semester = {
  id: string;
  name: string;
  academicYearId: string;
  startsOn: string;
  endsOn: string;
  status?: string;
};

export type Course = {
  id: string;
  code: string;
  title: string;
  departmentId?: string;
  creditHours?: number | null;
  status?: string;
};

export type Section = {
  id: string;
  name: string;
  courseId: string;
  semesterId: string;
  programId?: string;
  capacity?: number | null;
  status?: string;
};

export type StudentProfile = {
  id: string;
  identityUserId: string;
  studentId: string;
  programId?: string;
  batch?: string;
  status?: string;
};

export type TeacherProfile = {
  id: string;
  identityUserId: string;
  employeeId: string;
  departmentId?: string;
  status?: string;
};

export type Enrollment = {
  id: string;
  studentUserId: string;
  sectionId: string;
  status: string;
};

export type TeachingAssignment = {
  id: string;
  teacherUserId: string;
  sectionId: string;
  status?: string;
};

export type Schedule = {
  id: string;
  sectionId: string;
  courseId?: string | null;
  semesterId?: string | null;
  teacherUserId: string;
  roomId?: string | null;
  weekday: number;
  startsAt: string;
  endsAt: string;
  effectiveFrom: string;
  effectiveTo: string;
  timezoneName: string;
  status: string;
  version: number;
};

export type Facility = {
  id: string;
  code: string;
  name: string;
  kind: string;
  building?: string | null;
  floor?: string | null;
  capacity: number;
  isActive: boolean;
  isBookable: boolean;
};

export type Booking = {
  id: string;
  facilityId: string;
  requesterUserId: string;
  purpose: string;
  startsAt: string;
  endsAt: string;
  attendees: number;
  status: string;
  reviewNote?: string | null;
};

export type FacilityBlock = {
  id: string;
  facilityId: string;
  startsAt: string;
  endsAt: string;
  reason: string;
  status: string;
};

export type NotificationTemplate = {
  id: string;
  code: string;
  titleTemplate: string;
  bodyTemplate: string;
  defaultChannels: string[];
  category: string;
  enabled: boolean;
};

export type NotificationCampaign = {
  id: string;
  targetKind: string;
  targetValue: Record<string, unknown>;
  title?: string | null;
  body?: string | null;
  category: string;
  channels: string[];
  status: string;
  recipientCount: number;
  scheduledFor?: string | null;
  expiresAt?: string | null;
  createdAt: string;
};

export type ReportingOverview = {
  activeEnrollments: number;
  attendanceRecords: number;
  attendancePercentage?: number | null;
  gradedAttempts: number;
  assessmentAveragePercent?: number | null;
  assessmentPassRate?: number | null;
  facilityBookings: number;
  approvedFacilityBookings: number;
  notificationDeliveries: number;
  notificationSuccessRate?: number | null;
  scheduleChanges: number;
};

export type ReportSnapshot = {
  id: string;
  reportType: string;
  filters: Record<string, unknown>;
  payload: Record<string, unknown>;
  generatedByUserId: string;
  createdAt: string;
};

export type ServiceRegistry = {
  id: string;
  serviceName: string;
  baseUrl: string;
  healthPath: string;
  readyPath: string;
  enabled: boolean;
  critical: boolean;
  timeoutSeconds: number;
};

export type ServiceHealth = {
  serviceName: string;
  status: string;
  healthOk: boolean;
  readyOk: boolean;
  latencyMs?: number | null;
  detail?: string | null;
};

export type PlatformSetting = {
  key: string;
  value: Record<string, unknown>;
  isPublic: boolean;
  description?: string | null;
  updatedAt: string;
};

export type FeatureFlag = {
  key: string;
  enabled: boolean;
  config: Record<string, unknown>;
  description?: string | null;
  updatedAt: string;
};

export type PlatformJob = {
  id: string;
  jobType: string;
  targetService?: string | null;
  resourceType?: string | null;
  status: string;
  parameters: Record<string, unknown>;
  result: Record<string, unknown>;
  error?: string | null;
  attempts: number;
  createdAt: string;
};

export type SupportTicket = {
  id: string;
  ticketNumber: string;
  createdByUserId: string;
  assignedToUserId?: string | null;
  subject: string;
  description: string;
  category: string;
  priority: string;
  status: string;
  createdAt: string;
  updatedAt: string;
};

export type AuditEvent = {
  id: string;
  sourceService: string;
  actorUserId?: string | null;
  action: string;
  entityType?: string | null;
  entityId?: string | null;
  correlationId?: string | null;
  metadata: Record<string, unknown>;
  occurredAt: string;
};
