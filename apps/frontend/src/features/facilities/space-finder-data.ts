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
  block: "Block A" | "Block B" | "Block C" | "Block D";
  floor: "Ground Floor" | "1st Floor" | "2nd Floor" | "3rd Floor";
  capacity: number;
  type?: "classroom" | "lab";
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
  startMinutes: number;
  endMinutes: number;
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
  "Block D"
] as const;

export type CampusBlockFilter = (typeof CAMPUS_BLOCKS)[number];

export const CAMPUS_ROOMS: CampusRoom[] = [
  {
    "id": "a-1",
    "code": "A-1",
    "name": "Lecture Hall A-1",
    "block": "Block A",
    "floor": "1st Floor",
    "capacity": 60,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "a-2",
    "code": "A-2",
    "name": "Smart Classroom A-2",
    "block": "Block A",
    "floor": "1st Floor",
    "capacity": 45,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "a-3",
    "code": "A-3",
    "name": "Seminar Room A-3",
    "block": "Block A",
    "floor": "1st Floor",
    "capacity": 55,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "a-4",
    "code": "A-4",
    "name": "Tutorial Room A-4",
    "block": "Block A",
    "floor": "2nd Floor",
    "capacity": 40,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "a-1-1",
    "code": "A-1.1",
    "name": "Discussion Room A-1.1",
    "block": "Block A",
    "floor": "1st Floor",
    "capacity": 50,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "a-1-2",
    "code": "A-1.2",
    "name": "Study Room A-1.2",
    "block": "Block A",
    "floor": "1st Floor",
    "capacity": 38,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "a-1-3",
    "code": "A-1.1",
    "name": "Research Pod A-1.1",
    "block": "Block A",
    "floor": "2nd Floor",
    "capacity": 48,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "a-lab-9",
    "code": "A Lab-9",
    "name": "Applied Computing Lab 9",
    "block": "Block A",
    "floor": "Ground Floor",
    "capacity": 30,
    "type": "lab",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": true,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block A Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "b-1",
    "code": "B-1",
    "name": "Engineering Hall B-1",
    "block": "Block B",
    "floor": "Ground Floor",
    "capacity": 70,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "b-2",
    "code": "B-2",
    "name": "Circuit Design Room B-2",
    "block": "Block B",
    "floor": "1st Floor",
    "capacity": 65,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "b-7",
    "code": "B-7",
    "name": "Lecture Hall B-7",
    "block": "Block B",
    "floor": "2nd Floor",
    "capacity": 60,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "b-8",
    "code": "B-8",
    "name": "Digital Logic Room B-8",
    "block": "Block B",
    "floor": "2nd Floor",
    "capacity": 55,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "b-3",
    "code": "B-3",
    "name": "Tutorial Room B-3",
    "block": "Block B",
    "floor": "1st Floor",
    "capacity": 50,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "b-4",
    "code": "B-4",
    "name": "Seminar Room B-4",
    "block": "Block B",
    "floor": "3rd Floor",
    "capacity": 45,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "b-5",
    "code": "B-5",
    "name": "Smart Classroom B-5",
    "block": "Block B",
    "floor": "3rd Floor",
    "capacity": 40,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "b-lab-1",
    "code": "B Lab-1",
    "name": "Electronics Hardware Lab",
    "block": "Block B",
    "floor": "Ground Floor",
    "capacity": 35,
    "type": "lab",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": true,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "b-lab-2",
    "code": "B Lab-2",
    "name": "VLSI & Embedded Systems Lab",
    "block": "Block B",
    "floor": "Ground Floor",
    "capacity": 30,
    "type": "lab",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": true,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block B Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "c-1",
    "code": "C-1",
    "name": "CS Standard Hall C-1",
    "block": "Block C",
    "floor": "Ground Floor",
    "capacity": 65,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "c-2",
    "code": "C-2",
    "name": "Algorithms Room C-2",
    "block": "Block C",
    "floor": "1st Floor",
    "capacity": 60,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "c-3",
    "code": "C-3",
    "name": "Database Systems C-3",
    "block": "Block C",
    "floor": "1st Floor",
    "capacity": 55,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "c-4",
    "code": "C-4",
    "name": "Compiler Lab Class C-4",
    "block": "Block C",
    "floor": "2nd Floor",
    "capacity": 50,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "c-5",
    "code": "C-5",
    "name": "Software Design C-5",
    "block": "Block C",
    "floor": "2nd Floor",
    "capacity": 45,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "c-6",
    "code": "C-6",
    "name": "Data Science Hall C-6",
    "block": "Block C",
    "floor": "3rd Floor",
    "capacity": 40,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "c-lab-1",
    "code": "C Lab-1",
    "name": "High-Performance Computing Lab",
    "block": "Block C",
    "floor": "Ground Floor",
    "capacity": 35,
    "type": "lab",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": true,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "c-lab-2",
    "code": "C Lab-2",
    "name": "Cloud & Distributed Systems Lab",
    "block": "Block C",
    "floor": "Ground Floor",
    "capacity": 30,
    "type": "lab",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": true,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block C Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "d-1",
    "code": "D-1",
    "name": "Management Executive Hall D-1",
    "block": "Block D",
    "floor": "Ground Floor",
    "capacity": 60,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "d-2",
    "code": "D-2",
    "name": "Finance & Economics Room D-2",
    "block": "Block D",
    "floor": "1st Floor",
    "capacity": 55,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "d-3",
    "code": "D-3",
    "name": "Marketing Analytics D-3",
    "block": "Block D",
    "floor": "1st Floor",
    "capacity": 50,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "d-4",
    "code": "D-4",
    "name": "Case Study Hall D-4",
    "block": "Block D",
    "floor": "2nd Floor",
    "capacity": 45,
    "type": "classroom",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": false,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "d-lab-1",
    "code": "D Lab-1",
    "name": "Business Simulation & FinTech Lab",
    "block": "Block D",
    "floor": "Ground Floor",
    "capacity": 30,
    "type": "lab",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": true,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "d-lib-a",
    "code": "Library Pod A",
    "name": "Collaborative Study Pod A",
    "block": "Block D",
    "floor": "Ground Floor",
    "capacity": 15,
    "type": "lab",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": true,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Block D Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "lab-cs1",
    "code": "Software Lab 1",
    "name": "Departmental Software Lab",
    "block": "Block C",
    "floor": "Ground Floor",
    "capacity": 50,
    "type": "lab",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": true,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "lab-ai",
    "code": "AI & Robotics Lab",
    "name": "GPU Deep Learning Lab",
    "block": "Block B",
    "floor": "Ground Floor",
    "capacity": 40,
    "type": "lab",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": true,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  },
  {
    "id": "lab-nw",
    "code": "Networks & Cyber Lab",
    "name": "Cisco Networking Center",
    "block": "Block A",
    "floor": "1st Floor",
    "capacity": 45,
    "type": "lab",
    "equipment": {
      "hasProjector": true,
      "hasWifi": true,
      "hasAC": true,
      "hasPowerSockets": true,
      "hasWorkstations": true,
      "hasSmartPodium": true
    },
    "schedulesByDay": {
      "Monday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Tuesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        }
      ],
      "Wednesday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "10:00 AM",
          "nextClass": "Open for self study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Thursday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Friday": [
        {
          "slot": 1,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 4,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ],
      "Saturday": [
        {
          "slot": 1,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 2,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 3,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        },
        {
          "slot": 4,
          "isFree": false,
          "nextClass": "Scheduled Engineering Labs Lecture",
          "bookedBy": "Department Class"
        },
        {
          "slot": 5,
          "isFree": true,
          "freeUntil": "03:30 PM",
          "nextClass": "Free for collaborative study"
        }
      ]
    },
    "currentStatus": "AVAILABLE",
    "freeUntil": "05:00 PM",
    "nextClass": "Open for student study"
  }
];

export const INITIAL_STUDY_RESERVATIONS: StudyGroupReservation[] = [
  {
    id: "res-c1-1",
    roomCode: "C-1",
    roomName: "CS Standard Hall C-1",
    block: "Block C",
    floor: "Ground Floor",
    day: "Wednesday",
    slotNumber: 2,
    slotTime: "10:15 AM – 11:45 AM",
    durationMinutes: 90,
    purpose: "Data Structures Group Problem Solving",
    groupSize: 4,
    reservedAt: "10:05 AM",
    expiresAt: "10:20 AM",
    expiresInSeconds: 580,
    isCheckedIn: true,
    qrToken: "RES-C1-4491",
    status: "CONFIRMED_ACTIVE"
  }
];

export function getRoomDaySchedule(room: CampusRoom, day: string): RoomScheduleSlot[] {
  if (room.schedulesByDay && room.schedulesByDay[day]) {
    return room.schedulesByDay[day]!;
  }

  const baseWed = (room.schedulesByDay && room.schedulesByDay["Wednesday"]) || [];
  const dayOffset = CAMPUS_DAYS.indexOf(day as CampusDay);
  const hash = room.code.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0) + (dayOffset >= 0 ? dayOffset : 1);

  return [1, 2, 3, 4, 5].map((slotNum) => {
    const wedSlot = baseWed.find((s) => s.slot === slotNum);
    const isFree = (hash * slotNum * 7) % 3 !== 0;

    return {
      slot: slotNum,
      isFree: wedSlot ? (dayOffset % 2 === 0 ? wedSlot.isFree : isFree) : isFree,
      freeUntil: "05:15 PM",
      nextClass: isFree ? "Free for self-study / group meetings" : "Scheduled Department Lecture",
      bookedBy: isFree ? undefined : "Academic Class"
    };
  });
}

export function getCurrentSlotTelemetry(): {
  day: CampusDay;
  slotNumber: number;
  slotLabel: string;
  isWithinSlot: boolean;
  timeString: string;
} {
  const now = new Date();
  const dayIndex = now.getDay();
  const dayName: CampusDay =
    dayIndex >= 1 && dayIndex <= 6 ? CAMPUS_DAYS[dayIndex - 1]! : "Wednesday";

  const currentMinutes = now.getHours() * 60 + now.getMinutes();
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

  const nextSlot = CAMPUS_SLOTS.find((slot) => slot.startMinutes > currentMinutes) || CAMPUS_SLOTS[0]!;

  return {
    day: dayName,
    slotNumber: nextSlot.number,
    slotLabel: nextSlot.label,
    isWithinSlot: false,
    timeString: now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  };
}
