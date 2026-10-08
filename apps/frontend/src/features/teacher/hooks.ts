import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { AttendanceEntry } from "./types";
import {
  addLearningContentVersion,
  addQuestionToQuiz,
  archiveLearningResource,
  assignQuiz,
  cancelTeacherBooking,
  createAttendanceSession,
  createLearningResource,
  createQuestion,
  createQuestionBank,
  createQuiz,
  createTeacherAnnouncement,
  createTeacherBooking,
  finalizeAttendanceSession,
  getAssignmentAttempts,
  getSectionAttendanceSessions,
  getSectionRoster,
  getSessionAttendance,
  getTeacherAnnouncements,
  getTeacherAssignments,
  getTeacherBanks,
  getTeacherBookings,
  getTeacherFacilities,
  getTeacherQuestions,
  getTeacherQuizzes,
  getTeacherResources,
  getTeacherSections,
  getTeacherTimetable,
  gradeAttempt,
  publishLearningResource,
  publishQuiz,
  saveBulkAttendance,
  uploadLearningFile
} from "./teacher-api";

export const teacherKeys = {
  sections: ["teacher", "sections"] as const,
  timetable: ["teacher", "timetable"] as const,
  resources: ["teacher", "learning", "resources"] as const,
  banks: ["teacher", "assessment", "banks"] as const,
  questions: ["teacher", "assessment", "questions"] as const,
  quizzes: ["teacher", "assessment", "quizzes"] as const,
  assignments: ["teacher", "assessment", "assignments"] as const,
  facilities: ["teacher", "facilities"] as const,
  bookings: ["teacher", "bookings"] as const,
  announcements: ["teacher", "announcements"] as const
};

export const useTeacherSections = () =>
  useQuery({ queryKey: teacherKeys.sections, queryFn: getTeacherSections });

export const useSectionRoster = (sectionId: string) =>
  useQuery({
    queryKey: ["teacher", "sections", sectionId, "roster"],
    queryFn: () => getSectionRoster(sectionId),
    enabled: Boolean(sectionId)
  });

export const useAttendanceSessions = (sectionId: string) =>
  useQuery({
    queryKey: ["teacher", "attendance", "sessions", sectionId],
    queryFn: () => getSectionAttendanceSessions(sectionId),
    enabled: Boolean(sectionId)
  });

export const useSessionAttendance = (sessionId: string) =>
  useQuery({
    queryKey: ["teacher", "attendance", "session", sessionId],
    queryFn: () => getSessionAttendance(sessionId),
    enabled: Boolean(sessionId)
  });

export const useCreateAttendanceSession = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createAttendanceSession,
    onSuccess: async (session) => {
      await qc.invalidateQueries({
        queryKey: ["teacher", "attendance", "sessions", session.sectionId]
      });
    }
  });
};

export const useSaveBulkAttendance = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      sessionId,
      records
    }: {
      sessionId: string;
      records: AttendanceEntry[];
    }) => saveBulkAttendance(sessionId, records),
    onSuccess: async (_data, vars) => {
      await qc.invalidateQueries({
        queryKey: ["teacher", "attendance", "session", vars.sessionId]
      });
    }
  });
};

export const useFinalizeAttendanceSession = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: finalizeAttendanceSession,
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["teacher", "attendance"] });
    }
  });
};

export const useTeacherTimetable = () =>
  useQuery({ queryKey: teacherKeys.timetable, queryFn: () => getTeacherTimetable() });

export const useTeacherResources = () =>
  useQuery({ queryKey: teacherKeys.resources, queryFn: getTeacherResources });

export const useCreateLearningResource = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createLearningResource,
    onSuccess: () => qc.invalidateQueries({ queryKey: teacherKeys.resources })
  });
};

export const useAddLearningContentVersion = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      resourceId,
      input
    }: {
      resourceId: string;
      input: Parameters<typeof addLearningContentVersion>[1];
    }) => addLearningContentVersion(resourceId, input),
    onSuccess: () => qc.invalidateQueries({ queryKey: teacherKeys.resources })
  });
};

export const useUploadLearningFile = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      resourceId,
      file,
      changeNote
    }: {
      resourceId: string;
      file: File;
      changeNote?: string;
    }) => uploadLearningFile(resourceId, file, changeNote),
    onSuccess: () => qc.invalidateQueries({ queryKey: teacherKeys.resources })
  });
};

export const usePublishLearningResource = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: publishLearningResource,
    onSuccess: () => qc.invalidateQueries({ queryKey: teacherKeys.resources })
  });
};

export const useArchiveLearningResource = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: archiveLearningResource,
    onSuccess: () => qc.invalidateQueries({ queryKey: teacherKeys.resources })
  });
};

export const useTeacherBanks = () =>
  useQuery({ queryKey: teacherKeys.banks, queryFn: getTeacherBanks });

export const useTeacherQuestions = (bankId?: string) =>
  useQuery({
    queryKey: [...teacherKeys.questions, bankId ?? "all"],
    queryFn: () => getTeacherQuestions(bankId)
  });

export const useTeacherQuizzes = () =>
  useQuery({ queryKey: teacherKeys.quizzes, queryFn: getTeacherQuizzes });

export const useTeacherAssignments = () =>
  useQuery({ queryKey: teacherKeys.assignments, queryFn: getTeacherAssignments });

export const useAssignmentAttempts = (assignmentId: string) =>
  useQuery({
    queryKey: ["teacher", "assessment", "assignment", assignmentId, "attempts"],
    queryFn: () => getAssignmentAttempts(assignmentId),
    enabled: Boolean(assignmentId)
  });

export const useCreateQuestionBank = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createQuestionBank,
    onSuccess: () => qc.invalidateQueries({ queryKey: teacherKeys.banks })
  });
};

export const useCreateQuestion = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createQuestion,
    onSuccess: () => qc.invalidateQueries({ queryKey: teacherKeys.questions })
  });
};

export const useCreateQuiz = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createQuiz,
    onSuccess: () => qc.invalidateQueries({ queryKey: teacherKeys.quizzes })
  });
};

export const useAddQuestionToQuiz = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      quizId,
      input
    }: {
      quizId: string;
      input: Parameters<typeof addQuestionToQuiz>[1];
    }) => addQuestionToQuiz(quizId, input),
    onSuccess: () => qc.invalidateQueries({ queryKey: teacherKeys.quizzes })
  });
};

export const usePublishQuiz = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: publishQuiz,
    onSuccess: () => qc.invalidateQueries({ queryKey: teacherKeys.quizzes })
  });
};

export const useAssignQuiz = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      quizId,
      input
    }: {
      quizId: string;
      input: Parameters<typeof assignQuiz>[1];
    }) => assignQuiz(quizId, input),
    onSuccess: () => qc.invalidateQueries({ queryKey: teacherKeys.assignments })
  });
};

export const useGradeAttempt = (assignmentId: string) => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: gradeAttempt,
    onSuccess: async () => {
      await qc.invalidateQueries({
        queryKey: ["teacher", "assessment", "assignment", assignmentId, "attempts"]
      });
    }
  });
};

export const useTeacherFacilities = () =>
  useQuery({ queryKey: teacherKeys.facilities, queryFn: getTeacherFacilities });

export const useTeacherBookings = () =>
  useQuery({ queryKey: teacherKeys.bookings, queryFn: getTeacherBookings });

export const useCreateTeacherBooking = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createTeacherBooking,
    onSuccess: () => qc.invalidateQueries({ queryKey: teacherKeys.bookings })
  });
};

export const useCancelTeacherBooking = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ bookingId, reason }: { bookingId: string; reason: string }) =>
      cancelTeacherBooking(bookingId, reason),
    onSuccess: () => qc.invalidateQueries({ queryKey: teacherKeys.bookings })
  });
};

export const useTeacherAnnouncements = () =>
  useQuery({ queryKey: teacherKeys.announcements, queryFn: getTeacherAnnouncements });

export const useCreateTeacherAnnouncement = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createTeacherAnnouncement,
    onSuccess: () => qc.invalidateQueries({ queryKey: teacherKeys.announcements })
  });
};
