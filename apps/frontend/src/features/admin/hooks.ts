import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as api from "./admin-api";

export const adminKeys = {
  users: ["admin", "identity", "users"] as const,
  roles: ["admin", "identity", "roles"] as const,
  permissions: ["admin", "identity", "permissions"] as const,

  campuses: ["admin", "academic", "campuses"] as const,
  departments: ["admin", "academic", "departments"] as const,
  programs: ["admin", "academic", "programs"] as const,
  years: ["admin", "academic", "years"] as const,
  semesters: ["admin", "academic", "semesters"] as const,
  courses: ["admin", "academic", "courses"] as const,
  sections: ["admin", "academic", "sections"] as const,
  studentProfiles: ["admin", "academic", "student-profiles"] as const,
  teacherProfiles: ["admin", "academic", "teacher-profiles"] as const,
  enrollments: ["admin", "academic", "enrollments"] as const,
  teachingAssignments: ["admin", "academic", "teaching-assignments"] as const,

  schedules: ["admin", "scheduling", "schedules"] as const,

  equipment: ["admin", "facilities", "equipment"] as const,
  facilities: ["admin", "facilities", "facilities"] as const,
  bookings: ["admin", "facilities", "bookings"] as const,
  blocks: ["admin", "facilities", "blocks"] as const,

  templates: ["admin", "notifications", "templates"] as const,
  campaigns: ["admin", "notifications", "campaigns"] as const,

  reportingOverview: ["admin", "reporting", "overview"] as const,
  snapshots: ["admin", "reporting", "snapshots"] as const,

  services: ["admin", "platform", "services"] as const,
  settings: ["admin", "platform", "settings"] as const,
  features: ["admin", "platform", "features"] as const,
  jobs: ["admin", "platform", "jobs"] as const,
  tickets: ["admin", "platform", "tickets"] as const,
  audit: ["admin", "platform", "audit"] as const
};

export const useAdminUsers = () =>
  useQuery({ queryKey: adminKeys.users, queryFn: api.listUsers });
export const useAdminRoles = () =>
  useQuery({ queryKey: adminKeys.roles, queryFn: api.listRoles });
export const useAdminPermissions = () =>
  useQuery({ queryKey: adminKeys.permissions, queryFn: api.listPermissions });

export const useCampuses = () =>
  useQuery({ queryKey: adminKeys.campuses, queryFn: api.listCampuses });
export const useDepartments = () =>
  useQuery({ queryKey: adminKeys.departments, queryFn: api.listDepartments });
export const usePrograms = () =>
  useQuery({ queryKey: adminKeys.programs, queryFn: api.listPrograms });
export const useAcademicYears = () =>
  useQuery({ queryKey: adminKeys.years, queryFn: api.listAcademicYears });
export const useSemesters = () =>
  useQuery({ queryKey: adminKeys.semesters, queryFn: api.listSemesters });
export const useCourses = () =>
  useQuery({ queryKey: adminKeys.courses, queryFn: api.listCourses });
export const useSections = () =>
  useQuery({ queryKey: adminKeys.sections, queryFn: api.listSections });
export const useStudentProfiles = () =>
  useQuery({ queryKey: adminKeys.studentProfiles, queryFn: api.listStudentProfiles });
export const useTeacherProfiles = () =>
  useQuery({ queryKey: adminKeys.teacherProfiles, queryFn: api.listTeacherProfiles });
export const useEnrollments = () =>
  useQuery({ queryKey: adminKeys.enrollments, queryFn: api.listEnrollments });
export const useTeachingAssignments = () =>
  useQuery({ queryKey: adminKeys.teachingAssignments, queryFn: api.listTeachingAssignments });

export const useSchedules = () =>
  useQuery({ queryKey: adminKeys.schedules, queryFn: api.listSchedules });

export const useEquipment = () =>
  useQuery({ queryKey: adminKeys.equipment, queryFn: api.listEquipment });
export const useAdminFacilities = () =>
  useQuery({ queryKey: adminKeys.facilities, queryFn: api.listFacilities });
export const useAdminBookings = () =>
  useQuery({ queryKey: adminKeys.bookings, queryFn: () => api.listBookings() });
export const useFacilityBlocks = () =>
  useQuery({ queryKey: adminKeys.blocks, queryFn: api.listFacilityBlocks });

export const useNotificationTemplates = () =>
  useQuery({ queryKey: adminKeys.templates, queryFn: api.listNotificationTemplates });
export const useNotificationCampaigns = () =>
  useQuery({ queryKey: adminKeys.campaigns, queryFn: api.listNotificationCampaigns });

export const useReportingOverview = () =>
  useQuery({ queryKey: adminKeys.reportingOverview, queryFn: api.getReportingOverview });
export const useReportSnapshots = () =>
  useQuery({ queryKey: adminKeys.snapshots, queryFn: api.listReportSnapshots });

export const usePlatformServices = () =>
  useQuery({ queryKey: adminKeys.services, queryFn: api.listPlatformServices });
export const usePlatformSettings = () =>
  useQuery({ queryKey: adminKeys.settings, queryFn: api.listPlatformSettings });
export const useFeatureFlags = () =>
  useQuery({ queryKey: adminKeys.features, queryFn: api.listFeatureFlags });
export const usePlatformJobs = () =>
  useQuery({ queryKey: adminKeys.jobs, queryFn: api.listPlatformJobs });
export const useSupportTickets = () =>
  useQuery({ queryKey: adminKeys.tickets, queryFn: api.listSupportTickets });
export const useAuditEvents = () =>
  useQuery({ queryKey: adminKeys.audit, queryFn: () => api.listAuditEvents(200) });

export function useAdminMutation<TVariables, TResult>(
  mutationFn: (variables: TVariables) => Promise<TResult>,
  invalidate: readonly unknown[]
) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: invalidate });
    }
  });
}
