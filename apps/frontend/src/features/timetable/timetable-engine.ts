export interface TimetableSlot {
  id: string;
  slotNumber: number;
  timeRange: string;
  startTime: string; // "10:15"
  endTime: string;   // "11:45"
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

export const STUDENT_SCHEDULE: TimetableSlot[] = [
  {
    id: "slot-mon-1",
    slotNumber: 1,
    timeRange: "08:30 AM – 10:00 AM",
    startTime: "08:30",
    endTime: "10:00",
    courseCode: "CSC-322",
    courseTitle: "Operating Systems",
    instructorName: "Dr. Muhammad Asim",
    instructorOffice: "C Block, 2nd Floor, Room C-203",
    section: "BCS-7A",
    room: "Room C-101",
    block: "C Block",
    floor: "1st Floor",
    capacity: 65,
    enrolledStudents: 58,
    day: "Monday",
    colorScheme: {
      bg: "bg-blue-500/10 dark:bg-blue-950/40",
      border: "border-blue-500/30",
      text: "text-blue-700 dark:text-blue-300",
      badge: "bg-blue-500/20 text-blue-700 dark:text-blue-300"
    }
  },
  {
    id: "slot-mon-2",
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
    colorScheme: {
      bg: "bg-purple-500/10 dark:bg-purple-950/40",
      border: "border-purple-500/30",
      text: "text-purple-700 dark:text-purple-300",
      badge: "bg-purple-500/20 text-purple-700 dark:text-purple-300"
    }
  },
  {
    id: "slot-tue-2",
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
    colorScheme: {
      bg: "bg-emerald-500/10 dark:bg-emerald-950/40",
      border: "border-emerald-500/30",
      text: "text-emerald-700 dark:text-emerald-300",
      badge: "bg-emerald-500/20 text-emerald-700 dark:text-emerald-300"
    }
  },
  {
    id: "slot-tue-4",
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
    colorScheme: {
      bg: "bg-amber-500/10 dark:bg-amber-950/40",
      border: "border-amber-500/30",
      text: "text-amber-700 dark:text-amber-300",
      badge: "bg-amber-500/20 text-amber-700 dark:text-amber-300"
    },
    swapAlert: {
      type: "ROOM_SWAP",
      message: "Room swap: Moved from C-02 Robotics Lab to Software Lab 1 due to GPU setup.",
      previousRoom: "C-02 Robotics Lab",
      newRoom: "Software Lab 1"
    }
  },
  {
    id: "slot-wed-2",
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
    colorScheme: {
      bg: "bg-purple-500/10 dark:bg-purple-950/40",
      border: "border-purple-500/30",
      text: "text-purple-700 dark:text-purple-300",
      badge: "bg-purple-500/20 text-purple-700 dark:text-purple-300"
    }
  },
  {
    id: "slot-wed-3",
    slotNumber: 3,
    timeRange: "12:00 PM – 01:30 PM",
    startTime: "12:00",
    endTime: "13:30",
    courseCode: "CSC-331",
    courseTitle: "Database Systems",
    instructorName: "Engr. Tariq Mehmood",
    instructorOffice: "A Block, 1st Floor, Room A-103",
    section: "BCS-7B",
    room: "Room A-201",
    block: "A Block",
    floor: "2nd Floor",
    capacity: 65,
    enrolledStudents: 62,
    day: "Wednesday",
    colorScheme: {
      bg: "bg-cyan-500/10 dark:bg-cyan-950/40",
      border: "border-cyan-500/30",
      text: "text-cyan-700 dark:text-cyan-300",
      badge: "bg-cyan-500/20 text-cyan-700 dark:text-cyan-300"
    }
  },
  {
    id: "slot-thu-1",
    slotNumber: 1,
    timeRange: "08:30 AM – 10:00 AM",
    startTime: "08:30",
    endTime: "10:00",
    courseCode: "CSC-322",
    courseTitle: "Operating Systems",
    instructorName: "Dr. Muhammad Asim",
    instructorOffice: "C Block, 2nd Floor, Room C-203",
    section: "BCS-7A",
    room: "Room C-101",
    block: "C Block",
    floor: "1st Floor",
    capacity: 65,
    enrolledStudents: 58,
    day: "Thursday",
    colorScheme: {
      bg: "bg-blue-500/10 dark:bg-blue-950/40",
      border: "border-blue-500/30",
      text: "text-blue-700 dark:text-blue-300",
      badge: "bg-blue-500/20 text-blue-700 dark:text-blue-300"
    }
  },
  {
    id: "slot-thu-3",
    slotNumber: 3,
    timeRange: "12:00 PM – 01:30 PM",
    startTime: "12:00",
    endTime: "13:30",
    courseCode: "CSC-331",
    courseTitle: "Database Systems Lab",
    instructorName: "Engr. Tariq Mehmood",
    instructorOffice: "A Block, 1st Floor, Room A-103",
    section: "BCS-7B",
    room: "Computer Lab 1",
    block: "A Block",
    floor: "1st Floor",
    capacity: 50,
    enrolledStudents: 45,
    day: "Thursday",
    colorScheme: {
      bg: "bg-cyan-500/10 dark:bg-cyan-950/40",
      border: "border-cyan-500/30",
      text: "text-cyan-700 dark:text-cyan-300",
      badge: "bg-cyan-500/20 text-cyan-700 dark:text-cyan-300"
    }
  },
  {
    id: "slot-fri-4",
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
    colorScheme: {
      bg: "bg-emerald-500/10 dark:bg-emerald-950/40",
      border: "border-emerald-500/30",
      text: "text-emerald-700 dark:text-emerald-300",
      badge: "bg-emerald-500/20 text-emerald-700 dark:text-emerald-300"
    }
  }
];

export const TEACHER_SCHEDULE: TimetableSlot[] = [
  {
    id: "t-slot-mon-2",
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
    colorScheme: {
      bg: "bg-purple-500/10 dark:bg-purple-950/40",
      border: "border-purple-500/30",
      text: "text-purple-700 dark:text-purple-300",
      badge: "bg-purple-500/20 text-purple-700 dark:text-purple-300"
    }
  },
  {
    id: "t-slot-mon-4",
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
    colorScheme: {
      bg: "bg-purple-500/10 dark:bg-purple-950/40",
      border: "border-purple-500/30",
      text: "text-purple-700 dark:text-purple-300",
      badge: "bg-purple-500/20 text-purple-700 dark:text-purple-300"
    }
  },
  {
    id: "t-slot-wed-2",
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
    colorScheme: {
      bg: "bg-purple-500/10 dark:bg-purple-950/40",
      border: "border-purple-500/30",
      text: "text-purple-700 dark:text-purple-300",
      badge: "bg-purple-500/20 text-purple-700 dark:text-purple-300"
    }
  },
  {
    id: "t-slot-thu-4",
    slotNumber: 4,
    timeRange: "02:00 PM – 03:30 PM",
    startTime: "14:00",
    endTime: "15:30",
    courseCode: "CSC-354",
    courseTitle: "Advanced Compiler Topics (PG)",
    instructorName: "Dr. Munir Ahmad",
    instructorOffice: "A Block, 3rd Floor, Room A-301",
    section: "MCS-2A",
    room: "Room A-203",
    block: "A Block",
    floor: "2nd Floor",
    capacity: 40,
    enrolledStudents: 28,
    day: "Thursday",
    colorScheme: {
      bg: "bg-indigo-500/10 dark:bg-indigo-950/40",
      border: "border-indigo-500/30",
      text: "text-indigo-700 dark:text-indigo-300",
      badge: "bg-indigo-500/20 text-indigo-700 dark:text-indigo-300"
    }
  }
];

/** Generate an iCalendar (.ics) string for exporting to Google, Apple, or Outlook calendar */
export function generateICS(slots: TimetableSlot[], calendarName = "Academic Timetable"): string {
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
    "PRODID:-//COMSATS SmartEdu Platform//Timetable Engine//EN",
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
      `DESCRIPTION:Instructor: ${slot.instructorName}\\nOffice: ${slot.instructorOffice}\\nSection: ${slot.section}\\nClassroom: ${slot.room} (${slot.block}, ${slot.floor})\\nCapacity: ${slot.capacity} (Enrolled: ${slot.enrolledStudents})`,
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
