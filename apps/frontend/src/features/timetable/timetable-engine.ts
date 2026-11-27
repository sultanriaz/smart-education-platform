export interface TimetableSlot {
  id: string;
  slotNumber: number;
  timeRange: string;
  startTime: string; // 24h "HH:MM"
  endTime: string;   // 24h "HH:MM"
  courseCode: string;
  courseTitle: string;
  instructorName: string;
  instructorOffice: string;
  section: string;
  room: string;
  block: "A Block" | "C Block" | "D Block";
  floor: string;
  capacity: number;
  enrolledStudents: number;
  day: "Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday";
  colorScheme: {
    bg: string;
    border: string;
    text: string;
    badge: string;
  };
  swapAlert?: {
    type: "ROOM_SWAP" | "RESCHEDULED" | "ONLINE" | "CANCELLED";
    message: string;
    previousRoom?: string;
    newRoom?: string;
  };
}

export const STANDARD_PERIODS = [
  { slot: 1, label: "Slot 1", time: "08:30 AM – 10:00 AM", start: "08:30", end: "10:00" },
  { slot: 2, label: "Slot 2", time: "10:15 AM – 11:45 AM", start: "10:15", end: "11:45" },
  { slot: 3, label: "Slot 3", time: "12:00 PM – 01:30 PM", start: "12:00", end: "13:30" },
  { slot: 4, label: "Slot 4", time: "02:00 PM – 03:30 PM", start: "14:00", end: "15:30" },
  { slot: 5, label: "Slot 5", time: "03:45 PM – 05:15 PM", start: "15:45", end: "17:15" }
];

const COLOR_SCHEMES = {
  os: {
    bg: "bg-primary-soft/60",
    border: "border-primary/25",
    text: "text-primary-ink",
    badge: "bg-primary/15 text-primary-ink"
  },
  compiler: {
    bg: "bg-secondary-soft/60",
    border: "border-secondary/30",
    text: "text-secondary-ink",
    badge: "bg-secondary/15 text-secondary-ink"
  },
  se: {
    bg: "bg-success-soft/60",
    border: "border-success/25",
    text: "text-success-ink",
    badge: "bg-success/15 text-success-ink"
  },
  ai: {
    bg: "bg-warning-soft/70",
    border: "border-warning/30",
    text: "text-warning-ink",
    badge: "bg-warning/15 text-warning-ink"
  },
  db: {
    bg: "bg-subtle/75",
    border: "border-line",
    text: "text-ink",
    badge: "bg-panel text-muted border border-line"
  },
  grad: {
    bg: "bg-accent-soft/65",
    border: "border-accent/35",
    text: "text-accent-ink",
    badge: "bg-accent/20 text-accent-ink"
  }
} as const;

const MASTER_SLOTS: TimetableSlot[] = [
  // ==================== MONDAY ====================
  {
    id: "slot-mon-1-bcs7c",
    slotNumber: 1,
    timeRange: "08:30 AM – 10:00 AM",
    startTime: "08:30",
    endTime: "10:00",
    courseCode: "CSC-322",
    courseTitle: "Operating Systems",
    instructorName: "Dr. Muhammad Asim",
    instructorOffice: "C Block, 2nd Floor, Room C-203",
    section: "BCS-7C",
    room: "Room C-101",
    block: "C Block",
    floor: "1st Floor",
    capacity: 65,
    enrolledStudents: 58,
    day: "Monday",
    colorScheme: COLOR_SCHEMES.os
  },
  {
    id: "slot-mon-1-bcs7b",
    slotNumber: 1,
    timeRange: "08:30 AM – 10:00 AM",
    startTime: "08:30",
    endTime: "10:00",
    courseCode: "CSC-371",
    courseTitle: "Software Engineering",
    instructorName: "Dr. Majid Hussain",
    instructorOffice: "A Block, 3rd Floor, Room A-302",
    section: "BCS-7B",
    room: "Room A-102",
    block: "A Block",
    floor: "1st Floor",
    capacity: 60,
    enrolledStudents: 55,
    day: "Monday",
    colorScheme: COLOR_SCHEMES.se
  },
  {
    id: "slot-mon-2-bcs7c",
    slotNumber: 2,
    timeRange: "10:15 AM – 11:45 AM",
    startTime: "10:15",
    endTime: "11:45",
    courseCode: "CSC-354",
    courseTitle: "Compiler Construction",
    instructorName: "Dr. Munir Ahmad",
    instructorOffice: "A Block, 3rd Floor, Room A-301",
    section: "BCS-7C",
    room: "Room C-204",
    block: "C Block",
    floor: "2nd Floor",
    capacity: 60,
    enrolledStudents: 54,
    day: "Monday",
    colorScheme: COLOR_SCHEMES.compiler
  },
  {
    id: "slot-mon-3-bcs7a",
    slotNumber: 3,
    timeRange: "12:00 PM – 01:30 PM",
    startTime: "12:00",
    endTime: "13:30",
    courseCode: "CSC-322",
    courseTitle: "Operating Systems",
    instructorName: "Dr. Muhammad Asim",
    instructorOffice: "C Block, 2nd Floor, Room C-203",
    section: "BCS-7A",
    room: "Room C-103",
    block: "C Block",
    floor: "1st Floor",
    capacity: 65,
    enrolledStudents: 56,
    day: "Monday",
    colorScheme: COLOR_SCHEMES.os
  },
  {
    id: "slot-mon-4-bcs7a",
    slotNumber: 4,
    timeRange: "02:00 PM – 03:30 PM",
    startTime: "14:00",
    endTime: "15:30",
    courseCode: "CSC-354",
    courseTitle: "Compiler Construction Lab",
    instructorName: "Dr. Munir Ahmad",
    instructorOffice: "A Block, 3rd Floor, Room A-301",
    section: "BCS-7A",
    room: "Software Lab 2",
    block: "C Block",
    floor: "Ground Floor",
    capacity: 55,
    enrolledStudents: 48,
    day: "Monday",
    colorScheme: COLOR_SCHEMES.compiler
  },

  // ==================== TUESDAY ====================
  {
    id: "slot-tue-1-bcs7a",
    slotNumber: 1,
    timeRange: "08:30 AM – 10:00 AM",
    startTime: "08:30",
    endTime: "10:00",
    courseCode: "CSC-331",
    courseTitle: "Database Systems",
    instructorName: "Engr. Tariq Mehmood",
    instructorOffice: "A Block, 1st Floor, Room A-103",
    section: "BCS-7A",
    room: "Room A-201",
    block: "A Block",
    floor: "2nd Floor",
    capacity: 65,
    enrolledStudents: 59,
    day: "Tuesday",
    colorScheme: COLOR_SCHEMES.db
  },
  {
    id: "slot-tue-2-bcs7c",
    slotNumber: 2,
    timeRange: "10:15 AM – 11:45 AM",
    startTime: "10:15",
    endTime: "11:45",
    courseCode: "CSC-371",
    courseTitle: "Software Engineering",
    instructorName: "Dr. Majid Hussain",
    instructorOffice: "A Block, 3rd Floor, Room A-302",
    section: "BCS-7C",
    room: "Room C-102",
    block: "C Block",
    floor: "1st Floor",
    capacity: 65,
    enrolledStudents: 52,
    day: "Tuesday",
    colorScheme: COLOR_SCHEMES.se
  },
  {
    id: "slot-tue-3-bcs7b",
    slotNumber: 3,
    timeRange: "12:00 PM – 01:30 PM",
    startTime: "12:00",
    endTime: "13:30",
    courseCode: "CSC-322",
    courseTitle: "Operating Systems Lab",
    instructorName: "Dr. Muhammad Asim",
    instructorOffice: "C Block, 2nd Floor, Room C-203",
    section: "BCS-7B",
    room: "Computer Lab 2",
    block: "C Block",
    floor: "Ground Floor",
    capacity: 50,
    enrolledStudents: 47,
    day: "Tuesday",
    colorScheme: COLOR_SCHEMES.os
  },
  {
    id: "slot-tue-4-bcs7c",
    slotNumber: 4,
    timeRange: "02:00 PM – 03:30 PM",
    startTime: "14:00",
    endTime: "15:30",
    courseCode: "CSC-462",
    courseTitle: "Artificial Intelligence Lab",
    instructorName: "Engr. Bilal Khan",
    instructorOffice: "C Block, Ground Floor, Room C-02",
    section: "BCS-7C",
    room: "Software Lab 1",
    block: "C Block",
    floor: "Ground Floor",
    capacity: 50,
    enrolledStudents: 48,
    day: "Tuesday",
    colorScheme: COLOR_SCHEMES.ai,
    swapAlert: {
      type: "ROOM_SWAP",
      message: "Moved from Room C-02 to Software Lab 1 while new lab computers are set up.",
      previousRoom: "Room C-02",
      newRoom: "Software Lab 1"
    }
  },

  // ==================== WEDNESDAY ====================
  {
    id: "slot-wed-1-bcs7a",
    slotNumber: 1,
    timeRange: "08:30 AM – 10:00 AM",
    startTime: "08:30",
    endTime: "10:00",
    courseCode: "CSC-354",
    courseTitle: "Compiler Construction",
    instructorName: "Dr. Munir Ahmad",
    instructorOffice: "A Block, 3rd Floor, Room A-301",
    section: "BCS-7A",
    room: "Room C-201",
    block: "C Block",
    floor: "2nd Floor",
    capacity: 65,
    enrolledStudents: 56,
    day: "Wednesday",
    colorScheme: COLOR_SCHEMES.compiler
  },
  {
    id: "slot-wed-2-bcs7c",
    slotNumber: 2,
    timeRange: "10:15 AM – 11:45 AM",
    startTime: "10:15",
    endTime: "11:45",
    courseCode: "CSC-354",
    courseTitle: "Compiler Construction",
    instructorName: "Dr. Munir Ahmad",
    instructorOffice: "A Block, 3rd Floor, Room A-301",
    section: "BCS-7C",
    room: "Room C-204",
    block: "C Block",
    floor: "2nd Floor",
    capacity: 60,
    enrolledStudents: 54,
    day: "Wednesday",
    colorScheme: COLOR_SCHEMES.compiler
  },
  {
    id: "slot-wed-3-bcs7c",
    slotNumber: 3,
    timeRange: "12:00 PM – 01:30 PM",
    startTime: "12:00",
    endTime: "13:30",
    courseCode: "CSC-331",
    courseTitle: "Database Systems",
    instructorName: "Engr. Tariq Mehmood",
    instructorOffice: "A Block, 1st Floor, Room A-103",
    section: "BCS-7C",
    room: "Room A-201",
    block: "A Block",
    floor: "2nd Floor",
    capacity: 65,
    enrolledStudents: 62,
    day: "Wednesday",
    colorScheme: COLOR_SCHEMES.db
  },
  {
    id: "slot-wed-4-bcs7b",
    slotNumber: 4,
    timeRange: "02:00 PM – 03:30 PM",
    startTime: "14:00",
    endTime: "15:30",
    courseCode: "CSC-462",
    courseTitle: "Artificial Intelligence",
    instructorName: "Engr. Bilal Khan",
    instructorOffice: "C Block, Ground Floor, Room C-02",
    section: "BCS-7B",
    room: "Room D-101",
    block: "D Block",
    floor: "1st Floor",
    capacity: 60,
    enrolledStudents: 53,
    day: "Wednesday",
    colorScheme: COLOR_SCHEMES.ai
  },

  // ==================== THURSDAY ====================
  {
    id: "slot-thu-1-bcs7c",
    slotNumber: 1,
    timeRange: "08:30 AM – 10:00 AM",
    startTime: "08:30",
    endTime: "10:00",
    courseCode: "CSC-322",
    courseTitle: "Operating Systems",
    instructorName: "Dr. Muhammad Asim",
    instructorOffice: "C Block, 2nd Floor, Room C-203",
    section: "BCS-7C",
    room: "Room C-101",
    block: "C Block",
    floor: "1st Floor",
    capacity: 65,
    enrolledStudents: 58,
    day: "Thursday",
    colorScheme: COLOR_SCHEMES.os
  },
  {
    id: "slot-thu-2-bcs7a",
    slotNumber: 2,
    timeRange: "10:15 AM – 11:45 AM",
    startTime: "10:15",
    endTime: "11:45",
    courseCode: "CSC-322",
    courseTitle: "Operating Systems Lab",
    instructorName: "Dr. Muhammad Asim",
    instructorOffice: "C Block, 2nd Floor, Room C-203",
    section: "BCS-7A",
    room: "Computer Lab 2",
    block: "C Block",
    floor: "Ground Floor",
    capacity: 50,
    enrolledStudents: 49,
    day: "Thursday",
    colorScheme: COLOR_SCHEMES.os
  },
  {
    id: "slot-thu-3-bcs7c",
    slotNumber: 3,
    timeRange: "12:00 PM – 01:30 PM",
    startTime: "12:00",
    endTime: "13:30",
    courseCode: "CSC-331",
    courseTitle: "Database Systems Lab",
    instructorName: "Engr. Tariq Mehmood",
    instructorOffice: "A Block, 1st Floor, Room A-103",
    section: "BCS-7C",
    room: "Computer Lab 1",
    block: "A Block",
    floor: "1st Floor",
    capacity: 50,
    enrolledStudents: 45,
    day: "Thursday",
    colorScheme: COLOR_SCHEMES.db
  },
  {
    id: "slot-thu-3-bcs7b",
    slotNumber: 3,
    timeRange: "12:00 PM – 01:30 PM",
    startTime: "12:00",
    endTime: "13:30",
    courseCode: "CSC-371",
    courseTitle: "Software Engineering",
    instructorName: "Dr. Majid Hussain",
    instructorOffice: "A Block, 3rd Floor, Room A-302",
    section: "BCS-7B",
    room: "Room A-102",
    block: "A Block",
    floor: "1st Floor",
    capacity: 60,
    enrolledStudents: 55,
    day: "Thursday",
    colorScheme: COLOR_SCHEMES.se
  },
  {
    id: "slot-thu-4-mcs2a",
    slotNumber: 4,
    timeRange: "02:00 PM – 03:30 PM",
    startTime: "14:00",
    endTime: "15:30",
    courseCode: "CSC-354",
    courseTitle: "Advanced Compiler Design",
    instructorName: "Dr. Munir Ahmad",
    instructorOffice: "A Block, 3rd Floor, Room A-301",
    section: "MCS-2A",
    room: "Room A-203",
    block: "A Block",
    floor: "2nd Floor",
    capacity: 40,
    enrolledStudents: 28,
    day: "Thursday",
    colorScheme: COLOR_SCHEMES.grad
  },

  // ==================== FRIDAY ====================
  {
    id: "slot-fri-1-bcs7a",
    slotNumber: 1,
    timeRange: "08:30 AM – 10:00 AM",
    startTime: "08:30",
    endTime: "10:00",
    courseCode: "CSC-462",
    courseTitle: "Artificial Intelligence",
    instructorName: "Engr. Bilal Khan",
    instructorOffice: "C Block, Ground Floor, Room C-02",
    section: "BCS-7A",
    room: "Room D-101",
    block: "D Block",
    floor: "1st Floor",
    capacity: 60,
    enrolledStudents: 51,
    day: "Friday",
    colorScheme: COLOR_SCHEMES.ai
  },
  {
    id: "slot-fri-2-bcs7b",
    slotNumber: 2,
    timeRange: "10:15 AM – 11:45 AM",
    startTime: "10:15",
    endTime: "11:45",
    courseCode: "CSC-331",
    courseTitle: "Database Systems Lab",
    instructorName: "Engr. Tariq Mehmood",
    instructorOffice: "A Block, 1st Floor, Room A-103",
    section: "BCS-7B",
    room: "Computer Lab 1",
    block: "A Block",
    floor: "1st Floor",
    capacity: 50,
    enrolledStudents: 46,
    day: "Friday",
    colorScheme: COLOR_SCHEMES.db
  },
  {
    id: "slot-fri-4-bcs7c",
    slotNumber: 4,
    timeRange: "02:00 PM – 03:30 PM",
    startTime: "14:00",
    endTime: "15:30",
    courseCode: "CSC-371",
    courseTitle: "Software Engineering",
    instructorName: "Dr. Majid Hussain",
    instructorOffice: "A Block, 3rd Floor, Room A-302",
    section: "BCS-7C",
    room: "Room C-102",
    block: "C Block",
    floor: "1st Floor",
    capacity: 65,
    enrolledStudents: 52,
    day: "Friday",
    colorScheme: COLOR_SCHEMES.se
  }
];

function mapSectionSlots(sourceSection: string, displaySection: string): TimetableSlot[] {
  return MASTER_SLOTS.filter((s) => s.section === sourceSection).map((s) => ({
    ...s,
    id: `${s.id}-${displaySection.toLowerCase()}`,
    section: displaySection
  }));
}

const EXTRA_STUDENT_SLOTS: TimetableSlot[] = [
  {
    id: "slot-mon-1-bcs5b",
    slotNumber: 1,
    timeRange: "08:30 AM – 10:00 AM",
    startTime: "08:30",
    endTime: "10:00",
    courseCode: "CSC-301",
    courseTitle: "Design & Analysis of Algorithms",
    instructorName: "Dr. Muhammad Asim",
    instructorOffice: "C Block, 2nd Floor, Room C-203",
    section: "FA24-BCS-5B",
    room: "Room B-202",
    block: "C Block",
    floor: "2nd Floor",
    capacity: 60,
    enrolledStudents: 53,
    day: "Monday",
    colorScheme: COLOR_SCHEMES.os
  },
  {
    id: "slot-tue-2-bcs5b",
    slotNumber: 2,
    timeRange: "10:15 AM – 11:45 AM",
    startTime: "10:15",
    endTime: "11:45",
    courseCode: "CSC-322",
    courseTitle: "Operating Systems",
    instructorName: "Engr. Tariq Mehmood",
    instructorOffice: "C Block, 1st Floor, Room C-108",
    section: "FA24-BCS-5B",
    room: "Room C-105",
    block: "C Block",
    floor: "1st Floor",
    capacity: 60,
    enrolledStudents: 53,
    day: "Tuesday",
    colorScheme: COLOR_SCHEMES.compiler
  },
  {
    id: "slot-wed-3-bcs5b",
    slotNumber: 3,
    timeRange: "12:00 PM – 01:30 PM",
    startTime: "12:00",
    endTime: "13:30",
    courseCode: "CSC-336",
    courseTitle: "Web Engineering",
    instructorName: "Engr. Bilal Khan",
    instructorOffice: "C Block, Ground Floor, Room C-02",
    section: "FA24-BCS-5B",
    room: "Software Lab 1",
    block: "C Block",
    floor: "Ground Floor",
    capacity: 50,
    enrolledStudents: 48,
    day: "Wednesday",
    colorScheme: COLOR_SCHEMES.se
  },
  {
    id: "slot-thu-1-bcs5b",
    slotNumber: 1,
    timeRange: "08:30 AM – 10:00 AM",
    startTime: "08:30",
    endTime: "10:00",
    courseCode: "CSC-312",
    courseTitle: "Theory of Automata",
    instructorName: "Dr. Munir Ahmad",
    instructorOffice: "C Block, 2nd Floor, Room C-201",
    section: "FA24-BCS-5B",
    room: "Room A-104",
    block: "A Block",
    floor: "1st Floor",
    capacity: 60,
    enrolledStudents: 52,
    day: "Thursday",
    colorScheme: COLOR_SCHEMES.ai
  },
  {
    id: "slot-mon-2-bcs4a",
    slotNumber: 2,
    timeRange: "10:15 AM – 11:45 AM",
    startTime: "10:15",
    endTime: "11:45",
    courseCode: "CSC-331",
    courseTitle: "Database Systems",
    instructorName: "Dr. Majid Hussain",
    instructorOffice: "A Block, 3rd Floor, Room A-302",
    section: "SP25-BCS-4A",
    room: "Room A-201",
    block: "A Block",
    floor: "2nd Floor",
    capacity: 65,
    enrolledStudents: 56,
    day: "Monday",
    colorScheme: COLOR_SCHEMES.db
  },
  {
    id: "slot-wed-1-bcs4a",
    slotNumber: 1,
    timeRange: "08:30 AM – 10:00 AM",
    startTime: "08:30",
    endTime: "10:00",
    courseCode: "CSC-371",
    courseTitle: "Software Engineering",
    instructorName: "Dr. Majid Hussain",
    instructorOffice: "A Block, 3rd Floor, Room A-302",
    section: "SP25-BCS-4A",
    room: "Room C-102",
    block: "C Block",
    floor: "1st Floor",
    capacity: 65,
    enrolledStudents: 56,
    day: "Wednesday",
    colorScheme: COLOR_SCHEMES.se
  },
  {
    id: "slot-fri-2-bcs4a",
    slotNumber: 2,
    timeRange: "10:15 AM – 11:45 AM",
    startTime: "10:15",
    endTime: "11:45",
    courseCode: "CSC-291",
    courseTitle: "Computer Organization",
    instructorName: "Engr. Tariq Mehmood",
    instructorOffice: "C Block, 1st Floor, Room C-108",
    section: "SP25-BCS-4A",
    room: "Room C-103",
    block: "C Block",
    floor: "1st Floor",
    capacity: 60,
    enrolledStudents: 54,
    day: "Friday",
    colorScheme: COLOR_SCHEMES.os
  },
  {
    id: "slot-tue-1-bcs3c",
    slotNumber: 1,
    timeRange: "08:30 AM – 10:00 AM",
    startTime: "08:30",
    endTime: "10:00",
    courseCode: "CSC-211",
    courseTitle: "Data Structures & Algorithms",
    instructorName: "Engr. Bilal Khan",
    instructorOffice: "C Block, Ground Floor, Room C-02",
    section: "FA25-BCS-3C",
    room: "Room A-101",
    block: "A Block",
    floor: "1st Floor",
    capacity: 60,
    enrolledStudents: 57,
    day: "Tuesday",
    colorScheme: COLOR_SCHEMES.compiler
  },
  {
    id: "slot-thu-3-bcs3c",
    slotNumber: 3,
    timeRange: "12:00 PM – 01:30 PM",
    startTime: "12:00",
    endTime: "13:30",
    courseCode: "MTH-231",
    courseTitle: "Discrete Structures",
    instructorName: "Dr. Muhammad Asim",
    instructorOffice: "C Block, 2nd Floor, Room C-203",
    section: "FA25-BCS-3C",
    room: "Room D-104",
    block: "D Block",
    floor: "1st Floor",
    capacity: 55,
    enrolledStudents: 57,
    day: "Thursday",
    colorScheme: COLOR_SCHEMES.db
  }
];

export const STUDENT_SCHEDULE: TimetableSlot[] = mapSectionSlots("BCS-7C", "SP23-BCS-7C");

export const TEACHER_SCHEDULE: TimetableSlot[] = MASTER_SLOTS.filter(
  (s) => s.instructorName === "Dr. Munir Ahmad"
);

export const STUDENT_TIMETABLES_BY_SECTION: Record<string, TimetableSlot[]> = {
  "SP23-BCS-7C": mapSectionSlots("BCS-7C", "SP23-BCS-7C"),
  "SP23-BCS-7B": mapSectionSlots("BCS-7B", "SP23-BCS-7B"),
  "SP23-BCS-7A": mapSectionSlots("BCS-7A", "SP23-BCS-7A"),
  "FA24-BCS-5B": EXTRA_STUDENT_SLOTS.filter((s) => s.section === "FA24-BCS-5B"),
  "SP25-BCS-4A": EXTRA_STUDENT_SLOTS.filter((s) => s.section === "SP25-BCS-4A"),
  "FA25-BCS-3C": EXTRA_STUDENT_SLOTS.filter((s) => s.section === "FA25-BCS-3C")
};

export const TEACHER_TIMETABLES_BY_NAME: Record<string, TimetableSlot[]> = {
  "Sir Munir (Dr. Munir Ahmad)": MASTER_SLOTS.filter((s) => s.instructorName === "Dr. Munir Ahmad"),
  "Dr. Muhammad Asim": MASTER_SLOTS.filter((s) => s.instructorName === "Dr. Muhammad Asim"),
  "Dr. Majid Hussain": MASTER_SLOTS.filter((s) => s.instructorName === "Dr. Majid Hussain"),
  "Engr. Tariq Mehmood": MASTER_SLOTS.filter((s) => s.instructorName === "Engr. Tariq Mehmood"),
  "Engr. Bilal Khan": MASTER_SLOTS.filter((s) => s.instructorName === "Engr. Bilal Khan")
};

const COURSE_CODE_TO_ROUTE_SLUG: Record<string, string> = {
  "CSC-354": "compiler",
  "CSC-322": "os",
  "CSC-331": "db",
  "CSC-371": "se"
};

/** Resolve a timetable course code to its student course page slug, if available. */
export function getStudentCourseSlug(courseCode: string): string | null {
  return COURSE_CODE_TO_ROUTE_SLUG[courseCode.toUpperCase()] ?? null;
}

/** Generate an iCalendar (.ics) string for exporting to Google, Apple, or Outlook calendar. */
export function generateICS(slots: TimetableSlot[], calendarName = "Class Timetable"): string {
  const dayCodeMap: Record<string, string> = {
    Monday: "MO",
    Tuesday: "TU",
    Wednesday: "WE",
    Thursday: "TH",
    Friday: "FR"
  };

  const lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//COMSATS SmartEdu Platform//Timetable//EN",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    `X-WR-CALNAME:${calendarName}`,
    "X-WR-TIMEZONE:Asia/Karachi"
  ];

  for (const slot of slots) {
    const dayCode = dayCodeMap[slot.day] || "MO";
    const startHourMin = slot.startTime.replace(":", "") + "00";
    const endHourMin = slot.endTime.replace(":", "") + "00";
    const uid = `${slot.id}@smartedu.cuisahiwal.edu.pk`;

    lines.push(
      "BEGIN:VEVENT",
      `UID:${uid}`,
      `SUMMARY:${slot.courseCode}: ${slot.courseTitle} (${slot.section})`,
      `DESCRIPTION:Teacher: ${slot.instructorName}\\nOffice: ${slot.instructorOffice}\\nClass: ${slot.section}\\nRoom: ${slot.room} (${slot.block}, ${slot.floor})\\nSeats: ${slot.enrolledStudents} of ${slot.capacity}`,
      `LOCATION:${slot.room}, ${slot.block}, ${slot.floor}, COMSATS University Sahiwal`,
      `DTSTART;TZID=Asia/Karachi:20261116T${startHourMin}`,
      `DTEND;TZID=Asia/Karachi:20261116T${endHourMin}`,
      `RRULE:FREQ=WEEKLY;BYDAY=${dayCode};UNTIL=20270131T235959Z`,
      "STATUS:CONFIRMED",
      "END:VEVENT"
    );
  }

  lines.push("END:VCALENDAR");
  return lines.join("\r\n");
}

export function downloadICSFile(slots: TimetableSlot[], filename = "COMSATS_Timetable.ics") {
  const icsData = generateICS(slots);
  const blob = new Blob([icsData], { type: "text/calendar;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
