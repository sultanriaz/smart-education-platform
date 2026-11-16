export interface RoomEquipment {
  hasProjector: boolean;
  hasWifi: boolean;
  hasAC: boolean;
  hasPowerSockets: boolean;
  hasWorkstations: boolean;
  hasSmartPodium: boolean;
}

export interface RoomScheduleSlot {
  slot: number; // 1 to 5
  isFree: boolean;
  freeUntil?: string;
  nextClass?: string;
  bookedBy?: string;
}

export interface CampusRoom {
  id: string;
  code: string;
  name: string;
  block: "Block A" | "Block B" | "Block C" | "Block D" | "Engineering Labs";
  floor: "Ground Floor" | "1st Floor" | "2nd Floor" | "3rd Floor";
  capacity: number;
  equipment: RoomEquipment;
  schedulesByDay: Record<string, RoomScheduleSlot[]>;
  currentStatus: "AVAILABLE" | "OCCUPIED" | "RESERVED";
  freeUntil: string;
  nextClass: string;
}

export interface StudyGroupReservation {
  id: string;
  roomCode: string;
  roomName: string;
  block: string;
  floor: string;
  day: string;
  slotNumber: number;
  slotTime: string;
  durationMinutes: number;
  purpose: string;
  groupSize: number;
  reservedAt: string;
  expiresAt: string;
  expiresInSeconds: number; // 15-min check-in countdown
  isCheckedIn: boolean;
  qrToken: string;
  status: "AWAITING_CHECK_IN" | "CONFIRMED_ACTIVE" | "EXPIRED" | "CANCELLED";
}

export const CAMPUS_DAYS = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday"
] as const;

export type CampusDay = (typeof CAMPUS_DAYS)[number];

export interface SlotDefinition {
  number: number;
  label: string;
  timeRange: string;
  startMinutes: number; // minutes from midnight e.g. 8*60+30 = 510
  endMinutes: number;   // 10*60 = 600
}

export const CAMPUS_SLOTS: SlotDefinition[] = [
  { number: 1, label: "Slot 1 (08:30 - 10:00)", timeRange: "08:30 AM – 10:00 AM", startMinutes: 510, endMinutes: 600 },
  { number: 2, label: "Slot 2 (10:15 - 11:45)", timeRange: "10:15 AM – 11:45 AM", startMinutes: 615, endMinutes: 705 },
  { number: 3, label: "Slot 3 (12:00 - 01:30)", timeRange: "12:00 PM – 01:30 PM", startMinutes: 720, endMinutes: 810 },
  { number: 4, label: "Slot 4 (02:00 - 03:30)", timeRange: "02:00 PM – 03:30 PM", startMinutes: 840, endMinutes: 930 },
  { number: 5, label: "Slot 5 (03:45 - 05:15)", timeRange: "03:45 PM – 05:15 PM", startMinutes: 945, endMinutes: 1035 }
];

export const CAMPUS_BLOCKS = [
  "All Blocks",
  "Block A",
  "Block B",
  "Block C",
  "Block D",
  "Engineering Labs"
] as const;

export type CampusBlockFilter = (typeof CAMPUS_BLOCKS)[number];

export const CAMPUS_ROOMS: CampusRoom[] = [
  // ================= BLOCK A =================
  {
    id: "a-102",
    code: "Room A-102",
    name: "Natural Sciences Smart Classroom",
    block: "Block A",
    floor: "1st Floor",
    capacity: 60,
    equipment: {
      hasProjector: true,
      hasWifi: true,
      hasAC: true,
      hasPowerSockets: true,
      hasWorkstations: false,
      hasSmartPodium: true
    },
    schedulesByDay: {
      Monday: [
        { slot: 1, isFree: true, freeUntil: "10:00 AM", nextClass: "PHY-101 Physics Lecture" },
        { slot: 2, isFree: false, bookedBy: "PHY-101 Physics Lecture" },
        { slot: 3, isFree: true, freeUntil: "01:30 PM", nextClass: "CHM-110 General Chemistry" },
        { slot: 4, isFree: false, bookedBy: "CHM-110 General Chemistry" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Free for evening study" }
      ],
      Tuesday: [
        { slot: 1, isFree: false, bookedBy: "MTH-101 Calculus I" },
        { slot: 2, isFree: true, freeUntil: "11:45 AM", nextClass: "BIO-105 Molecular Biology" },
        { slot: 3, isFree: true, freeUntil: "01:30 PM", nextClass: "BIO-105 Molecular Biology" },
        { slot: 4, isFree: true, freeUntil: "03:30 PM", nextClass: "Free for study sessions" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Free for evening study" }
      ],
      Wednesday: [
        { slot: 1, isFree: true, freeUntil: "10:00 AM", nextClass: "PHY-101 Physics Lab Prep" },
        { slot: 2, isFree: false, bookedBy: "MTH-201 Differential Equations" },
        { slot: 3, isFree: true, freeUntil: "01:30 PM", nextClass: "MTH-302 Linear Algebra" },
        { slot: 4, isFree: true, freeUntil: "03:30 PM", nextClass: "Free for rest of day" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Evening Facility Maintenance" }
      ],
      Thursday: [
        { slot: 1, isFree: true, freeUntil: "10:00 AM", nextClass: "MTH-201 Differential Equations" },
        { slot: 2, isFree: true, freeUntil: "11:45 AM", nextClass: "Free for study" },
        { slot: 3, isFree: false, bookedBy: "PHY-202 Modern Physics" },
        { slot: 4, isFree: true, freeUntil: "03:30 PM", nextClass: "Free for student teams" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Free for evening study" }
      ],
      Friday: [
        { slot: 1, isFree: false, bookedBy: "CHM-201 Organic Chemistry" },
        { slot: 2, isFree: true, freeUntil: "11:45 AM", nextClass: "CHM-201 Tutorial" },
        { slot: 3, isFree: true, freeUntil: "01:30 PM", nextClass: "Friday Prayer Break & Free" },
        { slot: 4, isFree: true, freeUntil: "03:30 PM", nextClass: "Open Study Hall" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Open Study Hall" }
      ],
      Saturday: [
        { slot: 1, isFree: true, freeUntil: "10:00 AM", nextClass: "Weekend Robotics Boot Camp" },
        { slot: 2, isFree: true, freeUntil: "11:45 AM", nextClass: "Free for study" },
        { slot: 3, isFree: true, freeUntil: "01:30 PM", nextClass: "Free for study" },
        { slot: 4, isFree: true, freeUntil: "03:30 PM", nextClass: "Free for study" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Free for study" }
      ]
    },
    currentStatus: "AVAILABLE",
    freeUntil: "01:30 PM",
    nextClass: "MTH-302 Linear Algebra (Slot 3)"
  },
  {
    id: "a-201",
    code: "Room A-201",
    name: "Engineering Lecture Theater 1",
    block: "Block A",
    floor: "2nd Floor",
    capacity: 70,
    equipment: {
      hasProjector: true,
      hasWifi: true,
      hasAC: true,
      hasPowerSockets: true,
      hasWorkstations: false,
      hasSmartPodium: false
    },
    schedulesByDay: {
      Wednesday: [
        { slot: 1, isFree: false, bookedBy: "EEE-211 Electronic Devices" },
        { slot: 2, isFree: true, freeUntil: "11:45 AM", nextClass: "CSC-331 Database Systems" },
        { slot: 3, isFree: false, bookedBy: "CSC-331 Database Systems" },
        { slot: 4, isFree: true, freeUntil: "03:30 PM", nextClass: "Free for study sessions" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Faculty Departmental Meeting" }
      ]
    },
    currentStatus: "AVAILABLE",
    freeUntil: "11:45 AM",
    nextClass: "CSC-331 Database Systems (Slot 3)"
  },
  {
    id: "a-203",
    code: "Room A-203",
    name: "Graduate Seminar Room",
    block: "Block A",
    floor: "2nd Floor",
    capacity: 45,
    equipment: {
      hasProjector: true,
      hasWifi: true,
      hasAC: true,
      hasPowerSockets: true,
      hasWorkstations: false,
      hasSmartPodium: true
    },
    schedulesByDay: {
      Wednesday: [
        { slot: 1, isFree: true, freeUntil: "10:00 AM", nextClass: "MCS-2A Research Colloquium" },
        { slot: 2, isFree: true, freeUntil: "11:45 AM", nextClass: "MCS-2A Research Colloquium" },
        { slot: 3, isFree: false, bookedBy: "MS Thesis Defense Session" },
        { slot: 4, isFree: true, freeUntil: "03:30 PM", nextClass: "Free for project groups" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Evening study" }
      ]
    },
    currentStatus: "AVAILABLE",
    freeUntil: "11:45 AM",
    nextClass: "MS Thesis Defense Session (Slot 3)"
  },

  // ================= BLOCK B =================
  {
    id: "b-101",
    code: "Room B-101",
    name: "Circuit Theory Smart Room",
    block: "Block B",
    floor: "1st Floor",
    capacity: 55,
    equipment: {
      hasProjector: true,
      hasWifi: true,
      hasAC: true,
      hasPowerSockets: true,
      hasWorkstations: false,
      hasSmartPodium: true
    },
    schedulesByDay: {
      Wednesday: [
        { slot: 1, isFree: true, freeUntil: "10:00 AM", nextClass: "BEE-3A Circuits Analysis" },
        { slot: 2, isFree: false, bookedBy: "BEE-3A Circuits Analysis" },
        { slot: 3, isFree: true, freeUntil: "01:30 PM", nextClass: "Free for student teams" },
        { slot: 4, isFree: true, freeUntil: "03:30 PM", nextClass: "Robotics Club Workshop" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Free for study" }
      ]
    },
    currentStatus: "AVAILABLE",
    freeUntil: "10:00 AM",
    nextClass: "BEE-3A Circuits Analysis (Slot 2)"
  },
  {
    id: "b-202",
    code: "Room B-202",
    name: "Mechanical CAD & Design Hall",
    block: "Block B",
    floor: "2nd Floor",
    capacity: 48,
    equipment: {
      hasProjector: true,
      hasWifi: true,
      hasAC: true,
      hasPowerSockets: true,
      hasWorkstations: true,
      hasSmartPodium: true
    },
    schedulesByDay: {
      Wednesday: [
        { slot: 1, isFree: false, bookedBy: "SolidWorks Mechanical Modeling" },
        { slot: 2, isFree: true, freeUntil: "11:45 AM", nextClass: "Free for CAD practice" },
        { slot: 3, isFree: true, freeUntil: "01:30 PM", nextClass: "Thermodynamics Lecture" },
        { slot: 4, isFree: false, bookedBy: "Thermodynamics Lecture" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Evening study" }
      ]
    },
    currentStatus: "AVAILABLE",
    freeUntil: "01:30 PM",
    nextClass: "Thermodynamics Lecture (Slot 4)"
  },
  {
    id: "b-301",
    code: "Room B-301",
    name: "Civil Structures Lecture Hall",
    block: "Block B",
    floor: "3rd Floor",
    capacity: 60,
    equipment: {
      hasProjector: true,
      hasWifi: true,
      hasAC: true,
      hasPowerSockets: true,
      hasWorkstations: false,
      hasSmartPodium: false
    },
    schedulesByDay: {
      Wednesday: [
        { slot: 1, isFree: true, freeUntil: "10:00 AM", nextClass: "CE-301 Structural Analysis" },
        { slot: 2, isFree: true, freeUntil: "11:45 AM", nextClass: "CE-301 Structural Analysis" },
        { slot: 3, isFree: false, bookedBy: "CE-301 Structural Analysis" },
        { slot: 4, isFree: true, freeUntil: "03:30 PM", nextClass: "Open Study Group" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Open Study Group" }
      ]
    },
    currentStatus: "AVAILABLE",
    freeUntil: "11:45 AM",
    nextClass: "CE-301 Structural Analysis (Slot 3)"
  },

  // ================= BLOCK C =================
  {
    id: "c-102",
    code: "Room C-102",
    name: "Computer Science Standard Hall",
    block: "Block C",
    floor: "1st Floor",
    capacity: 65,
    equipment: {
      hasProjector: true,
      hasWifi: true,
      hasAC: true,
      hasPowerSockets: true,
      hasWorkstations: false,
      hasSmartPodium: false
    },
    schedulesByDay: {
      Wednesday: [
        { slot: 1, isFree: true, freeUntil: "10:00 AM", nextClass: "BCS-5A Data Structures" },
        { slot: 2, isFree: true, freeUntil: "11:45 AM", nextClass: "BCS-5A Data Structures" },
        { slot: 3, isFree: false, bookedBy: "BCS-5A Data Structures" },
        { slot: 4, isFree: true, freeUntil: "03:30 PM", nextClass: "Free for coding clubs" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Free until 05:15 PM" }
      ]
    },
    currentStatus: "AVAILABLE",
    freeUntil: "11:45 AM",
    nextClass: "BCS-5A Data Structures (Slot 3)"
  },
  {
    id: "c-201",
    code: "Room C-201",
    name: "Senior Lecture Room (BCS-7A)",
    block: "Block C",
    floor: "2nd Floor",
    capacity: 65,
    equipment: {
      hasProjector: true,
      hasWifi: true,
      hasAC: true,
      hasPowerSockets: true,
      hasWorkstations: false,
      hasSmartPodium: true
    },
    schedulesByDay: {
      Wednesday: [
        { slot: 1, isFree: false, bookedBy: "CSC-322 Operating Systems" },
        { slot: 2, isFree: true, freeUntil: "11:45 AM", nextClass: "Free for group projects" },
        { slot: 3, isFree: true, freeUntil: "01:30 PM", nextClass: "Free for group projects" },
        { slot: 4, isFree: false, bookedBy: "CSC-462 AI Advanced Elective" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Free for evening study" }
      ]
    },
    currentStatus: "AVAILABLE",
    freeUntil: "01:30 PM",
    nextClass: "CSC-462 AI Advanced Elective (Slot 4)"
  },
  {
    id: "c-204",
    code: "Room C-204",
    name: "Smart Lecture Hall (BCS-7C)",
    block: "Block C",
    floor: "2nd Floor",
    capacity: 60,
    equipment: {
      hasProjector: true,
      hasWifi: true,
      hasAC: true,
      hasPowerSockets: true,
      hasWorkstations: false,
      hasSmartPodium: true
    },
    schedulesByDay: {
      Wednesday: [
        { slot: 1, isFree: true, freeUntil: "10:15 AM", nextClass: "CSC-354 Compiler Construction" },
        { slot: 2, isFree: false, bookedBy: "CSC-354 Compiler Construction" },
        { slot: 3, isFree: true, freeUntil: "01:30 PM", nextClass: "Free for study teams" },
        { slot: 4, isFree: true, freeUntil: "03:30 PM", nextClass: "Free for study teams" },
        { slot: 5, isFree: false, bookedBy: "Evening Professional Certification" }
      ]
    },
    currentStatus: "AVAILABLE",
    freeUntil: "10:15 AM",
    nextClass: "CSC-354 Compiler Construction (Slot 2)"
  },
  {
    id: "c-302",
    code: "Room C-302",
    name: "Postgraduate Research Suite",
    block: "Block C",
    floor: "3rd Floor",
    capacity: 35,
    equipment: {
      hasProjector: true,
      hasWifi: true,
      hasAC: true,
      hasPowerSockets: true,
      hasWorkstations: true,
      hasSmartPodium: true
    },
    schedulesByDay: {
      Wednesday: [
        { slot: 1, isFree: true, freeUntil: "10:00 AM", nextClass: "MS-CS Seminar" },
        { slot: 2, isFree: true, freeUntil: "11:45 AM", nextClass: "MS-CS Seminar" },
        { slot: 3, isFree: true, freeUntil: "01:30 PM", nextClass: "MS-CS Seminar" },
        { slot: 4, isFree: false, bookedBy: "Natural Language Processing Workshop" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Evening research" }
      ]
    },
    currentStatus: "AVAILABLE",
    freeUntil: "01:30 PM",
    nextClass: "Natural Language Processing Workshop (Slot 4)"
  },

  // ================= BLOCK D =================
  {
    id: "d-101",
    code: "Room D-101",
    name: "Management Sciences Executive Hall",
    block: "Block D",
    floor: "1st Floor",
    capacity: 60,
    equipment: {
      hasProjector: true,
      hasWifi: true,
      hasAC: true,
      hasPowerSockets: true,
      hasWorkstations: false,
      hasSmartPodium: true
    },
    schedulesByDay: {
      Wednesday: [
        { slot: 1, isFree: true, freeUntil: "10:00 AM", nextClass: "BBA-4B Financial Accounting" },
        { slot: 2, isFree: false, bookedBy: "BBA-4B Financial Accounting" },
        { slot: 3, isFree: true, freeUntil: "01:30 PM", nextClass: "Free for study groups" },
        { slot: 4, isFree: true, freeUntil: "03:30 PM", nextClass: "Free for study groups" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Free for study groups" }
      ]
    },
    currentStatus: "AVAILABLE",
    freeUntil: "10:00 AM",
    nextClass: "BBA-4B Financial Accounting (Slot 2)"
  },
  {
    id: "d-lib-a",
    code: "Library Pod A",
    name: "Collaborative Study Pod A",
    block: "Block D",
    floor: "Ground Floor",
    capacity: 12,
    equipment: {
      hasProjector: false,
      hasWifi: true,
      hasAC: true,
      hasPowerSockets: true,
      hasWorkstations: false,
      hasSmartPodium: false
    },
    schedulesByDay: {
      Wednesday: [
        { slot: 1, isFree: true, freeUntil: "10:00 AM", nextClass: "Open Collaborative Study" },
        { slot: 2, isFree: true, freeUntil: "11:45 AM", nextClass: "Open Collaborative Study" },
        { slot: 3, isFree: true, freeUntil: "01:30 PM", nextClass: "Open Collaborative Study" },
        { slot: 4, isFree: true, freeUntil: "03:30 PM", nextClass: "Open Collaborative Study" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Open Collaborative Study" }
      ]
    },
    currentStatus: "AVAILABLE",
    freeUntil: "05:00 PM",
    nextClass: "Open for walk-in study all day"
  },
  {
    id: "d-lib-b",
    code: "Library Pod B",
    name: "Collaborative Study Pod B",
    block: "Block D",
    floor: "Ground Floor",
    capacity: 16,
    equipment: {
      hasProjector: true,
      hasWifi: true,
      hasAC: true,
      hasPowerSockets: true,
      hasWorkstations: false,
      hasSmartPodium: false
    },
    schedulesByDay: {
      Wednesday: [
        { slot: 1, isFree: false, bookedBy: "Debate Society Practice" },
        { slot: 2, isFree: true, freeUntil: "11:45 AM", nextClass: "Open Study Group" },
        { slot: 3, isFree: true, freeUntil: "01:30 PM", nextClass: "Open Study Group" },
        { slot: 4, isFree: true, freeUntil: "03:30 PM", nextClass: "Open Study Group" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Open Study Group" }
      ]
    },
    currentStatus: "AVAILABLE",
    freeUntil: "05:15 PM",
    nextClass: "Open Study Group (Slot 3)"
  },

  // ================= ENGINEERING & CS LABS =================
  {
    id: "lab-cs1",
    code: "Software Lab 1",
    name: "Departmental Software Engineering Lab",
    block: "Engineering Labs",
    floor: "Ground Floor",
    capacity: 50,
    equipment: {
      hasProjector: true,
      hasWifi: true,
      hasAC: true,
      hasPowerSockets: true,
      hasWorkstations: true,
      hasSmartPodium: true
    },
    schedulesByDay: {
      Wednesday: [
        { slot: 1, isFree: true, freeUntil: "10:00 AM", nextClass: "SE-4A Agile Scrum Sprint" },
        { slot: 2, isFree: false, bookedBy: "SE-4A Agile Scrum Sprint" },
        { slot: 3, isFree: true, freeUntil: "01:30 PM", nextClass: "Free for programming practice" },
        { slot: 4, isFree: true, freeUntil: "03:30 PM", nextClass: "Free for programming practice" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Free for programming practice" }
      ]
    },
    currentStatus: "AVAILABLE",
    freeUntil: "10:00 AM",
    nextClass: "SE-4A Agile Scrum Sprint (Slot 2)"
  },
  {
    id: "lab-ai",
    code: "AI & Robotics Lab",
    name: "GPU Deep Learning & Automation Lab",
    block: "Engineering Labs",
    floor: "Ground Floor",
    capacity: 40,
    equipment: {
      hasProjector: true,
      hasWifi: true,
      hasAC: true,
      hasPowerSockets: true,
      hasWorkstations: true,
      hasSmartPodium: true
    },
    schedulesByDay: {
      Wednesday: [
        { slot: 1, isFree: true, freeUntil: "10:00 AM", nextClass: "Free for student AI experiments" },
        { slot: 2, isFree: true, freeUntil: "11:45 AM", nextClass: "Free for student AI experiments" },
        { slot: 3, isFree: false, bookedBy: "CSC-462 Computer Vision Lab" },
        { slot: 4, isFree: false, bookedBy: "CSC-462 Computer Vision Lab" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Robotics Club Testing" }
      ]
    },
    currentStatus: "AVAILABLE",
    freeUntil: "11:45 AM",
    nextClass: "CSC-462 Computer Vision Lab (Slot 3)"
  },
  {
    id: "lab-nw",
    code: "Networks & Cyber Lab",
    name: "Cisco Networking & Security Center",
    block: "Engineering Labs",
    floor: "1st Floor",
    capacity: 45,
    equipment: {
      hasProjector: true,
      hasWifi: true,
      hasAC: true,
      hasPowerSockets: true,
      hasWorkstations: true,
      hasSmartPodium: true
    },
    schedulesByDay: {
      Wednesday: [
        { slot: 1, isFree: false, bookedBy: "CNS-411 Ethical Hacking Lab" },
        { slot: 2, isFree: false, bookedBy: "CNS-411 Ethical Hacking Lab" },
        { slot: 3, isFree: true, freeUntil: "01:30 PM", nextClass: "Free for Packet Tracer practice" },
        { slot: 4, isFree: true, freeUntil: "03:30 PM", nextClass: "Free for Packet Tracer practice" },
        { slot: 5, isFree: true, freeUntil: "05:15 PM", nextClass: "Evening maintenance" }
      ]
    },
    currentStatus: "AVAILABLE",
    freeUntil: "01:30 PM",
    nextClass: "Free for Packet Tracer practice (Slot 3)"
  }
];

export const INITIAL_STUDY_RESERVATIONS: StudyGroupReservation[] = [
  {
    id: "res-c201-1",
    roomCode: "Room C-201",
    roomName: "Senior Lecture Room (BCS-7A)",
    block: "Block C",
    floor: "2nd Floor",
    day: "Wednesday",
    slotNumber: 2,
    slotTime: "10:15 AM – 11:45 AM",
    durationMinutes: 90,
    purpose: "Compiler Construction Parser Implementation Sprint",
    groupSize: 4,
    reservedAt: "10:05 AM",
    expiresAt: "10:20 AM",
    expiresInSeconds: 580,
    isCheckedIn: true,
    qrToken: "RES-C201-4491-BCS7C",
    status: "CONFIRMED_ACTIVE"
  }
];

/**
 * Returns the 5 slots schedule for a given room on any day.
 * If not explicitly recorded for that day, returns an authentic deterministic schedule
 * derived from the room's base schedule so all days (Monday - Saturday) are complete.
 */
export function getRoomDaySchedule(room: CampusRoom, day: string): RoomScheduleSlot[] {
  if (room.schedulesByDay[day]) {
    return room.schedulesByDay[day]!;
  }

  // Deterministic schedule generator for non-explicit days
  const baseWed = room.schedulesByDay["Wednesday"] || [];
  const dayOffset = CAMPUS_DAYS.indexOf(day as CampusDay);
  const hash = room.code.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0) + (dayOffset >= 0 ? dayOffset : 1);

  return [1, 2, 3, 4, 5].map((slotNum) => {
    const wedSlot = baseWed.find((s) => s.slot === slotNum);
    const isFree = (hash * slotNum * 7) % 3 !== 0; // ~66% free rate
    const nextSlotDef = CAMPUS_SLOTS.find((s) => s.number === slotNum);

    return {
      slot: slotNum,
      isFree: wedSlot ? (dayOffset % 2 === 0 ? wedSlot.isFree : isFree) : isFree,
      freeUntil: nextSlotDef?.timeRange.split("–")[1]?.trim() || "05:15 PM",
      nextClass: isFree ? `Free for self-study / group meetings` : `Departmental Lecture (${room.block})`,
      bookedBy: isFree ? undefined : `Academic Class Slot ${slotNum}`
    };
  });
}

/**
 * Helper to get the current clock status (day, slot, or whether it's available right now).
 */
export function getCurrentSlotTelemetry(): {
  day: CampusDay;
  slotNumber: number;
  slotLabel: string;
  isWithinSlot: boolean;
  timeString: string;
} {
  const now = new Date();
  const dayIndex = now.getDay(); // 0 is Sunday, 1 is Monday...
  const dayName: CampusDay =
    dayIndex >= 1 && dayIndex <= 6 ? CAMPUS_DAYS[dayIndex - 1]! : "Wednesday";

  const currentMinutes = now.getHours() * 60 + now.getMinutes();

  // Find slot that contains currentMinutes, or find next nearest slot
  const activeSlot = CAMPUS_SLOTS.find(
    (slot) => currentMinutes >= slot.startMinutes && currentMinutes <= slot.endMinutes
  );

  if (activeSlot) {
    return {
      day: dayName,
      slotNumber: activeSlot.number,
      slotLabel: activeSlot.label,
      isWithinSlot: true,
      timeString: now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    };
  }

  // If outside standard slots, find the next upcoming slot or default to Slot 2
  const nextSlot = CAMPUS_SLOTS.find((slot) => slot.startMinutes > currentMinutes) || CAMPUS_SLOTS[1]!;

  return {
    day: dayName,
    slotNumber: nextSlot.number,
    slotLabel: nextSlot.label,
    isWithinSlot: false,
    timeString: now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  };
}
