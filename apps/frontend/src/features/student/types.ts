export type AttendanceStatus = "PRESENT" | "ABSENT" | "LATE" | "EXCUSED" | string;

export type AttendanceSummary = {
  present: number;
  absent: number;
  late: number;
  excused: number;
  totalConsidered: number;
  percentage: number;
};

export type AttendanceRecord = {
  id: string;
  sessionId?: string;
  sectionId?: string;
  courseId?: string;
  courseLabel?: string;
  sessionDate?: string;
  status: AttendanceStatus;
  notes?: string | null;
};

export type TimetableItem = {
  id: string;
  title: string;
  sectionId?: string;
  courseId?: string;
  roomLabel?: string;
  startsAt: string;
  endsAt: string;
  status?: string;
};

export type LearningResource = {
  id: string;
  title: string;
  description?: string | null;
  resourceType?: string;
  courseId?: string;
  sectionId?: string;
  publishedAt?: string | null;
  downloadPath?: string | null;
  externalUrl?: string | null;
  textContent?: string | null;
  score?: number | null;
  reason?: string | null;
};

export type AssessmentAssignment = {
  id: string;
  quizId: string;
  title: string;
  description?: string | null;
  sectionId?: string;
  opensAt: string;
  dueAt: string;
  attemptLimit: number;
  attemptsUsed?: number;
  activeAttemptId?: string;
  status?: string;
};

export type AssessmentChoice = {
  id: string;
  text: string;
};

export type AssessmentQuestion = {
  id: string;
  prompt: string;
  questionType: "MCQ_SINGLE" | "TRUE_FALSE" | "SHORT_TEXT" | string;
  points: number;
  choices: AssessmentChoice[];
};

export type AssessmentAssignmentDetail = AssessmentAssignment & {
  durationMinutes?: number | null;
  questions: AssessmentQuestion[];
};

export type AssessmentAttempt = {
  id: string;
  assignmentId: string;
  status: string;
  attemptNumber?: number;
  expiresAt?: string | null;
  serverTime?: string | null;
  answers?: { questionId: string; selectedChoiceId?: string; textAnswer?: string }[];
};

export type AssessmentResult = {
  attemptId: string;
  assignmentId?: string;
  quizId?: string;
  title?: string;
  score?: number | null;
  reason?: string | null;
  maxScore?: number | null;
  percent?: number | null;
  passed?: boolean | null;
  status: string;
  submittedAt?: string | null;
  gradedAt?: string | null;
};

export type Facility = {
  id: string;
  name: string;
  code?: string;
  facilityType?: string;
  building?: string | null;
  floor?: string | null;
  capacity?: number | null;
  isBookable: boolean;
};

export type Booking = {
  id: string;
  facilityId: string;
  facilityName?: string;
  startsAt: string;
  endsAt: string;
  purpose?: string | null;
  status: string;
};

export type NotificationItem = {
  id: string;
  title: string;
  message: string;
  category?: string | null;
  readAt?: string | null;
  createdAt: string;
};

export type NotificationPreferences = {
  emailEnabled?: boolean;
  inAppEnabled?: boolean;
  mutedCategories?: string[];
};
