export interface EnrolledCourse {
  id: string;
  code: string;
  title: string;
  creditHours: number;
  section: string;
  semester: string;
  teacher: {
    name: string;
    role: string;
    avatar: string;
    status: "Available in Office" | "In Lecture" | "Consultation Hours";
    office: string;
    email: string;
    officeHours: string;
    bio: string;
  };
  attendance: {
    percentage: number;
    attended: number;
    total: number;
    absent: number;
    late: number;
    excused: number;
    requiredConsecutive: number;
  };
  standing: {
    estimatedGrade: string;
    scorePercentage: number;
    gpa: string;
    nextDeadline: string;
  };
  overview: {
    description: string;
    objectives: string[];
    prerequisites: string;
    textbooks: { title: string; author: string; edition: string }[];
    gradingPolicy: { item: string; weight: string; description: string }[];
    announcements: {
      id: string;
      title: string;
      date: string;
      content: string;
      isPinned?: boolean;
      author: string;
    }[];
  };
  coursework: {
    assignments: {
      id: string;
      title: string;
      dueDate: string;
      maxPoints: number;
      weight: string;
      status: "Pending" | "Submitted" | "Graded";
      submittedFile?: string;
      submittedAt?: string;
      obtainedScore?: number;
      feedback?: string;
    }[];
    quizzes: {
      id: string;
      title: string;
      date: string;
      maxPoints: number;
      obtainedScore: number;
      classAverage: number;
      topics: string;
    }[];
    exams: {
      id: string;
      title: string;
      date: string;
      maxPoints: number;
      obtainedScore?: number;
      classAverage?: number;
      status: "Upcoming" | "Completed";
    }[];
  };
  attendanceLedger: {
    id: string;
    lectureNo: number;
    date: string;
    day: string;
    slot: string;
    room: string;
    topic: string;
    status: "PRESENT" | "ABSENT" | "LATE" | "EXCUSED";
    notes?: string;
  }[];
  leaveRequests: {
    id: string;
    lectureNo: number;
    date: string;
    reason: string;
    documentName?: string;
    submittedAt: string;
    status: "Pending" | "Approved" | "Rejected";
    adminRemarks?: string;
  }[];
  lectureHub: {
    recordings: {
      id: string;
      lectureNo: number;
      title: string;
      date: string;
      duration: string;
      videoUrl?: string;
      timestamps: { time: string; label: string }[];
      slidesUrl?: string;
    }[];
    materials: {
      id: string;
      title: string;
      category: "Slides" | "Textbook" | "Handout" | "Code";
      format: "PDF" | "PPTX" | "ZIP" | "DOCX";
      size: string;
      uploadDate: string;
      downloadsCount: number;
    }[];
  };
}

export const COURSES_CATALOG: EnrolledCourse[] = [
  {
    id: "compiler",
    code: "CSC-354",
    title: "Compiler Construction",
    creditHours: 3,
    section: "BCS-7C",
    semester: "7th Semester · Fall 2026",
    teacher: {
      name: "Dr. Munir Ahmad",
      role: "Associate Professor / Batch Advisor",
      avatar: "MA",
      status: "Available in Office",
      office: "A Block, 3rd Floor, Room A-301",
      email: "drmunir@cuisahiwal.edu.pk",
      officeHours: "Mon & Wed: 11:45 AM – 01:15 PM",
      bio: "Ph.D. in Computer Science with 14+ years research expertise in compiler optimization, program analysis, and runtime verification systems."
    },
    attendance: {
      percentage: 68.5,
      attended: 14,
      total: 20,
      absent: 5,
      late: 1,
      excused: 1,
      requiredConsecutive: 4
    },
    standing: {
      estimatedGrade: "84.5% · A-",
      scorePercentage: 84.5,
      gpa: "3.67",
      nextDeadline: "Assignment 2: LL(1) Parser due tomorrow at 11:59 PM"
    },
    overview: {
      description: "Principles of modern compiler design, focusing on lexical analysis, context-free grammars, deterministic syntax analysis, syntax-directed translation, symbol tables, intermediate code representation, and target code generation.",
      objectives: [
        "Design lexical analyzers using deterministic finite automata (DFA) and regular expressions.",
        "Construct top-down LL(1) and bottom-up LR(1) parsers with syntax error recovery.",
        "Implement intermediate representation (Three-Address Code) and optimization passes."
      ],
      prerequisites: "Theory of Automata (CSC-312), Data Structures & Algorithms (CSC-211)",
      textbooks: [
        { title: "Compilers: Principles, Techniques, and Tools", author: "Aho, Lam, Sethi, Ullman (Dragon Book)", edition: "2nd Edition" },
        { title: "Engineering a Compiler", author: "Keith D. Cooper, Linda Torczon", edition: "2nd Edition" }
      ],
      gradingPolicy: [
        { item: "Quizzes (Best 3 of 4)", weight: "15%", description: "Surprise and scheduled conceptual tests." },
        { item: "Assignments & Projects (4 Total)", weight: "10%", description: "Lexer, Parser, and AST compiler deliverables." },
        { item: "Mid-Term Examination", weight: "25%", description: "Comprehensive coverage of Lexical and Top-Down parsing." },
        { item: "Terminal Final Examination", weight: "50%", description: "Comprehensive final exam covering all 6 compiler phases." }
      ],
      announcements: [
        {
          id: "an-1",
          title: "Assignment 2 Deadline Extension & Lab Assistance",
          date: "Yesterday at 04:15 PM",
          content: "Due to student requests, Assignment 2 (LL(1) Parsing Table Construction) deadline has been extended to tomorrow midnight (11:59 PM). TA office hours will be held in C-01 Lab.",
          isPinned: true,
          author: "Dr. Munir Ahmad"
        },
        {
          id: "an-2",
          title: "Midterm Evaluation Papers Review Session",
          date: "May 10, 2026",
          content: "Midterm answer scripts will be reviewed during office hours on Thursday from 11:45 AM to 01:15 PM in Room A-301. Bring your student ID card.",
          isPinned: false,
          author: "Dr. Munir Ahmad"
        }
      ]
    },
    coursework: {
      assignments: [
        {
          id: "as-1",
          title: "Assignment 1: Lexical Analyzer with Flex",
          dueDate: "Oct 24, 2026",
          maxPoints: 10,
          weight: "2.5%",
          status: "Graded",
          submittedFile: "bcs155_assignment1_flex.cpp",
          submittedAt: "Oct 23, 2026 · 10:45 PM",
          obtainedScore: 9.5,
          feedback: "Flawless DFA transitions. Handled string literals and escaped tokens correctly."
        },
        {
          id: "as-2",
          title: "Assignment 2: LL(1) Parsing Table & First/Follow Computation",
          dueDate: "Tomorrow at 11:59 PM",
          maxPoints: 10,
          weight: "2.5%",
          status: "Pending"
        },
        {
          id: "as-3",
          title: "Assignment 3: LR(1) Item Sets & Shift-Reduce Table",
          dueDate: "In 2 weeks",
          maxPoints: 10,
          weight: "2.5%",
          status: "Pending"
        }
      ],
      quizzes: [
        {
          id: "qz-1",
          title: "Quiz 1: Regular Expressions & NFA to DFA",
          date: "Oct 18, 2026",
          maxPoints: 10,
          obtainedScore: 9.0,
          classAverage: 6.8,
          topics: "Subset construction, minimized states, epsilon closures"
        },
        {
          id: "qz-2",
          title: "Quiz 2: Context Free Grammars & Ambiguity Removal",
          date: "Nov 02, 2026",
          maxPoints: 10,
          obtainedScore: 8.5,
          classAverage: 7.1,
          topics: "Dangling-else ambiguity, Left recursion elimination, Left factoring"
        }
      ],
      exams: [
        {
          id: "ex-1",
          title: "Mid-Term Examination",
          date: "Nov 12, 2026",
          maxPoints: 25,
          obtainedScore: 21.5,
          classAverage: 17.2,
          status: "Completed"
        },
        {
          id: "ex-2",
          title: "Terminal Comprehensive Examination",
          date: "Dec 20, 2026",
          maxPoints: 50,
          status: "Upcoming"
        }
      ]
    },
    attendanceLedger: [
      { id: "att-1", lectureNo: 1, date: "Oct 12, 2026", day: "Monday", slot: "Slot 2 (10:15 - 11:45)", room: "Room C-204", topic: "Intro to Compilers, Analysis vs Synthesis phases", status: "PRESENT" },
      { id: "att-2", lectureNo: 2, date: "Oct 14, 2026", day: "Wednesday", slot: "Slot 2 (10:15 - 11:45)", room: "Room C-204", topic: "Lexical Tokens, Patterns, Lexemes & Regex", status: "PRESENT" },
      { id: "att-3", lectureNo: 3, date: "Oct 19, 2026", day: "Monday", slot: "Slot 2 (10:15 - 11:45)", room: "Room C-204", topic: "Thompson's Construction (Regex to NFA)", status: "PRESENT" },
      { id: "att-4", lectureNo: 4, date: "Oct 21, 2026", day: "Wednesday", slot: "Slot 2 (10:15 - 11:45)", room: "Room C-204", topic: "Subset Construction Algorithm (NFA to DFA)", status: "ABSENT", notes: "Unexcused absence" },
      { id: "att-5", lectureNo: 5, date: "Oct 26, 2026", day: "Monday", slot: "Slot 2 (10:15 - 11:45)", room: "Room C-204", topic: "DFA State Minimization (Hopcroft Algorithm)", status: "PRESENT" },
      { id: "att-6", lectureNo: 6, date: "Oct 28, 2026", day: "Wednesday", slot: "Slot 2 (10:15 - 11:45)", room: "Room C-204", topic: "Hands-on Flex Scanner Architecture", status: "ABSENT", notes: "Fever / Medical Certificate submitted" },
      { id: "att-7", lectureNo: 7, date: "Nov 02, 2026", day: "Monday", slot: "Slot 2 (10:15 - 11:45)", room: "Room C-204", topic: "Context Free Grammars & Derivation Trees", status: "PRESENT" },
      { id: "att-8", lectureNo: 8, date: "Nov 04, 2026", day: "Wednesday", slot: "Slot 2 (10:15 - 11:45)", room: "Room C-204", topic: "Left Recursion Elimination & Left Factoring", status: "LATE", notes: "Admitted with warning (12 mins late)" },
      { id: "att-9", lectureNo: 9, date: "Nov 09, 2026", day: "Monday", slot: "Slot 2 (10:15 - 11:45)", room: "Room C-204", topic: "First & Follow Sets Formal Computation", status: "PRESENT" },
      { id: "att-10", lectureNo: 10, date: "Nov 11, 2026", day: "Wednesday", slot: "Slot 2 (10:15 - 11:45)", room: "Room C-204", topic: "LL(1) Predictive Parsing Table Construction", status: "ABSENT", notes: "Unexcused absence" }
    ],
    leaveRequests: [
      {
        id: "lv-1",
        lectureNo: 6,
        date: "Oct 28, 2026",
        reason: "Medical / Severe viral influenza",
        documentName: "hospital_clinic_prescription.pdf",
        submittedAt: "Oct 29, 2026 · 09:20 AM",
        status: "Approved",
        adminRemarks: "Doctor verified. Excused under Academic Regulation 4.2."
      }
    ],
    lectureHub: {
      recordings: [
        {
          id: "rec-1",
          lectureNo: 1,
          title: "Introduction to Compiler Phases & Lexical Structure",
          date: "Oct 12, 2026",
          duration: "46:15",
          timestamps: [
            { time: "02:10", label: "Phases of a Modern Compiler" },
            { time: "18:45", label: "Lexical Analyzer Role & Token Attributes" },
            { time: "34:20", label: "Symbol Table Management Interface" }
          ]
        },
        {
          id: "rec-2",
          lectureNo: 3,
          title: "Thompson's Construction (Regular Expressions to NFA)",
          date: "Oct 19, 2026",
          duration: "52:40",
          timestamps: [
            { time: "05:00", label: "Epsilon Transitions & Inductive Rules" },
            { time: "22:15", label: "Concatenation and Kleene Star States" },
            { time: "41:30", label: "Step-by-step Trace: (a|b)*abb" }
          ]
        },
        {
          id: "rec-3",
          lectureNo: 9,
          title: "Computation of First and Follow Sets in Context-Free Grammars",
          date: "Nov 09, 2026",
          duration: "49:10",
          timestamps: [
            { time: "04:30", label: "First Set Definition and Base Cases" },
            { time: "20:15", label: "Epsilon Propagation in First Sets" },
            { time: "35:50", label: "Follow Set 3 Invariant Rules & Dollar Symbol" }
          ]
        }
      ],
      materials: [
        { id: "mat-1", title: "Dragon Book: Compilers Principles & Techniques (Full PDF)", category: "Textbook", format: "PDF", size: "18.4 MB", uploadDate: "Oct 08, 2026", downloadsCount: 142 },
        { id: "mat-2", title: "Chapter 3: Lexical Analysis & Finite Automata Slides", category: "Slides", format: "PPTX", size: "5.2 MB", uploadDate: "Oct 14, 2026", downloadsCount: 98 },
        { id: "mat-3", title: "Chapter 4: Syntax Analysis & LL(1) Tables Slides", category: "Slides", format: "PPTX", size: "6.8 MB", uploadDate: "Nov 02, 2026", downloadsCount: 84 },
        { id: "mat-4", title: "Flex Scanner Template Code & Makefile", category: "Code", format: "ZIP", size: "1.4 MB", uploadDate: "Oct 20, 2026", downloadsCount: 65 },
        { id: "mat-5", title: "LL(1) Grammar Parsing Homework Practice Sheet", category: "Handout", format: "DOCX", size: "750 KB", uploadDate: "Nov 05, 2026", downloadsCount: 71 }
      ]
    }
  },
  {
    id: "os",
    code: "CSC-322",
    title: "Operating Systems",
    creditHours: 4,
    section: "BCS-7A",
    semester: "7th Semester · Fall 2026",
    teacher: {
      name: "Dr. Muhammad Asim",
      role: "Assistant Professor",
      avatar: "MA",
      status: "In Lecture",
      office: "C Block, 2nd Floor, Room C-203",
      email: "masim@cuisahiwal.edu.pk",
      officeHours: "Tue & Thu: 10:00 AM – 12:00 PM",
      bio: "Ph.D. in Distributed Systems with emphasis on high-performance concurrency, kernel process scheduling, and cloud virtualization."
    },
    attendance: {
      percentage: 88.0,
      attended: 22,
      total: 25,
      absent: 2,
      late: 1,
      excused: 0,
      requiredConsecutive: 0
    },
    standing: {
      estimatedGrade: "91.2% · A",
      scorePercentage: 91.2,
      gpa: "4.00",
      nextDeadline: "Banker's Algorithm Simulation due in 4 days"
    },
    overview: {
      description: "Structures, algorithms, and design paradigms of modern operating systems, addressing concurrent processes, threads, synchronization primitives, deadlocks, virtual memory, paging, and disk scheduling.",
      objectives: [
        "Implement POSIX thread synchronization using mutexes, semaphores, and condition variables.",
        "Simulate deadlock detection and avoidance algorithms (Banker's algorithm).",
        "Analyze virtual memory page replacement policies (LRU, FIFO, Clock)."
      ],
      prerequisites: "Data Structures (CSC-211), Assembly Language (CSC-221)",
      textbooks: [
        { title: "Operating System Concepts", author: "Silberschatz, Galvin, and Gagne", edition: "10th Edition" },
        { title: "Modern Operating Systems", author: "Andrew S. Tanenbaum", edition: "4th Edition" }
      ],
      gradingPolicy: [
        { item: "Quizzes", weight: "15%", description: "Theoretical understanding of synchronization and memory." },
        { item: "Lab Tasks & Kernel Modules", weight: "15%", description: "POSIX threads, shared memory, and Linux system calls." },
        { item: "Mid-Term", weight: "20%", description: "Processes, threads, and CPU scheduling." },
        { item: "Terminal Examination", weight: "50%", description: "Comprehensive final exam." }
      ],
      announcements: [
        {
          id: "an-os-1",
          title: "Kernel Synchronization Lab in C-01",
          date: "May 12, 2026",
          content: "Please ensure your Linux VM or dual-boot system has gcc and build-essential installed before the Thursday lab.",
          isPinned: true,
          author: "Dr. Muhammad Asim"
        }
      ]
    },
    coursework: {
      assignments: [
        {
          id: "as-os-1",
          title: "Lab 3: POSIX Multi-threaded Matrix Multiplication",
          dueDate: "Oct 20, 2026",
          maxPoints: 10,
          weight: "2.5%",
          status: "Graded",
          submittedFile: "matrix_pthread_sim.c",
          submittedAt: "Oct 19, 2026 · 11:15 PM",
          obtainedScore: 9.8,
          feedback: "Great job utilizing pthread_join and dynamic chunking."
        },
        {
          id: "as-os-2",
          title: "Assignment 2: Banker's Algorithm Deadlock Avoidance",
          dueDate: "In 4 days",
          maxPoints: 10,
          weight: "2.5%",
          status: "Pending"
        }
      ],
      quizzes: [
        {
          id: "qz-os-1",
          title: "Quiz 1: Round Robin & Multi-Level Feedback Queues",
          date: "Oct 22, 2026",
          maxPoints: 10,
          obtainedScore: 9.0,
          classAverage: 7.4,
          topics: "Turnaround time, Waiting time, Preemption"
        }
      ],
      exams: [
        {
          id: "ex-os-1",
          title: "Mid-Term Examination",
          date: "Nov 14, 2026",
          maxPoints: 25,
          obtainedScore: 23.0,
          classAverage: 18.1,
          status: "Completed"
        }
      ]
    },
    attendanceLedger: [
      { id: "att-os-1", lectureNo: 1, date: "Oct 13, 2026", day: "Tuesday", slot: "Slot 1 (08:30 - 10:00)", room: "Room C-101", topic: "Dual-Mode Operation & System Calls", status: "PRESENT" },
      { id: "att-os-2", lectureNo: 2, date: "Oct 15, 2026", day: "Thursday", slot: "Slot 1 (08:30 - 10:00)", room: "Room C-101", topic: "Process Control Block & Context Switching", status: "PRESENT" },
      { id: "att-os-3", lectureNo: 3, date: "Oct 20, 2026", day: "Tuesday", slot: "Slot 1 (08:30 - 10:00)", room: "Room C-101", topic: "Inter-Process Communication (Pipes, Shared Memory)", status: "PRESENT" },
      { id: "att-os-4", lectureNo: 4, date: "Oct 22, 2026", day: "Thursday", slot: "Slot 1 (08:30 - 10:00)", room: "Room C-101", topic: "CPU Scheduling Algorithms (FCFS, SJF, RR)", status: "ABSENT", notes: "Unexcused" },
      { id: "att-os-5", lectureNo: 5, date: "Oct 27, 2026", day: "Tuesday", slot: "Slot 1 (08:30 - 10:00)", room: "Room C-101", topic: "Critical Section Problem & Peterson's Solution", status: "PRESENT" }
    ],
    leaveRequests: [],
    lectureHub: {
      recordings: [
        {
          id: "rec-os-1",
          lectureNo: 1,
          title: "System Call Dispatching and Context Switching",
          date: "Oct 13, 2026",
          duration: "50:12",
          timestamps: [
            { time: "05:10", label: "Trap Instructions & Interrupt Vectors" },
            { time: "24:00", label: "PCB State Transitions" }
          ]
        }
      ],
      materials: [
        { id: "mat-os-1", title: "Silberschatz Operating System Concepts (10th Ed).pdf", category: "Textbook", format: "PDF", size: "22.3 MB", uploadDate: "Oct 10, 2026", downloadsCount: 165 },
        { id: "mat-os-2", title: "Process Synchronization & Mutex Slides", category: "Slides", format: "PPTX", size: "4.8 MB", uploadDate: "Oct 25, 2026", downloadsCount: 92 }
      ]
    }
  },
  {
    id: "db",
    code: "CSC-331",
    title: "Database Systems",
    creditHours: 4,
    section: "BCS-7B",
    semester: "7th Semester · Fall 2026",
    teacher: {
      name: "Engr. Tariq Mehmood",
      role: "Assistant Professor",
      avatar: "TM",
      status: "Available in Office",
      office: "A Block, 1st Floor, Room A-103",
      email: "tariqmehmood@cuisahiwal.edu.pk",
      officeHours: "Wed & Fri: 02:00 PM – 04:00 PM",
      bio: "Senior engineer and educator specializing in enterprise database architectures, relational algebra, SQL optimization, and distributed query engines."
    },
    attendance: {
      percentage: 94.2,
      attended: 26,
      total: 28,
      absent: 1,
      late: 1,
      excused: 0,
      requiredConsecutive: 0
    },
    standing: {
      estimatedGrade: "95.0% · A+",
      scorePercentage: 95.0,
      gpa: "4.00",
      nextDeadline: "B+ Tree Indexing Case Study due next Monday"
    },
    overview: {
      description: "Foundational and applied principles of database design, entity-relationship modeling, relational algebra, advanced SQL, normal forms (1NF through BCNF), indexing, concurrency control, and transactions.",
      objectives: [
        "Construct enterprise normalized relational schemas adhering to BCNF standards.",
        "Write complex SQL queries involving window functions, common table expressions, and recursive views.",
        "Implement ACID transaction isolation strategies using WAL (Write-Ahead Logging)."
      ],
      prerequisites: "Data Structures (CSC-211), Discrete Mathematics (CSC-102)",
      textbooks: [
        { title: "Database System Concepts", author: "Silberschatz, Korth, Sudarshan", edition: "7th Edition" },
        { title: "Fundamentals of Database Systems", author: "Elmasri, Navathe", edition: "7th Edition" }
      ],
      gradingPolicy: [
        { item: "Quizzes", weight: "15%", description: "Relational algebra and Normalization." },
        { item: "Lab Exams & SQL Queries", weight: "15%", description: "PostgreSQL queries, triggers, and stored procedures." },
        { item: "Midterm", weight: "20%", description: "ER Modeling and SQL." },
        { item: "Terminal Examination", weight: "50%", description: "Comprehensive final examination." }
      ],
      announcements: [
        {
          id: "an-db-1",
          title: "PostgreSQL Advanced Indexing Workshop",
          date: "May 09, 2026",
          content: "Workshop on EXPLAIN ANALYZE and query optimizer planning will be conducted in Computer Lab 1.",
          isPinned: true,
          author: "Engr. Tariq Mehmood"
        }
      ]
    },
    coursework: {
      assignments: [
        {
          id: "as-db-1",
          title: "Assignment 1: Enterprise ER to Relational Mapping",
          dueDate: "Oct 16, 2026",
          maxPoints: 10,
          weight: "2.5%",
          status: "Graded",
          submittedFile: "relational_schema_hospital.sql",
          submittedAt: "Oct 15, 2026 · 08:30 PM",
          obtainedScore: 10.0,
          feedback: "Exemplary 3NF normalization without any redundancy."
        }
      ],
      quizzes: [
        {
          id: "qz-db-1",
          title: "Quiz 1: Functional Dependencies & BCNF",
          date: "Oct 30, 2026",
          maxPoints: 10,
          obtainedScore: 10.0,
          classAverage: 8.2,
          topics: "Armstrong's axioms, Canonical cover, Lossless join"
        }
      ],
      exams: [
        {
          id: "ex-db-1",
          title: "Mid-Term Examination",
          date: "Nov 15, 2026",
          maxPoints: 25,
          obtainedScore: 24.0,
          classAverage: 19.4,
          status: "Completed"
        }
      ]
    },
    attendanceLedger: [
      { id: "att-db-1", lectureNo: 1, date: "Oct 14, 2026", day: "Wednesday", slot: "Slot 3 (12:00 - 01:30)", room: "Room A-201", topic: "Database Architecture & ANSI/SPARC 3-Tier Model", status: "PRESENT" },
      { id: "att-db-2", lectureNo: 2, date: "Oct 16, 2026", day: "Friday", slot: "Slot 3 (12:00 - 01:30)", room: "Room A-201", topic: "Relational Data Model & Integrity Constraints", status: "PRESENT" },
      { id: "att-db-3", lectureNo: 3, date: "Oct 21, 2026", day: "Wednesday", slot: "Slot 3 (12:00 - 01:30)", room: "Room A-201", topic: "Relational Algebra Operations", status: "PRESENT" }
    ],
    leaveRequests: [],
    lectureHub: {
      recordings: [
        {
          id: "rec-db-1",
          lectureNo: 1,
          title: "Relational Algebra & Schema Decomposition",
          date: "Oct 21, 2026",
          duration: "45:30",
          timestamps: [
            { time: "06:00", label: "Select, Project, and Cartesian Product" },
            { time: "25:10", label: "Theta Join vs Natural Join" }
          ]
        }
      ],
      materials: [
        { id: "mat-db-1", title: "PostgreSQL Advanced Indexing Guide.pdf", category: "Handout", format: "PDF", size: "3.5 MB", uploadDate: "Oct 15, 2026", downloadsCount: 112 }
      ]
    }
  },
  {
    id: "se",
    code: "CSC-371",
    title: "Software Engineering",
    creditHours: 3,
    section: "BCS-7C",
    semester: "7th Semester · Fall 2026",
    teacher: {
      name: "Dr. Majid Hussain",
      role: "Head of Department (HOD) / Professor",
      avatar: "MH",
      status: "Consultation Hours",
      office: "A Block, 3rd Floor, Room A-302",
      email: "hod-cs@cuisahiwal.edu.pk",
      officeHours: "Tue & Thu: 02:00 PM – 03:30 PM",
      bio: "Professor and Head of Computer Science Department with 20+ years expertise in software architectural quality, agile requirements engineering, and safety-critical software."
    },
    attendance: {
      percentage: 78.0,
      attended: 16,
      total: 21,
      absent: 4,
      late: 1,
      excused: 0,
      requiredConsecutive: 1
    },
    standing: {
      estimatedGrade: "81.0% · B+",
      scorePercentage: 81.0,
      gpa: "3.33",
      nextDeadline: "Term Project Sprint 2 Review in 5 days"
    },
    overview: {
      description: "Engineering approaches to software lifecycle methodologies, Agile/Scrum, requirements elicitation (SRS), architectural modeling using UML, unit testing, and continuous integration pipelines.",
      objectives: [
        "Author formal Software Requirements Specifications (IEEE Std 830).",
        "Design modular software architectures using Gang of Four (GoF) design patterns.",
        "Execute automated test suites using CI/CD pipelines."
      ],
      prerequisites: "Object Oriented Programming (CSC-241)",
      textbooks: [
        { title: "Software Engineering: A Practitioner's Approach", author: "Roger S. Pressman", edition: "9th Edition" },
        { title: "Software Engineering", author: "Ian Sommerville", edition: "10th Edition" }
      ],
      gradingPolicy: [
        { item: "Quizzes", weight: "15%", description: "Agile, UML, and Testing theory." },
        { item: "Semester Capstone Project", weight: "20%", description: "Sprint deliverables, architecture, and code reviews." },
        { item: "Midterm", weight: "15%", description: "Requirements and Design patterns." },
        { item: "Terminal Examination", weight: "50%", description: "Comprehensive examination." }
      ],
      announcements: [
        {
          id: "an-se-1",
          title: "Sprint 2 Evaluation Schedule",
          date: "May 11, 2026",
          content: "All project groups must submit their GitHub repository links with unit tests pass rates before Monday.",
          isPinned: true,
          author: "Dr. Majid Hussain"
        }
      ]
    },
    coursework: {
      assignments: [
        {
          id: "as-se-1",
          title: "Assignment 1: IEEE 830 Standard SRS Document",
          dueDate: "Oct 18, 2026",
          maxPoints: 10,
          weight: "2.5%",
          status: "Graded",
          submittedFile: "smart_health_srs_final.pdf",
          submittedAt: "Oct 17, 2026 · 06:15 PM",
          obtainedScore: 8.5,
          feedback: "Well detailed use cases. Ensure non-functional latency requirements are quantified."
        }
      ],
      quizzes: [
        {
          id: "qz-se-1",
          title: "Quiz 1: Scrum Ceremonies, Artifacts & User Stories",
          date: "Nov 03, 2026",
          maxPoints: 10,
          obtainedScore: 8.0,
          classAverage: 7.2,
          topics: "Sprint Planning, Daily Standup, Definition of Done"
        }
      ],
      exams: [
        {
          id: "ex-se-1",
          title: "Mid-Term Examination",
          date: "Nov 17, 2026",
          maxPoints: 20,
          obtainedScore: 16.5,
          classAverage: 14.0,
          status: "Completed"
        }
      ]
    },
    attendanceLedger: [
      { id: "att-se-1", lectureNo: 1, date: "Oct 15, 2026", day: "Thursday", slot: "Slot 4 (02:00 - 03:30)", room: "Room C-102", topic: "Waterfall vs Agile Lifecycle Models", status: "PRESENT" },
      { id: "att-se-2", lectureNo: 2, date: "Oct 20, 2026", day: "Tuesday", slot: "Slot 4 (02:00 - 03:30)", room: "Room C-102", topic: "Requirements Elicitation & Prototyping", status: "PRESENT" },
      { id: "att-se-3", lectureNo: 3, date: "Oct 22, 2026", day: "Thursday", slot: "Slot 4 (02:00 - 03:30)", room: "Room C-102", topic: "Use Case Modeling & Activity Diagrams", status: "ABSENT", notes: "Unexcused" }
    ],
    leaveRequests: [],
    lectureHub: {
      recordings: [
        {
          id: "rec-se-1",
          lectureNo: 1,
          title: "Agile Estimation, Velocity, and Burndown Charts",
          date: "Oct 15, 2026",
          duration: "44:00",
          timestamps: [
            { time: "04:15", label: "Planning Poker & Story Points" },
            { time: "22:30", label: "Burndown vs Burnup Metrics" }
          ]
        }
      ],
      materials: [
        { id: "mat-se-1", title: "IEEE Recommended Practice for Software Requirements Specifications.pdf", category: "Handout", format: "PDF", size: "2.1 MB", uploadDate: "Oct 12, 2026", downloadsCount: 110 }
      ]
    }
  }
];

export function getCourseById(id: string): EnrolledCourse | undefined {
  return COURSES_CATALOG.find((c) => c.id.toLowerCase() === id.toLowerCase() || c.code.toLowerCase() === id.toLowerCase());
}
