export type TeacherSection = {
  id: string;
  name: string;
  courseId?: string;
  courseCode?: string;
  courseTitle?: string;
  semesterId?: string;
  capacity?: number | null;
};

export type RosterMember = {
  userId: string;
  studentId?: string;
  name?: string;
  email?: string;
  enrollmentStatus?: string;
};

export type AttendanceSession = {
  id: string;
  sectionId: string;
  sessionDate: string;
  startsAt?: string | null;
  endsAt?: string | null;
  status: string;
  locked?: boolean;
};

export type AttendanceEntry = {
  id?: string;
  studentUserId: string;
  studentName?: string;
  status: "PRESENT" | "ABSENT" | "LATE" | "EXCUSED";
  notes?: string | null;
};

export type TeacherTimetableItem = {
  id: string;
  sectionId: string;
  courseId?: string;
  roomId?: string | null;
  startsAt: string;
  endsAt: string;
  date: string;
  title: string;
  source?: string;
};

export type LearningTarget = {
  target_type: "SECTION" | "COURSE";
  target_id: string;
};

export type LearningVersion = {
  id: string;
  versionNumber: number;
  textContent?: string | null;
  externalUrl?: string | null;
  originalFilename?: string | null;
  changeNote?: string | null;
  createdAt?: string;
};

export type TeacherLearningResource = {
  id: string;
  title: string;
  description?: string | null;
  resourceType: "FILE" | "LINK" | "VIDEO" | "NOTE" | string;
  status: string;
  categoryId?: string | null;
  tags: string[];
  targets: LearningTarget[];
  versions: LearningVersion[];
  createdAt?: string;
  updatedAt?: string;
};

export type QuestionBank = {
  id: string;
  name: string;
  courseId?: string | null;
};

export type QuestionChoice = {
  id: string;
  text: string;
  isCorrect?: boolean;
};

export type TeacherQuestion = {
  id: string;
  bankId: string;
  questionType: "MCQ_SINGLE" | "TRUE_FALSE" | "SHORT_TEXT" | string;
  prompt: string;
  points: number;
  correctText?: string | null;
  explanation?: string | null;
  choices: QuestionChoice[];
};

export type TeacherQuiz = {
  id: string;
  title: string;
  description?: string | null;
  courseId: string;
  status: string;
  durationMinutes?: number | null;
  passPercent: number;
  questionCount?: number;
};

export type TeacherAssignment = {
  id: string;
  quizId: string;
  quizTitle?: string;
  sectionId: string;
  opensAt: string;
  dueAt: string;
  attemptLimit: number;
};

export type TeacherAttemptAnswer = {
  id: string;
  questionId: string;
  prompt?: string;
  questionType?: string;
  points?: number;
  textAnswer?: string | null;
  selectedChoiceId?: string | null;
  autoScore?: number | null;
  manualScore?: number | null;
  feedback?: string | null;
};

export type TeacherAttempt = {
  id: string;
  assignmentId: string;
  studentUserId: string;
  attemptNumber: number;
  status: string;
  score?: number | null;
  maxScore?: number | null;
  percent?: number | null;
  passed?: boolean | null;
  startedAt: string;
  submittedAt?: string | null;
  gradedAt?: string | null;
  answers: TeacherAttemptAnswer[];
};

export type TeacherFacility = {
  id: string;
  name: string;
  code?: string;
  type?: string;
  capacity?: number | null;
  building?: string | null;
  isBookable: boolean;
};

export type TeacherBooking = {
  id: string;
  facilityId: string;
  purpose: string;
  startsAt: string;
  endsAt: string;
  attendees: number;
  status: string;
};

export type TeacherAnnouncement = {
  id: string;
  sectionId?: string;
  title: string;
  body: string;
  category?: string;
  channels: string[];
  recipientCount: number;
  status: string;
  createdAt: string;
};
