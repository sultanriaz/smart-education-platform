export type FacultyDesignation =
  | "Campus Director"
  | "Dean of Faculty"
  | "Head of Department (HOD)"
  | "Batch Advisor"
  | "Tenured Professor"
  | "Associate Professor"
  | "Assistant Professor"
  | "Lecturer";

export interface FacultyProfile {
  id: string;
  name: string;
  designation: FacultyDesignation;
  department: string;
  advisoryBatch?: string;
  advisorySeason?: "Spring" | "Fall";
  officeRoom: string;
  block: "Block A" | "Block B" | "Block C" | "Block D" | "Engineering Labs";
  floor: "Ground Floor" | "1st Floor" | "2nd Floor" | "3rd Floor";
  email: string;
  phoneExtension: string;
  consultationHours: string;
  researchFocus: string;
  isAvailableToday: boolean;
  avatarInitials: string;
}

export interface AdministrativeOffice {
  id: string;
  name: string;
  category: "Academic Records" | "Finance & Accounts" | "Student Support" | "Health & Safety" | "Administration";
  officeRoom: string;
  block: "Block A" | "Block B" | "Block C" | "Block D" | "Admin Block";
  floor: "Ground Floor" | "1st Floor" | "2nd Floor" | "3rd Floor";
  headOfficer: string;
  headTitle: string;
  email: string;
  phone?: string;
  phoneExtension: string;
  workingHours: string;
  currentTicketServing: number;
  queueLength: number;
  avgWaitMinutes: number;
  counterStatus: "OPEN" | "BUSY" | "LUNCH_BREAK" | "CLOSED";
  servicesOffered: string[];
}

export interface ClassroomLab {
  id: string;
  roomCode: string;
  name: string;
  type: "Smart Classroom" | "Lecture Theater" | "Computer Lab" | "Hardware/Engineering Lab" | "Auditorium" | "Seminar Hall";
  block: "Block A" | "Block B" | "Block C" | "Block D" | "Engineering Labs";
  floor: "Ground Floor" | "1st Floor" | "2nd Floor" | "3rd Floor";
  capacity: number;
  equipment: {
    projectorsCount: number;
    workstationsCount: number;
    hasAC: boolean;
    hasWifi: boolean;
    hasAudioSystem: boolean;
    hasSmartPodium: boolean;
    specialGear?: string;
  };
  currentActivity: string;
  inCharge: string;
}

export interface LibraryBook {
  id: string;
  isbn: string;
  title: string;
  authors: string;
  edition: string;
  category: "Computer Science" | "Mathematics" | "Electrical Eng" | "Management Sciences" | "General Literature";
  shelfLocation: string;
  floor: "Ground Floor" | "1st Floor";
  totalCopies: number;
  availableCopies: number;
  isAvailable: boolean;
  digitalPdfAvailable: boolean;
}

export interface LibraryStatus {
  totalSilentSeats: number;
  availableSilentSeats: number;
  collaborativePodsTotal: number;
  collaborativePodsAvailable: number;
  openingHours: string;
  librarianOnDuty: string;
  catalog: LibraryBook[];
}

export interface FloorRoomMapNode {
  code: string;
  name: string;
  type: "classroom" | "lab" | "office" | "amenity" | "hall";
  gridCol: string; // e.g. "col-span-1"
  statusText?: string;
}

export interface FloorBlueprintLayout {
  block: string;
  floor: string;
  corridorDescription: string;
  emergencyExits: string;
  rooms: FloorRoomMapNode[];
}

// ================= DATASETS =================

export const CAMPUS_TOTAL_TEACHERS = 72;

export const FACULTY_DIRECTORY: FacultyProfile[] = [
  {
    id: "fac-1",
    name: "Prof. Dr. Saleem Farooq Shaukat",
    designation: "Campus Director",
    department: "Physics & Engineering",
    officeRoom: "Room A-301 (Directorate Wing)",
    block: "Block A",
    floor: "3rd Floor",
    email: "director@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 101",
    consultationHours: "Tue / Thu: 02:30 PM – 04:00 PM (By Appointment)",
    researchFocus: "Condensed Matter Physics, Semiconductor Materials & Nano-optics",
    isAvailableToday: true,
    avatarInitials: "SS"
  },
  {
    id: "fac-2",
    name: "Dr. Munir Ahmad (Sir Munir)",
    designation: "Head of Department (HOD)",
    department: "Computer Science",
    officeRoom: "Room A-301 (CS Faculty Wing)",
    block: "Block A",
    floor: "3rd Floor",
    email: "munir@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 201",
    consultationHours: "Mon / Wed: 11:30 AM – 01:00 PM",
    researchFocus: "Compiler Optimization, High Performance Computing & Software Engineering",
    isAvailableToday: true,
    avatarInitials: "MA"
  },
  {
    id: "fac-3",
    name: "Dr. Muhammad Asim",
    designation: "Head of Department (HOD)",
    department: "Electrical Engineering",
    officeRoom: "Room B-302 (EE Secretariat)",
    block: "Block B",
    floor: "3rd Floor",
    email: "hod-ee@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 301",
    consultationHours: "Wed / Fri: 10:00 AM – 11:30 AM",
    researchFocus: "Power Electronics, Renewable Micro-grids & Digital Signal Processing",
    isAvailableToday: true,
    avatarInitials: "MA"
  },
  {
    id: "fac-4",
    name: "Dr. Javed Iqbal",
    designation: "Batch Advisor",
    department: "Computer Science",
    advisoryBatch: "Fa22-BCS",
    advisorySeason: "Fall",
    officeRoom: "Room C-205",
    block: "Block C",
    floor: "2nd Floor",
    email: "javed.iqbal@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 215",
    consultationHours: "Mon – Thu: 01:30 PM – 03:00 PM",
    researchFocus: "Senior Batch Academic Advising (BCS-7), Distributed Systems",
    isAvailableToday: true,
    avatarInitials: "JI"
  },
  {
    id: "fac-5",
    name: "Dr. Raja Rizwan",
    designation: "Dean of Faculty",
    department: "Management Sciences",
    officeRoom: "Room D-104 (Dean's Complex)",
    block: "Block D",
    floor: "1st Floor",
    email: "studentaffairs@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 401",
    consultationHours: "Mon – Fri: 10:00 AM – 12:30 PM",
    researchFocus: "Corporate Strategy, Student Affairs & Organizational Dynamics",
    isAvailableToday: true,
    avatarInitials: "RR"
  },
  {
    id: "fac-6",
    name: "Dr. Ayesha Malik",
    designation: "Associate Professor",
    department: "Computer Science",
    officeRoom: "Room C-208",
    block: "Block C",
    floor: "2nd Floor",
    email: "ayesha.malik@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 224",
    consultationHours: "Tue / Thu: 10:15 AM – 12:00 PM",
    researchFocus: "Database Tuning, Natural Language Processing & Big Data Analytics",
    isAvailableToday: true,
    avatarInitials: "AM"
  },
  {
    id: "fac-7",
    name: "Engr. Bilal Khalid",
    designation: "Lecturer",
    department: "Electrical Engineering",
    officeRoom: "Room B-105",
    block: "Block B",
    floor: "1st Floor",
    email: "bilal.khalid@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 312",
    consultationHours: "Mon / Wed: 02:00 PM – 03:30 PM",
    researchFocus: "FPGA Design, Embedded IoT Architectures & Robotics Control",
    isAvailableToday: false,
    avatarInitials: "BK"
  },
  {
    id: "fac-8",
    name: "Ms. Hina Qaiser",
    designation: "Lecturer",
    department: "Computer Science",
    officeRoom: "Room C-107",
    block: "Block C",
    floor: "1st Floor",
    email: "hina.qaiser@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 235",
    consultationHours: "Wed / Fri: 09:00 AM – 11:00 AM",
    researchFocus: "Automata Theory, Formal Methods & Programming Fundamentals",
    isAvailableToday: true,
    avatarInitials: "HQ"
  },
  {
    id: "fac-9",
    name: "Dr. Majid Hussain",
    designation: "Head of Department (HOD)",
    department: "Software Engineering",
    officeRoom: "Room A-302 (SE Faculty Wing)",
    block: "Block A",
    floor: "3rd Floor",
    email: "majid.hussain@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 204",
    consultationHours: "Tue / Thu: 11:00 AM – 01:00 PM",
    researchFocus: "Software Architecture, Quality Engineering & Agile Systems",
    isAvailableToday: true,
    avatarInitials: "MH"
  },
  {
    id: "fac-10",
    name: "Dr. Sadia Mahmood",
    designation: "Head of Department (HOD)",
    department: "Management Sciences",
    officeRoom: "Room D-102 (MS Secretariat)",
    block: "Block D",
    floor: "1st Floor",
    email: "sadia.mahmood@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 405",
    consultationHours: "Mon / Wed: 12:00 PM – 02:00 PM",
    researchFocus: "Organizational Leadership, Corporate Finance & Policy",
    isAvailableToday: true,
    avatarInitials: "SM"
  },
  {
    id: "fac-11",
    name: "Engr. Tariq Mehmood",
    designation: "Assistant Professor",
    department: "Computer Science",
    officeRoom: "Room A-103",
    block: "Block A",
    floor: "1st Floor",
    email: "tariq.mehmood@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 219",
    consultationHours: "Tue / Thu: 01:30 PM – 03:00 PM",
    researchFocus: "Database Systems, Distributed Warehousing & Cloud Indexing",
    isAvailableToday: true,
    avatarInitials: "TM"
  },
  {
    id: "fac-12",
    name: "Engr. Bilal Khan",
    designation: "Lecturer",
    department: "Computer Science",
    officeRoom: "Room C-02",
    block: "Block C",
    floor: "Ground Floor",
    email: "bilal.khan@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 241",
    consultationHours: "Wed / Fri: 02:00 PM – 03:30 PM",
    researchFocus: "Applied Artificial Intelligence, Computer Vision & Machine Learning",
    isAvailableToday: true,
    avatarInitials: "BK"
  },
  {
    id: "fac-13",
    name: "Ms. Amna Tariq",
    designation: "Batch Advisor",
    department: "Software Engineering",
    advisoryBatch: "SP24-BSE",
    advisorySeason: "Spring",
    officeRoom: "Room A-206",
    block: "Block A",
    floor: "2nd Floor",
    email: "amna.tariq@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 248",
    consultationHours: "Mon – Thu: 11:00 AM – 01:00 PM",
    researchFocus: "Student Academic Advising (BSE-5) & Software Verification",
    isAvailableToday: true,
    avatarInitials: "AT"
  },
  {
    id: "fac-14",
    name: "Engr. Saad Mahmood",
    designation: "Batch Advisor",
    department: "Food Science",
    advisoryBatch: "Fa23-FSN",
    advisorySeason: "Fall",
    officeRoom: "Room B-204",
    block: "Block B",
    floor: "2nd Floor",
    email: "saad.mahmood@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 318",
    consultationHours: "Tue – Fri: 10:30 AM – 12:30 PM",
    researchFocus: "Student Academic Advising (Fa23-FSN) & Quality Assurance",
    isAvailableToday: true,
    avatarInitials: "SM"
  },
  {
    id: "fac-15",
    name: "Mr. Usman Khalid",
    designation: "Batch Advisor",
    department: "Management Sciences",
    advisoryBatch: "SP25-BBA",
    advisorySeason: "Spring",
    officeRoom: "Room D-203",
    block: "Block D",
    floor: "2nd Floor",
    email: "usman.khalid@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 418",
    consultationHours: "Mon / Wed / Fri: 01:00 PM – 03:00 PM",
    researchFocus: "Student Academic Advising (BBA-6) & Business Analytics",
    isAvailableToday: false,
    avatarInitials: "UK"
  },
  {
    id: "fac-30",
    name: "Mr. Arslan Sarwar",
    designation: "Batch Advisor",
    department: "Computer Science",
    advisoryBatch: "SP23-BCS",
    advisorySeason: "Spring",
    officeRoom: "Room C-104",
    block: "Block C",
    floor: "1st Floor",
    email: "arslan.sarwar@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 212",
    consultationHours: "Mon – Thu: 10:00 AM – 12:00 PM",
    researchFocus: "Batch Academic Advising (SP23-BCS) & Core Programming",
    isAvailableToday: true,
    avatarInitials: "AS"
  },
  {
    id: "fac-31",
    name: "Dr. Ahmed Sarwar",
    designation: "Batch Advisor",
    department: "Computer Science",
    advisoryBatch: "Fa24-BCS",
    advisorySeason: "Fall",
    officeRoom: "Room C-202",
    block: "Block C",
    floor: "2nd Floor",
    email: "ahmed.sarwar@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 214",
    consultationHours: "Tue / Thu: 11:30 AM – 01:30 PM",
    researchFocus: "Batch Academic Advising (Fa24-BCS) & Machine Learning",
    isAvailableToday: true,
    avatarInitials: "AS"
  },
  {
    id: "fac-16",
    name: "Dr. Ahmed Bilal",
    designation: "Head of Department (HOD)",
    department: "Food Science",
    officeRoom: "Room D-201 (Biosciences Wing)",
    block: "Block D",
    floor: "2nd Floor",
    email: "hod-fs@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 501",
    consultationHours: "Tue / Thu: 11:00 AM – 01:00 PM",
    researchFocus: "Food Preservation, Nutritional Biochemistry & Safety",
    isAvailableToday: true,
    avatarInitials: "AB"
  },
  {
    id: "fac-17",
    name: "Dr. Ali Raza",
    designation: "Head of Department (HOD)",
    department: "Chemistry",
    officeRoom: "Room B-102 (Sciences Secretariat)",
    block: "Block B",
    floor: "1st Floor",
    email: "hod-chem@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 512",
    consultationHours: "Mon / Wed: 10:00 AM – 12:00 PM",
    researchFocus: "Analytical Chemistry, Catalysis & Polymer Synthesis",
    isAvailableToday: true,
    avatarInitials: "AR"
  },
  {
    id: "fac-18",
    name: "Dr. Akbar Siddiqui",
    designation: "Head of Department (HOD)",
    department: "Civil Engineering",
    officeRoom: "Room B-201 (Civil Engg Wing)",
    block: "Block B",
    floor: "2nd Floor",
    email: "hod-civil@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 524",
    consultationHours: "Wed / Fri: 11:30 AM – 01:30 PM",
    researchFocus: "Structural Concrete Design & Geotechnical Infrastructure",
    isAvailableToday: true,
    avatarInitials: "AS"
  },
  {
    id: "fac-19",
    name: "Dr. Kamran Haider",
    designation: "Head of Department (HOD)",
    department: "Mathematics",
    officeRoom: "Room A-204 (Math Faculty Office)",
    block: "Block A",
    floor: "2nd Floor",
    email: "hod-math@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 535",
    consultationHours: "Tue / Thu: 01:30 PM – 03:00 PM",
    researchFocus: "Computational Fluid Dynamics & Applied Differential Equations",
    isAvailableToday: true,
    avatarInitials: "KH"
  },
  {
    id: "fac-20",
    name: "Ms. Saima Noor",
    designation: "Lecturer",
    department: "Food Science",
    officeRoom: "Room D-108",
    block: "Block D",
    floor: "1st Floor",
    email: "saima.noor@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 506",
    consultationHours: "Mon / Thu: 12:00 PM – 02:00 PM",
    researchFocus: "Dairy Processing & Clinical Nutrition Lab Courses",
    isAvailableToday: true,
    avatarInitials: "SN"
  },
  {
    id: "fac-21",
    name: "Mr. Bilal Shabir Qaisar",
    designation: "Lecturer",
    department: "Computer Science",
    officeRoom: "Room C-109",
    block: "Block C",
    floor: "1st Floor",
    email: "bilal.shabir@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 252",
    consultationHours: "Mon / Wed: 10:00 AM – 12:00 PM",
    researchFocus: "Object-Oriented Software Design & Web Engineering",
    isAvailableToday: true,
    avatarInitials: "BS"
  },
  {
    id: "fac-26",
    name: "Ms. Ayesha Tariq",
    designation: "Lecturer",
    department: "Software Engineering",
    officeRoom: "Room A-107",
    block: "Block A",
    floor: "1st Floor",
    email: "ayesha.tariq@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 254",
    consultationHours: "Tue / Thu: 11:00 AM – 01:00 PM",
    researchFocus: "Requirements Engineering & Human-Computer Interaction",
    isAvailableToday: true,
    avatarInitials: "AT"
  },
  {
    id: "fac-27",
    name: "Mr. Hassan Raza",
    designation: "Lecturer",
    department: "Electrical Engineering",
    officeRoom: "Room B-106",
    block: "Block B",
    floor: "1st Floor",
    email: "hassan.raza@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 319",
    consultationHours: "Mon / Wed: 01:30 PM – 03:00 PM",
    researchFocus: "Circuit Analysis, Power Systems & Control Lab",
    isAvailableToday: true,
    avatarInitials: "HR"
  },
  {
    id: "fac-28",
    name: "Ms. Sana Malik",
    designation: "Lecturer",
    department: "Computer Science",
    officeRoom: "Room C-110",
    block: "Block C",
    floor: "1st Floor",
    email: "sana.malik@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 258",
    consultationHours: "Wed / Fri: 10:30 AM – 12:30 PM",
    researchFocus: "Data Structures, Algorithms & Competitive Programming",
    isAvailableToday: true,
    avatarInitials: "SM"
  },
  {
    id: "fac-29",
    name: "Mr. Ali Shahzad",
    designation: "Lecturer",
    department: "Mechanical Engineering",
    officeRoom: "Room B-108",
    block: "Block B",
    floor: "1st Floor",
    email: "ali.shahzad@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 545",
    consultationHours: "Tue / Thu: 09:30 AM – 11:30 AM",
    researchFocus: "Thermodynamics, CAD Modeling & Manufacturing Systems",
    isAvailableToday: true,
    avatarInitials: "AS"
  },
  {
    id: "fac-22",
    name: "Dr. Farah Naz",
    designation: "Associate Professor",
    department: "Chemistry",
    officeRoom: "Room B-206",
    block: "Block B",
    floor: "2nd Floor",
    email: "farah.naz@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 518",
    consultationHours: "Mon / Wed: 01:00 PM – 02:30 PM",
    researchFocus: "Organic Reaction Mechanisms & Pharmaceutical Chemistry",
    isAvailableToday: true,
    avatarInitials: "FN"
  },
  {
    id: "fac-23",
    name: "Dr. Salman Qureshi",
    designation: "Tenured Professor",
    department: "Civil Engineering",
    officeRoom: "Room B-208",
    block: "Block B",
    floor: "2nd Floor",
    email: "salman.qureshi@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 529",
    consultationHours: "Tue / Thu: 10:00 AM – 12:00 PM",
    researchFocus: "Transportation Geometrics & Urban Water Hydrology",
    isAvailableToday: true,
    avatarInitials: "SQ"
  },
  {
    id: "fac-24",
    name: "Dr. Zainab Bibi",
    designation: "Associate Professor",
    department: "Food Science",
    officeRoom: "Room D-205",
    block: "Block D",
    floor: "2nd Floor",
    email: "zainab.bibi@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 509",
    consultationHours: "Wed / Fri: 09:30 AM – 11:30 AM",
    researchFocus: "Post-Harvest Food Biotechnology & Functional Foods",
    isAvailableToday: false,
    avatarInitials: "ZB"
  },
  {
    id: "fac-25",
    name: "Dr. Nasir Mehmood",
    designation: "Tenured Professor",
    department: "Mathematics",
    officeRoom: "Room A-209",
    block: "Block A",
    floor: "2nd Floor",
    email: "nasir.mehmood@cuisahiwal.edu.pk",
    phoneExtension: "Ext. 541",
    consultationHours: "Mon / Thu: 11:00 AM – 01:00 PM",
    researchFocus: "Numerical Analysis, Linear Algebra & Cryptography",
    isAvailableToday: true,
    avatarInitials: "NM"
  }
];

export const CAMPUS_LIBRARY_INFO = {
  blockName: "D Block",
  location: "Ground Floor, Central Academic Concourse (Next to Auditorium)"
} as const;

export const ADMINISTRATIVE_OFFICES: AdministrativeOffice[] = [
  {
    id: "adm-6",
    name: "Admission Office",
    category: "Administration",
    officeRoom: "Room A-102 (Admissions Wing)",
    block: "Block A",
    floor: "1st Floor",
    headOfficer: "Mr. Kamran Javed",
    headTitle: "Admissions Officer",
    email: "admissions@cuisahiwal.edu.pk",
    phone: "+92 300 1234567",
    phoneExtension: "Ext. 105",
    workingHours: "08:30 AM – 04:30 PM (Mon – Fri)",
    currentTicketServing: 18,
    queueLength: 3,
    avgWaitMinutes: 6,
    counterStatus: "OPEN",
    servicesOffered: [
      "Undergraduate & Graduate Admissions",
      "Merit List & Document Verification",
      "Entry Test & Program Transfers"
    ]
  },
  {
    id: "adm-3",
    name: "Exam Office",
    category: "Academic Records",
    officeRoom: "Room B-02 (Examinations Wing)",
    block: "Block B",
    floor: "Ground Floor",
    headOfficer: "Dr. Farooq Tariq",
    headTitle: "Controller of Examinations",
    email: "exams@cuisahiwal.edu.pk",
    phone: "+92 311 9876543",
    phoneExtension: "Ext. 410",
    workingHours: "08:30 AM – 04:30 PM (Mon – Fri)",
    currentTicketServing: 19,
    queueLength: 2,
    avgWaitMinutes: 5,
    counterStatus: "OPEN",
    servicesOffered: [
      "Official Transcript Requests",
      "Exam Paper Rechecking Applications",
      "Graduation Clearance Verification",
      "Duplicate Admit Card Issuance"
    ]
  },
  {
    id: "adm-2",
    name: "Accounts Office",
    category: "Finance & Accounts",
    officeRoom: "Room AD-201 (Finance Arcade)",
    block: "Admin Block",
    floor: "2nd Floor",
    headOfficer: "Mr. Khurram Shahzad",
    headTitle: "Treasurer & Accounts Officer",
    email: "accounts@cuisahiwal.edu.pk",
    phone: "+92 322 7654321",
    phoneExtension: "Ext. 115",
    workingHours: "09:00 AM – 03:30 PM (Mon – Fri)",
    currentTicketServing: 88,
    queueLength: 9,
    avgWaitMinutes: 14,
    counterStatus: "BUSY",
    servicesOffered: [
      "Semester Fee Challan Inquiries",
      "Installment & Scholarship Disbursals",
      "Hostel & Transport Dues Reconciliation",
      "Refund & Caution Money Vouchers"
    ]
  },
  {
    id: "adm-1",
    name: "Registrar Office",
    category: "Academic Records",
    officeRoom: "Room C-101 (Academic Records)",
    block: "Block C",
    floor: "1st Floor",
    headOfficer: "Mr. Muhammad Nawaz",
    headTitle: "Deputy Registrar",
    email: "registrar@cuisahiwal.edu.pk",
    phone: "+92 333 4567890",
    phoneExtension: "Ext. 110",
    workingHours: "08:30 AM – 04:30 PM (Mon – Fri)",
    currentTicketServing: 42,
    queueLength: 4,
    avgWaitMinutes: 8,
    counterStatus: "OPEN",
    servicesOffered: [
      "Degree & Transcript Verification",
      "Enrollment & Bonafide Certificates",
      "Course Drop / Semester Freeze Requests",
      "Migration & NOC Processing"
    ]
  },
  {
    id: "adm-4",
    name: "Career Placement Cell",
    category: "Student Support",
    officeRoom: "Room D-106",
    block: "Block D",
    floor: "1st Floor",
    headOfficer: "Ms. Sadia Perveen",
    headTitle: "Director Career Services",
    email: "careers@cuisahiwal.edu.pk",
    phone: "+92 301 2345678",
    phoneExtension: "Ext. 420",
    workingHours: "09:00 AM – 04:00 PM (Mon – Fri)",
    currentTicketServing: 11,
    queueLength: 1,
    avgWaitMinutes: 3,
    counterStatus: "OPEN",
    servicesOffered: [
      "Software House Internship Recommendations",
      "Campus Recruitment Drives & Job Fairs",
      "Resume & Technical Mock Interviews",
      "Alumni Mentorship Networking"
    ]
  },
  {
    id: "adm-5",
    name: "Campus Medical Center",
    category: "Health & Safety",
    officeRoom: "Room B-Ground-01 (Medical Dispensary)",
    block: "Block B",
    floor: "Ground Floor",
    headOfficer: "Dr. Zahida Khan",
    headTitle: "Chief Medical Officer",
    email: "medical@cuisahiwal.edu.pk",
    phone: "+92 304 5550119",
    phoneExtension: "Ext. 119",
    workingHours: "24/7 On-Call Emergency Service",
    currentTicketServing: 6,
    queueLength: 0,
    avgWaitMinutes: 0,
    counterStatus: "OPEN",
    servicesOffered: [
      "Immediate Medical First-Aid & Triage",
      "Ambulance Transfer to DHQ Hospital",
      "Medical Leave Certificates Examination",
      "Routine Health Consultations & OTC Dispensary"
    ]
  }
];

export const CLASSROOMS_LABS: ClassroomLab[] = [
  // Block C - Computer Science
  {
    id: "rm-c204",
    roomCode: "Room C-204",
    name: "Smart Lecture Hall (BCS-7C Designated)",
    type: "Smart Classroom",
    block: "Block C",
    floor: "2nd Floor",
    capacity: 60,
    equipment: {
      projectorsCount: 1,
      workstationsCount: 0,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: true,
      hasSmartPodium: true
    },
    currentActivity: "CSC-354 Compiler Construction Lecture",
    inCharge: "Dr. Munir Ahmad"
  },
  {
    id: "rm-c201",
    roomCode: "Room C-201",
    name: "Senior Lecture Room (BCS-7A Designated)",
    type: "Smart Classroom",
    block: "Block C",
    floor: "2nd Floor",
    capacity: 65,
    equipment: {
      projectorsCount: 1,
      workstationsCount: 0,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: true,
      hasSmartPodium: true
    },
    currentActivity: "Available / Free for Study",
    inCharge: "Dr. Javed Iqbal"
  },
  {
    id: "rm-c301",
    roomCode: "Auditorium C-301",
    name: "Executive Computer Science Seminar Hall",
    type: "Seminar Hall",
    block: "Block C",
    floor: "3rd Floor",
    capacity: 120,
    equipment: {
      projectorsCount: 2,
      workstationsCount: 0,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: true,
      hasSmartPodium: true,
      specialGear: "Dual 4K Laser Projectors, Ceiling Array Microphones, Video Conferencing"
    },
    currentActivity: "MS-CS Thesis Defense Colloquium",
    inCharge: "CS Department Office"
  },

  // Engineering Labs
  {
    id: "lab-sw1",
    roomCode: "Software Lab 1",
    name: "Departmental Software Engineering Laboratory",
    type: "Computer Lab",
    block: "Engineering Labs",
    floor: "Ground Floor",
    capacity: 50,
    equipment: {
      projectorsCount: 1,
      workstationsCount: 50,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: true,
      hasSmartPodium: true,
      specialGear: "Core i7 Workstations, Dual Monitors, Linux/Windows Dual-boot"
    },
    currentActivity: "SE-4A Agile Scrum Lab",
    inCharge: "Engr. Farhan Tariq"
  },
  {
    id: "lab-ai-gpu",
    roomCode: "AI & Robotics Lab",
    name: "GPU Deep Learning & Automation Center",
    type: "Hardware/Engineering Lab",
    block: "Engineering Labs",
    floor: "Ground Floor",
    capacity: 40,
    equipment: {
      projectorsCount: 1,
      workstationsCount: 35,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: true,
      hasSmartPodium: true,
      specialGear: "8x NVIDIA RTX 4090 Workstations, TurtleBot ROS Hardware, CUDA Cluster"
    },
    currentActivity: "Available for Student AI Research",
    inCharge: "Dr. Ayesha Malik"
  },
  {
    id: "lab-cisco",
    roomCode: "Networks & Cyber Lab",
    name: "Cisco Certified Academy & Cybersecurity Lab",
    type: "Hardware/Engineering Lab",
    block: "Engineering Labs",
    floor: "1st Floor",
    capacity: 45,
    equipment: {
      projectorsCount: 1,
      workstationsCount: 45,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: false,
      hasSmartPodium: true,
      specialGear: "Cisco 2900 Series Routers & Catalysts Racks, Packet Sniffing Bench"
    },
    currentActivity: "CNS-411 Ethical Hacking Practical",
    inCharge: "Engr. Bilal Khalid"
  },

  // Block A - Natural Sciences & Engineering
  {
    id: "rm-a102",
    roomCode: "Room A-102",
    name: "Natural Sciences Smart Lecture Room",
    type: "Smart Classroom",
    block: "Block A",
    floor: "1st Floor",
    capacity: 60,
    equipment: {
      projectorsCount: 1,
      workstationsCount: 0,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: true,
      hasSmartPodium: true
    },
    currentActivity: "Available for Study",
    inCharge: "Natural Sciences Dept"
  },
  {
    id: "rm-a201",
    roomCode: "Theater A-201",
    name: "Engineering Lecture Theater 1",
    type: "Lecture Theater",
    block: "Block A",
    floor: "2nd Floor",
    capacity: 75,
    equipment: {
      projectorsCount: 1,
      workstationsCount: 0,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: true,
      hasSmartPodium: false
    },
    currentActivity: "EEE-211 Electronic Devices",
    inCharge: "Electrical Eng Dept"
  },

  // Block D - Management Sciences & Central Concourse
  {
    id: "rm-d101",
    roomCode: "Room D-101",
    name: "Management Sciences Executive Classroom",
    type: "Smart Classroom",
    block: "Block D",
    floor: "1st Floor",
    capacity: 60,
    equipment: {
      projectorsCount: 1,
      workstationsCount: 0,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: true,
      hasSmartPodium: true
    },
    currentActivity: "Available / Free for Study",
    inCharge: "Management Sciences Dept"
  },
  {
    id: "rm-d-aud",
    roomCode: "Main Campus Auditorium",
    name: "Quaid-e-Azam Grand Auditorium",
    type: "Auditorium",
    block: "Block D",
    floor: "Ground Floor",
    capacity: 500,
    equipment: {
      projectorsCount: 2,
      workstationsCount: 0,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: true,
      hasSmartPodium: true,
      specialGear: "Concert PA System, Motorized 20-Foot Drop Screen, Theatrical Stage Lights"
    },
    currentActivity: "Sports Week 2026 Orientation Prep",
    inCharge: "Directorate of Student Affairs"
  },
  // Additional Block A, B, C, D Classrooms for complete floor-by-floor directory
  {
    id: "rm-a02",
    roomCode: "Room A-02",
    name: "Foundation Sciences Lecture Hall",
    type: "Lecture Theater",
    block: "Block A",
    floor: "Ground Floor",
    capacity: 70,
    equipment: {
      projectorsCount: 1,
      workstationsCount: 0,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: true,
      hasSmartPodium: false
    },
    currentActivity: "PHY-101 Applied Physics",
    inCharge: "Natural Sciences Dept"
  },
  {
    id: "rm-b01",
    roomCode: "Room B-01",
    name: "Electrical Circuits Foundation Room",
    type: "Smart Classroom",
    block: "Block B",
    floor: "Ground Floor",
    capacity: 55,
    equipment: {
      projectorsCount: 1,
      workstationsCount: 0,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: true,
      hasSmartPodium: true
    },
    currentActivity: "BEE-1A Basic Electronics",
    inCharge: "Electrical Eng Dept"
  },
  {
    id: "rm-b101",
    roomCode: "Room B-101",
    name: "Circuit Theory Smart Room",
    type: "Smart Classroom",
    block: "Block B",
    floor: "1st Floor",
    capacity: 55,
    equipment: {
      projectorsCount: 1,
      workstationsCount: 0,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: true,
      hasSmartPodium: true
    },
    currentActivity: "BEE-3A Circuits Analysis",
    inCharge: "Electrical Eng Dept"
  },
  {
    id: "rm-b202",
    roomCode: "Room B-202",
    name: "Mechanical CAD & Design Hall",
    type: "Computer Lab",
    block: "Block B",
    floor: "2nd Floor",
    capacity: 48,
    equipment: {
      projectorsCount: 1,
      workstationsCount: 48,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: true,
      hasSmartPodium: true,
      specialGear: "SolidWorks & AutoCAD Workstations"
    },
    currentActivity: "Mechanical Modeling Practical",
    inCharge: "Mechanical Eng Dept"
  },
  {
    id: "rm-c101",
    roomCode: "Room C-101",
    name: "Operating Systems Lecture Room (BCS-7A)",
    type: "Smart Classroom",
    block: "Block C",
    floor: "1st Floor",
    capacity: 65,
    equipment: {
      projectorsCount: 1,
      workstationsCount: 0,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: true,
      hasSmartPodium: true
    },
    currentActivity: "CSC-322 Operating Systems",
    inCharge: "Dr. Muhammad Asim"
  },
  {
    id: "rm-c102",
    roomCode: "Room C-102",
    name: "Software Engineering Hall (BCS-7C)",
    type: "Smart Classroom",
    block: "Block C",
    floor: "1st Floor",
    capacity: 65,
    equipment: {
      projectorsCount: 1,
      workstationsCount: 0,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: true,
      hasSmartPodium: false
    },
    currentActivity: "CSC-371 Software Engineering",
    inCharge: "Dr. Majid Hussain"
  },
  {
    id: "rm-d202",
    roomCode: "Room D-202",
    name: "Business Analytics Seminar Room",
    type: "Seminar Hall",
    block: "Block D",
    floor: "2nd Floor",
    capacity: 50,
    equipment: {
      projectorsCount: 1,
      workstationsCount: 0,
      hasAC: true,
      hasWifi: true,
      hasAudioSystem: true,
      hasSmartPodium: true
    },
    currentActivity: "BBA-6A Quantitative Methods",
    inCharge: "Management Sciences Dept"
  }
];

export const LIBRARY_INTELLIGENCE: LibraryStatus = {
  totalSilentSeats: 140,
  availableSilentSeats: 48,
  collaborativePodsTotal: 6,
  collaborativePodsAvailable: 2,
  openingHours: "08:00 AM – 09:30 PM (Mon – Sat)",
  librarianOnDuty: "Mr. Tariq Bashir (Chief Librarian)",
  catalog: [
    {
      id: "bk-1",
      isbn: "978-0321486813",
      title: "Compilers: Principles, Techniques, and Tools (Dragon Book)",
      authors: "Alfred V. Aho, Monica S. Lam, Ravi Sethi, Jeffrey D. Ullman",
      edition: "2nd Edition (Pearson)",
      category: "Computer Science",
      shelfLocation: "Shelf CS-04 (2nd Floor)",
      floor: "1st Floor",
      totalCopies: 8,
      availableCopies: 3,
      isAvailable: true,
      digitalPdfAvailable: true
    },
    {
      id: "bk-2",
      isbn: "978-1119800361",
      title: "Operating System Concepts",
      authors: "Abraham Silberschatz, Peter B. Galvin, Greg Gagne",
      edition: "10th Edition (Wiley)",
      category: "Computer Science",
      shelfLocation: "Shelf CS-08 (2nd Floor)",
      floor: "1st Floor",
      totalCopies: 12,
      availableCopies: 5,
      isAvailable: true,
      digitalPdfAvailable: true
    },
    {
      id: "bk-3",
      isbn: "978-0262033848",
      title: "Introduction to Algorithms (CLRS)",
      authors: "Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein",
      edition: "3rd Edition (MIT Press)",
      category: "Computer Science",
      shelfLocation: "Shelf CS-02 (2nd Floor)",
      floor: "1st Floor",
      totalCopies: 10,
      availableCopies: 0,
      isAvailable: false,
      digitalPdfAvailable: true
    },
    {
      id: "bk-4",
      isbn: "978-0132350884",
      title: "Clean Code: A Handbook of Agile Software Craftsmanship",
      authors: "Robert C. Martin",
      edition: "1st Edition (Prentice Hall)",
      category: "Computer Science",
      shelfLocation: "Shelf CS-11 (2nd Floor)",
      floor: "1st Floor",
      totalCopies: 6,
      availableCopies: 2,
      isAvailable: true,
      digitalPdfAvailable: false
    },
    {
      id: "bk-5",
      isbn: "978-0262035613",
      title: "Deep Learning",
      authors: "Ian Goodfellow, Yoshua Bengio, Aaron Courville",
      edition: "Adaptive Computation (MIT Press)",
      category: "Computer Science",
      shelfLocation: "Shelf CS-15 (2nd Floor)",
      floor: "1st Floor",
      totalCopies: 5,
      availableCopies: 2,
      isAvailable: true,
      digitalPdfAvailable: true
    },
    {
      id: "bk-6",
      isbn: "978-0073380445",
      title: "Fundamentals of Electric Circuits",
      authors: "Charles K. Alexander, Matthew N.O. Sadiku",
      edition: "5th Edition (McGraw-Hill)",
      category: "Electrical Eng",
      shelfLocation: "Shelf EE-03 (1st Floor)",
      floor: "Ground Floor",
      totalCopies: 14,
      availableCopies: 6,
      isAvailable: true,
      digitalPdfAvailable: true
    }
  ]
};

// ================= FLOOR PLANS BLUEPRINT DATA =================

export const FLOOR_BLUEPRINTS: Record<string, FloorBlueprintLayout> = {
  "Block C - 2nd Floor": {
    block: "Block C",
    floor: "2nd Floor",
    corridorDescription: "Main Computer Science Academic Wing corridor connecting BCS Classrooms with Faculty Advisory Suites.",
    emergencyExits: "East Fire Stairwell & West Central Elevator Lobby",
    rooms: [
      { code: "Stairs / Lobby", name: "Central Elevator & Fire Staircase", type: "amenity", gridCol: "col-span-1" },
      { code: "Room C-201", name: "Senior Lecture Hall (BCS-7A)", type: "classroom", gridCol: "col-span-2", statusText: "Free Now" },
      { code: "Restrooms", name: "Faculty & Student Restrooms", type: "amenity", gridCol: "col-span-1" },
      { code: "Room C-202", name: "BCS-5A Lecture Room", type: "classroom", gridCol: "col-span-2", statusText: "Class in Session" },
      { code: "Room C-204", name: "Smart Lecture Hall (BCS-7C)", type: "classroom", gridCol: "col-span-2", statusText: "Compiler Construction" },
      { code: "Room C-205", name: "Dr. Javed Iqbal (Batch Advisor)", type: "office", gridCol: "col-span-1", statusText: "Office Open" },
      { code: "Room C-208", name: "Dr. Ayesha Malik (Faculty Office)", type: "office", gridCol: "col-span-1", statusText: "Office Open" },
      { code: "Student Lounge", name: "CS Collaborative Quad Hub", type: "hall", gridCol: "col-span-2", statusText: "Open 24/7" }
    ]
  },
  "Block C - 3rd Floor": {
    block: "Block C",
    floor: "3rd Floor",
    corridorDescription: "Department Secretariat, HOD Directorate & Graduate Research Suite.",
    emergencyExits: "East Fire Stairwell",
    rooms: [
      { code: "Stairs / Lobby", name: "Central Staircase Access", type: "amenity", gridCol: "col-span-1" },
      { code: "Room C-301", name: "HOD Secretariat & Dr. Munir Office", type: "office", gridCol: "col-span-2", statusText: "In Office" },
      { code: "Room C-302", name: "Postgraduate Research Suite", type: "lab", gridCol: "col-span-2", statusText: "MS-CS Research" },
      { code: "Executive Hall", name: "Executive Seminar Hall C-301", type: "hall", gridCol: "col-span-3", statusText: "Thesis Defense" }
    ]
  },
  "Block A - 1st Floor": {
    block: "Block A",
    floor: "1st Floor",
    corridorDescription: "University Central Administration, Registrar Wing & Accounts Arcade.",
    emergencyExits: "Main North Portico & West Ramp",
    rooms: [
      { code: "Main Entrance", name: "Portico & Security Reception", type: "amenity", gridCol: "col-span-1" },
      { code: "Room A-101", name: "Registrar Office & Records", type: "office", gridCol: "col-span-2", statusText: "Serving #42" },
      { code: "Room A-105", name: "Accounts & Fee Cashier Arcade", type: "office", gridCol: "col-span-2", statusText: "Serving #88" },
      { code: "Room A-102", name: "Natural Sciences Smart Room", type: "classroom", gridCol: "col-span-2", statusText: "Free Now" },
      { code: "Waiting Concourse", name: "Public Waiting Arcade", type: "hall", gridCol: "col-span-1" }
    ]
  },
  "Engineering Labs - Ground Floor": {
    block: "Engineering Labs",
    floor: "Ground Floor",
    corridorDescription: "High-power computing and hardware research arcade with dedicated clean-power feeder.",
    emergencyExits: "South Industrial Loading Bay & East Fire Exit",
    rooms: [
      { code: "Lab Entrance", name: "Turnstile Card Access Portal", type: "amenity", gridCol: "col-span-1" },
      { code: "Software Lab 1", name: "Departmental Software Lab", type: "lab", gridCol: "col-span-3", statusText: "SE-4A Scrum" },
      { code: "AI & Robotics", name: "GPU Deep Learning & Automation Center", type: "lab", gridCol: "col-span-3", statusText: "RTX 4090 Bench" },
      { code: "Server Vault", name: "Campus Datacenter & Fiber Hub", type: "amenity", gridCol: "col-span-1", statusText: "Authorized Only" }
    ]
  }
};

export interface CampusStatisticMetric {
  label: string;
  value: string;
  sublabel: string;
}

export interface DepartmentEnrollmentStat {
  department: string;
  code: string;
  students: number;
  faculty: number;
  labs: number;
}

export const CAMPUS_STATISTICS: {
  overview: CampusStatisticMetric[];
  departments: DepartmentEnrollmentStat[];
} = {
  overview: [
    { label: "Total Enrolled Students", value: "4,850+", sublabel: "Undergraduate & Graduate programs" },
    { label: "Faculty & Teaching Staff", value: "215", sublabel: "PhD Professors, HODs & Lecturers" },
    { label: "Academic Blocks", value: "5", sublabel: "Blocks A, B, C, D & Engineering Labs" },
    { label: "Classrooms & Theaters", value: "68", sublabel: "Multimedia & smart lecture rooms" },
    { label: "Specialized Labs", value: "24", sublabel: "Computing, AI/GPU, Cisco & Engineering" },
    { label: "Central Library Capacity", value: "140 Desks", sublabel: "Plus 6 collaborative study pods & 42k+ volumes" },
    { label: "University Fleet", value: "18 Buses", sublabel: "City commuter lines & intra-campus shuttles" },
    { label: "Student Societies", value: "16 Active", sublabel: "Tech, Sports, Literary & Entrepreneurship" }
  ],
  departments: [
    { department: "Computer Science", code: "BCS / MCS", students: 1620, faculty: 64, labs: 9 },
    { department: "Software Engineering", code: "BSE", students: 1180, faculty: 46, labs: 5 },
    { department: "Electrical Engineering", code: "BEE", students: 740, faculty: 38, labs: 6 },
    { department: "Management Sciences", code: "BBA / MBA", students: 820, faculty: 41, labs: 2 },
    { department: "Mechanical & Sciences", code: "BME / BS", students: 490, faculty: 26, labs: 2 }
  ]
};

export type ClassroomBlockName = "Block A" | "Block B" | "Block C";
export type ClassroomFloorName = "Ground Floor" | "1st Floor" | "2nd Floor" | "3rd Floor";

export interface BlockClassroomItem {
  id: string;
  roomCode: string;
  name: string;
  block: ClassroomBlockName;
  floor: ClassroomFloorName;
  capacity: number;
  hasAC: boolean;
  hasWifi: boolean;
  hasProjector: boolean;
}

function makeRoom(
  block: ClassroomBlockName,
  floor: ClassroomFloorName,
  roomCode: string,
  capacity: number,
  name?: string
): BlockClassroomItem {
  const idSlug = `${block.toLowerCase().replace(/\s+/g, "-")}-${roomCode.toLowerCase().replace(/[^a-z0-9]+/g, "-")}`;
  return {
    id: idSlug,
    roomCode,
    name: name ?? `Classroom ${roomCode}`,
    block,
    floor,
    capacity,
    hasAC: true,
    hasWifi: true,
    hasProjector: true
  };
}

export const BLOCK_CLASSROOMS: BlockClassroomItem[] = [
  // Block A — 20 Classrooms (Ground: 7, 1st: 7, 2nd: 6)
  makeRoom("Block A", "Ground Floor", "A-1", 60, "Lecture Hall A-1"),
  makeRoom("Block A", "Ground Floor", "A-2", 45, "Smart Classroom A-2"),
  makeRoom("Block A", "Ground Floor", "A-3", 55, "Classroom A-3"),
  makeRoom("Block A", "Ground Floor", "A-4", 40, "Classroom A-4"),
  makeRoom("Block A", "Ground Floor", "A-5", 50, "Classroom A-5"),
  makeRoom("Block A", "Ground Floor", "A-6", 38, "Classroom A-6"),
  makeRoom("Block A", "Ground Floor", "A-7", 48, "Classroom A-7"),

  makeRoom("Block A", "1st Floor", "A-1.1", 70, "Lecture Hall A-1.1"),
  makeRoom("Block A", "1st Floor", "A-1.2", 65, "Classroom A-1.2"),
  makeRoom("Block A", "1st Floor", "A-1.3", 60, "Classroom A-1.3"),
  makeRoom("Block A", "1st Floor", "A-1.4", 55, "Classroom A-1.4"),
  makeRoom("Block A", "1st Floor", "A-1.5", 50, "Classroom A-1.5"),
  makeRoom("Block A", "1st Floor", "A-1.6", 45, "Classroom A-1.6"),
  makeRoom("Block A", "1st Floor", "A-1.7", 40, "Classroom A-1.7"),

  makeRoom("Block A", "2nd Floor", "A-2.1", 65, "Lecture Hall A-2.1"),
  makeRoom("Block A", "2nd Floor", "A-2.2", 60, "Classroom A-2.2"),
  makeRoom("Block A", "2nd Floor", "A-2.3", 55, "Classroom A-2.3"),
  makeRoom("Block A", "2nd Floor", "A-2.4", 50, "Classroom A-2.4"),
  makeRoom("Block A", "2nd Floor", "A-2.5", 45, "Classroom A-2.5"),
  makeRoom("Block A", "2nd Floor", "A-2.6", 40, "Classroom A-2.6"),

  // Block B — 18 Classrooms (Ground: 6, 1st: 5, 2nd: 4, 3rd: 3)
  makeRoom("Block B", "Ground Floor", "B-1", 70, "Engineering Hall B-1"),
  makeRoom("Block B", "Ground Floor", "B-2", 65, "Classroom B-2"),
  makeRoom("Block B", "Ground Floor", "B-3", 60, "Classroom B-3"),
  makeRoom("Block B", "Ground Floor", "B-4", 55, "Classroom B-4"),
  makeRoom("Block B", "Ground Floor", "B-5", 50, "Classroom B-5"),
  makeRoom("Block B", "Ground Floor", "B-6", 45, "Classroom B-6"),

  makeRoom("Block B", "1st Floor", "B-1.1", 65, "Smart Classroom B-1.1"),
  makeRoom("Block B", "1st Floor", "B-1.2", 60, "Classroom B-1.2"),
  makeRoom("Block B", "1st Floor", "B-1.3", 55, "Classroom B-1.3"),
  makeRoom("Block B", "1st Floor", "B-1.4", 50, "Classroom B-1.4"),
  makeRoom("Block B", "1st Floor", "B-1.5", 45, "Classroom B-1.5"),

  makeRoom("Block B", "2nd Floor", "B-2.1", 60, "Classroom B-2.1"),
  makeRoom("Block B", "2nd Floor", "B-2.2", 55, "Classroom B-2.2"),
  makeRoom("Block B", "2nd Floor", "B-2.3", 50, "Classroom B-2.3"),
  makeRoom("Block B", "2nd Floor", "B-2.4", 45, "Classroom B-2.4"),

  makeRoom("Block B", "3rd Floor", "B-3.1", 50, "Classroom B-3.1"),
  makeRoom("Block B", "3rd Floor", "B-3.2", 45, "Classroom B-3.2"),
  makeRoom("Block B", "3rd Floor", "B-3.3", 40, "Classroom B-3.3"),

  // Block C — 18 Classrooms (Ground: 6, 1st: 5, 2nd: 5, 3rd: 2)
  makeRoom("Block C", "Ground Floor", "C-1", 65, "CS Lecture Hall C-1"),
  makeRoom("Block C", "Ground Floor", "C-2", 60, "Classroom C-2"),
  makeRoom("Block C", "Ground Floor", "C-3", 55, "Classroom C-3"),
  makeRoom("Block C", "Ground Floor", "C-4", 50, "Classroom C-4"),
  makeRoom("Block C", "Ground Floor", "C-5", 45, "Classroom C-5"),
  makeRoom("Block C", "Ground Floor", "C-6", 40, "Classroom C-6"),

  makeRoom("Block C", "1st Floor", "C-101", 65, "Operating Systems Room C-101"),
  makeRoom("Block C", "1st Floor", "C-102", 65, "Software Eng Hall C-102"),
  makeRoom("Block C", "1st Floor", "C-103", 60, "Classroom C-103"),
  makeRoom("Block C", "1st Floor", "C-104", 55, "Classroom C-104"),
  makeRoom("Block C", "1st Floor", "C-105", 50, "Classroom C-105"),

  makeRoom("Block C", "2nd Floor", "C-201", 65, "Senior Lecture Room C-201"),
  makeRoom("Block C", "2nd Floor", "C-202", 60, "Classroom C-202"),
  makeRoom("Block C", "2nd Floor", "C-203", 55, "Classroom C-203"),
  makeRoom("Block C", "2nd Floor", "C-204", 60, "Smart Lecture Hall C-204"),
  makeRoom("Block C", "2nd Floor", "C-205", 50, "Classroom C-205"),

  makeRoom("Block C", "3rd Floor", "C-302", 45, "Classroom C-302"),
  makeRoom("Block C", "3rd Floor", "C-303", 40, "Classroom C-303")
];

export type LabBlockLabel = "A Block" | "B Block" | "C Block";

export interface CampusLabItem {
  id: string;
  name: string;
  block: LabBlockLabel;
  floor: string;
  seats: number;
  computersCount: number;
  inCharge: string;
  description: string;
  hasWifi: boolean;
  hasAC: boolean;
  hasProjector: boolean;
}

export const CAMPUS_LABS_DIRECTORY: CampusLabItem[] = [
  {
    id: "lab-c6",
    name: "C Lab - 6",
    block: "C Block",
    floor: "1st Floor",
    seats: 50,
    computersCount: 50,
    inCharge: "Engr. Farhan Tariq",
    description: "Computer lab for coding classes, software practice, and student lab exams.",
    hasWifi: true,
    hasAC: true,
    hasProjector: true
  },
  {
    id: "lab-c8",
    name: "C Lab - 8",
    block: "A Block",
    floor: "G Floor",
    seats: 45,
    computersCount: 45,
    inCharge: "Dr. Ayesha Malik",
    description: "Ground floor computer lab with fast campus internet and dual-boot systems.",
    hasWifi: true,
    hasAC: true,
    hasProjector: true
  },
  {
    id: "lab-physics",
    name: "Physics Lab",
    block: "A Block",
    floor: "2nd Floor",
    seats: 40,
    computersCount: 0,
    inCharge: "Dr. Tariq Mehmood",
    description: "Physics experiment benches for optics, mechanics, and basic circuits.",
    hasWifi: true,
    hasAC: true,
    hasProjector: true
  },
  {
    id: "lab-bio",
    name: "Biosciences Lab",
    block: "B Block",
    floor: "1st Floor",
    seats: 36,
    computersCount: 0,
    inCharge: "Dr. Sanaullah",
    description: "Life sciences laboratory equipped with microscopes and clean lab benches.",
    hasWifi: true,
    hasAC: true,
    hasProjector: false
  },
  {
    id: "lab-chem",
    name: "Chemistry Lab",
    block: "A Block",
    floor: "1st Floor",
    seats: 38,
    computersCount: 0,
    inCharge: "Dr. Nadia Bibi",
    description: "Chemistry practical hall with safety hoods, glassware, and water stations.",
    hasWifi: true,
    hasAC: true,
    hasProjector: false
  },
  {
    id: "lab-sw1",
    name: "Software Lab 1",
    block: "C Block",
    floor: "G Floor",
    seats: 50,
    computersCount: 50,
    inCharge: "Engr. Bilal Khan",
    description: "Software and artificial intelligence lab used for senior projects.",
    hasWifi: true,
    hasAC: true,
    hasProjector: true
  },
  {
    id: "lab-net",
    name: "Networks Lab",
    block: "B Block",
    floor: "2nd Floor",
    seats: 45,
    computersCount: 45,
    inCharge: "Engr. Bilal Khalid",
    description: "Networking lab with routers, switches, and computer security test racks.",
    hasWifi: true,
    hasAC: true,
    hasProjector: true
  }
];
