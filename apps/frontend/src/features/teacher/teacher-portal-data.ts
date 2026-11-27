export interface FacultyClassRosterStudent {
  studentId: string;
  rollNo: string;
  name: string;
  email: string;
}

export interface FacultyClassInfo {
  id: string;
  courseCode: string;
  courseTitle: string;
  section: string;
  room: string;
  scheduleSummary: string;
  students: FacultyClassRosterStudent[];
}

export interface ClassAttendanceSlotOption {
  slot: string;
  timeRange: string;
}

export const FACULTY_TIME_SLOTS: ClassAttendanceSlotOption[] = [
  { slot: "Slot 1", timeRange: "08:30 AM – 10:00 AM" },
  { slot: "Slot 2", timeRange: "10:15 AM – 11:45 AM" },
  { slot: "Slot 3", timeRange: "12:00 PM – 01:30 PM" },
  { slot: "Slot 4", timeRange: "02:00 PM – 03:30 PM" },
  { slot: "Slot 5", timeRange: "03:45 PM – 05:15 PM" }
];

const BCS_7C_STUDENTS: FacultyClassRosterStudent[] = [
  { studentId: "stu-7c-101", rollNo: "SP23-BCS-101", name: "Hamza Tariq", email: "sp23-bcs-101@cuisahiwal.edu.pk" },
  { studentId: "stu-7c-112", rollNo: "SP23-BCS-112", name: "Ayesha Siddiqa", email: "sp23-bcs-112@cuisahiwal.edu.pk" },
  { studentId: "stu-7c-118", rollNo: "SP23-BCS-118", name: "Bilal Ahmed Raza", email: "sp23-bcs-118@cuisahiwal.edu.pk" },
  { studentId: "stu-7c-124", rollNo: "SP23-BCS-124", name: "Fatima Noor", email: "sp23-bcs-124@cuisahiwal.edu.pk" },
  { studentId: "stu-7c-131", rollNo: "SP23-BCS-131", name: "Usman Ghani", email: "sp23-bcs-131@cuisahiwal.edu.pk" },
  { studentId: "stu-7c-139", rollNo: "SP23-BCS-139", name: "Zainab Khalid", email: "sp23-bcs-139@cuisahiwal.edu.pk" },
  { studentId: "stu-7c-145", rollNo: "SP23-BCS-145", name: "Muhammad Saad", email: "sp23-bcs-145@cuisahiwal.edu.pk" },
  { studentId: "stu-7c-155", rollNo: "SP23-BCS-155", name: "Hira Mansoor", email: "sp23-bcs-155@cuisahiwal.edu.pk" },
  { studentId: "stu-7c-162", rollNo: "SP23-BCS-162", name: "Daniyal Farooq", email: "sp23-bcs-162@cuisahiwal.edu.pk" },
  { studentId: "stu-7c-170", rollNo: "SP23-BCS-170", name: "Maryam Nawazish", email: "sp23-bcs-170@cuisahiwal.edu.pk" }
];

const BCS_7A_STUDENTS: FacultyClassRosterStudent[] = [
  { studentId: "stu-7a-004", rollNo: "SP23-BCS-004", name: "Ali Hassan Bajwa", email: "sp23-bcs-004@cuisahiwal.edu.pk" },
  { studentId: "stu-7a-011", rollNo: "SP23-BCS-011", name: "Maham Javed", email: "sp23-bcs-011@cuisahiwal.edu.pk" },
  { studentId: "stu-7a-019", rollNo: "SP23-BCS-019", name: "Talha Mehmood", email: "sp23-bcs-019@cuisahiwal.edu.pk" },
  { studentId: "stu-7a-027", rollNo: "SP23-BCS-027", name: "Sana Waqar", email: "sp23-bcs-027@cuisahiwal.edu.pk" },
  { studentId: "stu-7a-034", rollNo: "SP23-BCS-034", name: "Fawad Irshad", email: "sp23-bcs-034@cuisahiwal.edu.pk" },
  { studentId: "stu-7a-042", rollNo: "SP23-BCS-042", name: "Amina Sohail", email: "sp23-bcs-042@cuisahiwal.edu.pk" },
  { studentId: "stu-7a-049", rollNo: "SP23-BCS-049", name: "Zohaib Akhtar", email: "sp23-bcs-049@cuisahiwal.edu.pk" },
  { studentId: "stu-7a-056", rollNo: "SP23-BCS-056", name: "Laiba Arshad", email: "sp23-bcs-056@cuisahiwal.edu.pk" }
];

const BCS_8B_STUDENTS: FacultyClassRosterStudent[] = [
  { studentId: "stu-8b-203", rollNo: "FA22-BCS-203", name: "Omer Hayat", email: "fa22-bcs-203@cuisahiwal.edu.pk" },
  { studentId: "stu-8b-210", rollNo: "FA22-BCS-210", name: "Khadija Nadeem", email: "fa22-bcs-210@cuisahiwal.edu.pk" },
  { studentId: "stu-8b-216", rollNo: "FA22-BCS-216", name: "Rehan Aslam", email: "fa22-bcs-216@cuisahiwal.edu.pk" },
  { studentId: "stu-8b-225", rollNo: "FA22-BCS-225", name: "Noor-ul-Ain", email: "fa22-bcs-225@cuisahiwal.edu.pk" },
  { studentId: "stu-8b-233", rollNo: "FA22-BCS-233", name: "Salman Haider", email: "fa22-bcs-233@cuisahiwal.edu.pk" },
  { studentId: "stu-8b-241", rollNo: "FA22-BCS-241", name: "Iqra Riaz", email: "fa22-bcs-241@cuisahiwal.edu.pk" },
  { studentId: "stu-8b-248", rollNo: "FA22-BCS-248", name: "Waleed Zafar", email: "fa22-bcs-248@cuisahiwal.edu.pk" },
  { studentId: "stu-8b-259", rollNo: "FA22-BCS-259", name: "Mahnoor Tariq", email: "fa22-bcs-259@cuisahiwal.edu.pk" }
];

export const FACULTY_CLASSES: FacultyClassInfo[] = [
  {
    id: "cls-compiler-7c",
    courseCode: "CSC-354",
    courseTitle: "Compiler Construction",
    section: "BCS-7C",
    room: "Room C-204 (C Block, 2nd Floor)",
    scheduleSummary: "Mon / Wed · Slot 2 (10:15 AM – 11:45 AM)",
    students: BCS_7C_STUDENTS
  },
  {
    id: "cls-compiler-7a",
    courseCode: "CSC-354",
    courseTitle: "Compiler Construction Lab",
    section: "BCS-7A",
    room: "Software Lab 2 (C Block, Ground Floor)",
    scheduleSummary: "Tue / Thu · Slot 4 (02:00 PM – 03:30 PM)",
    students: BCS_7A_STUDENTS
  },
  {
    id: "cls-ai-8b",
    courseCode: "CSC-462",
    courseTitle: "Artificial Intelligence",
    section: "BCS-8B",
    room: "Room A-201 (A Block, 2nd Floor)",
    scheduleSummary: "Wed / Fri · Slot 5 (03:45 PM – 05:15 PM)",
    students: BCS_8B_STUDENTS
  }
];

export type BinaryAttendanceStatus = "PRESENT" | "ABSENT";

export interface SavedAttendanceSheet {
  key: string; // `${classId}__${date}__${slot}`
  classId: string;
  date: string;
  slot: string;
  submittedAt: string;
  records: Record<string, BinaryAttendanceStatus>;
}

export interface FolderAssessmentMarkRow {
  studentId: string;
  rollNo: string;
  studentName: string;
  submittedFile: string;
  marks: number | null;
}

export interface ClassAssessmentFolder {
  id: string;
  classId: string;
  folderName: "Assignment 1" | "Assignment 2" | "Quizzes";
  subtitle: string;
  maxMarks: number;
  rows: FolderAssessmentMarkRow[];
}

export const ATTENDANCE_SHEETS_STORAGE_KEY = "smart_edu_teacher_attendance_sheets_v1";
export const FOLDER_GRADES_STORAGE_KEY = "smart_edu_teacher_folder_grades_v1";
export const LOCAL_RESOURCES_STORAGE_KEY = "smart_edu_teacher_local_resources_v1";

function buildFolderRows(
  students: FacultyClassRosterStudent[],
  folderName: ClassAssessmentFolder["folderName"],
  maxMarks: number,
  leaveSomeUngraded: boolean
): FolderAssessmentMarkRow[] {
  return students.map((stu, index) => {
    const filePrefix =
      folderName === "Quizzes"
        ? "quiz_attempt"
        : folderName.toLowerCase().replace(/\s+/g, "_");
    const ext = folderName === "Quizzes" ? "sheet" : "pdf";
    const isPending = leaveSomeUngraded && index >= students.length - 4;
    const sampleScore = Math.max(
      Math.round(maxMarks * 0.55 * 2) / 2,
      Math.min(maxMarks, maxMarks - ((index % 4) * 0.5))
    );
    return {
      studentId: stu.studentId,
      rollNo: stu.rollNo,
      studentName: stu.name,
      submittedFile: `${stu.rollNo}_${filePrefix}.${ext}`,
      marks: isPending ? null : sampleScore
    };
  });
}

export function createInitialAssessmentFolders(): ClassAssessmentFolder[] {
  const folders: ClassAssessmentFolder[] = [];
  for (const cls of FACULTY_CLASSES) {
    folders.push(
      {
        id: `${cls.id}-as-1`,
        classId: cls.id,
        folderName: "Assignment 1",
        subtitle:
          cls.courseCode === "CSC-462"
            ? "Midterm Lab Project"
            : "Assignment 1 (Flex Lexical Analyzer)",
        maxMarks: 10,
        rows: buildFolderRows(
          cls.students,
          "Assignment 1",
          10,
          cls.id === "cls-compiler-7c"
        )
      },
      {
        id: `${cls.id}-as-2`,
        classId: cls.id,
        folderName: "Assignment 2",
        subtitle:
          cls.courseCode === "CSC-462"
            ? "Heuristic Search Report"
            : "Assignment 2 (LL(1) & Syntax Parser)",
        maxMarks: 10,
        rows: buildFolderRows(cls.students, "Assignment 2", 10, false)
      },
      {
        id: `${cls.id}-quizzes`,
        classId: cls.id,
        folderName: "Quizzes",
        subtitle: `${cls.courseTitle} — Quizzes Gradebook`,
        maxMarks: 10,
        rows: buildFolderRows(cls.students, "Quizzes", 10, false)
      }
    );
  }
  return folders;
}

export function loadSavedAttendanceSheets(): Record<string, SavedAttendanceSheet> {
  try {
    const raw = localStorage.getItem(ATTENDANCE_SHEETS_STORAGE_KEY);
    if (raw) return JSON.parse(raw) as Record<string, SavedAttendanceSheet>;
  } catch {
    // ignore corrupted local cache
  }
  const initialRecords: Record<string, BinaryAttendanceStatus> = {};
  BCS_8B_STUDENTS.forEach((s, idx) => {
    initialRecords[s.studentId] = idx === 2 ? "ABSENT" : "PRESENT";
  });
  const today = new Date().toISOString().slice(0, 10);
  const seedKey = `cls-ai-8b__${today}__Slot 5`;
  return {
    [seedKey]: {
      key: seedKey,
      classId: "cls-ai-8b",
      date: today,
      slot: "Slot 5",
      submittedAt: "Today, 03:50 PM",
      records: initialRecords
    }
  };
}

export function saveAttendanceSheet(sheet: SavedAttendanceSheet) {
  const existing = loadSavedAttendanceSheets();
  const next = { ...existing, [sheet.key]: sheet };
  try {
    localStorage.setItem(ATTENDANCE_SHEETS_STORAGE_KEY, JSON.stringify(next));
  } catch {
    // ignore storage quota errors
  }
  return next;
}

export function loadFolderGrades(): ClassAssessmentFolder[] {
  try {
    const raw = localStorage.getItem(FOLDER_GRADES_STORAGE_KEY);
    if (raw) return JSON.parse(raw) as ClassAssessmentFolder[];
  } catch {
    // ignore
  }
  return createInitialAssessmentFolders();
}

export function saveFolderGrades(folders: ClassAssessmentFolder[]) {
  try {
    localStorage.setItem(FOLDER_GRADES_STORAGE_KEY, JSON.stringify(folders));
  } catch {
    // ignore
  }
}

export interface LocalTeacherResource {
  id: string;
  title: string;
  description: string;
  resourceType: string;
  sectionLabel: string;
  fileName?: string;
  createdAt: string;
}

export function loadLocalTeacherResources(): LocalTeacherResource[] {
  try {
    const raw = localStorage.getItem(LOCAL_RESOURCES_STORAGE_KEY);
    if (raw) return JSON.parse(raw) as LocalTeacherResource[];
  } catch {
    // ignore
  }
  return [
    {
      id: "loc-res-1",
      title: "Week 06 — Lexical Analysis & DFA Slides (PDF)",
      description: "Complete lecture deck for SP23-BCS-7C Compiler Construction.",
      resourceType: "FILE",
      sectionLabel: "CSC-354 · BCS-7C",
      fileName: "week06-lexical-dfa.pdf",
      createdAt: "Today"
    }
  ];
}

export function saveLocalTeacherResources(items: LocalTeacherResource[]) {
  try {
    localStorage.setItem(LOCAL_RESOURCES_STORAGE_KEY, JSON.stringify(items));
  } catch {
    // ignore
  }
}
