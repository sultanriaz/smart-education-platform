import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  cancelBooking,
  createBooking,
  getAssessmentAssignmentDetail,
  getAssessmentAssignments,
  getAssessmentResults,
  getAttendanceRecords,
  getAttendanceSummary,
  getFacilities,
  getMyBookings,
  getMyResources,
  getLearningActivity,
  getMyTimetable,
  getNotificationPreferences,
  getNotifications,
  getRecommendations,
  getUnreadCount,
  markAllNotificationsRead,
  markNotificationRead,
  startAttempt,
  submitAttempt,
  updateNotificationPreferences
} from "./student-api";
import type { NotificationPreferences } from "./types";
import type { AttendanceFilters, NotificationFilters } from "./student-api";

export const studentKeys = {
  attendanceSummary: ["student", "attendance", "summary"] as const,
  attendanceRecords: ["student", "attendance", "records"] as const,
  timetable: ["student", "timetable"] as const,
  resources: ["student", "resources"] as const,
  recommendations: ["student", "recommendations"] as const,
  assignments: ["student", "assessments", "assignments"] as const,
  results: ["student", "assessments", "results"] as const,
  facilities: ["student", "facilities"] as const,
  bookings: ["student", "bookings"] as const,
  notifications: ["student", "notifications"] as const,
  unread: ["student", "notifications", "unread"] as const,
  preferences: ["student", "notifications", "preferences"] as const
};

export const useAttendanceSummary = (filters: AttendanceFilters = {}) =>
  useQuery({ queryKey: [...studentKeys.attendanceSummary, filters], queryFn: () => getAttendanceSummary(filters) });

export const useAttendanceRecords = (filters: AttendanceFilters = {}) =>
  useQuery({ queryKey: [...studentKeys.attendanceRecords, filters], queryFn: () => getAttendanceRecords(filters) });

export const useTimetable = () =>
  useQuery({ queryKey: studentKeys.timetable, queryFn: getMyTimetable });

export const useLearningActivity = (offset=0) =>
  useQuery({ queryKey: ["student","learning","activity",offset], queryFn: () => getLearningActivity(offset) });

export const useResources = () =>
  useQuery({ queryKey: studentKeys.resources, queryFn: getMyResources });

export const useRecommendations = () =>
  useQuery({ queryKey: studentKeys.recommendations, queryFn: getRecommendations });

export const useAssessmentAssignments = () =>
  useQuery({ queryKey: studentKeys.assignments, queryFn: getAssessmentAssignments });

export const useAssessmentResults = () =>
  useQuery({ queryKey: studentKeys.results, queryFn: getAssessmentResults });

export const useAssessmentAssignmentDetail = (assignmentId: string) =>
  useQuery({
    queryKey: ["student", "assessments", "assignment", assignmentId],
    queryFn: () => getAssessmentAssignmentDetail(assignmentId),
    enabled: Boolean(assignmentId)
  });

export const useStartAttempt = () =>
  useMutation({ mutationFn: startAttempt });

export const useSubmitAttempt = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: submitAttempt,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: studentKeys.assignments });
      await queryClient.invalidateQueries({ queryKey: studentKeys.results });
    }
  });
};

export const useFacilities = () =>
  useQuery({ queryKey: studentKeys.facilities, queryFn: getFacilities });

export const useBookings = () =>
  useQuery({ queryKey: studentKeys.bookings, queryFn: getMyBookings });

export const useCreateBooking = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createBooking,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: studentKeys.bookings })
  });
};

export const useCancelBooking = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: cancelBooking,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: studentKeys.bookings })
  });
};

export const useNotifications = (filters: NotificationFilters = {}) =>
  useQuery({ queryKey: [...studentKeys.notifications, filters], queryFn: () => getNotifications(filters) });

export const useUnreadCount = () =>
  useQuery({ queryKey: studentKeys.unread, queryFn: getUnreadCount, refetchInterval: 4_000, refetchIntervalInBackground: false });

export const useNotificationPreferences = () =>
  useQuery({ queryKey: studentKeys.preferences, queryFn: getNotificationPreferences });

export const useMarkNotificationRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: markNotificationRead,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: studentKeys.notifications });
      await queryClient.invalidateQueries({ queryKey: studentKeys.unread });
    }
  });
};

export const useMarkAllNotificationsRead = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: markAllNotificationsRead,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: studentKeys.notifications });
      await queryClient.invalidateQueries({ queryKey: studentKeys.unread });
    }
  });
};

export const useUpdateNotificationPreferences = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: NotificationPreferences) =>
      updateNotificationPreferences(input),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: studentKeys.preferences })
  });
};
