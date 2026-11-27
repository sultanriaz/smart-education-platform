export interface EnrolledCourse {
  id: string;
  code: string;
  title: string;
  creditHours: number;
  section: string;
  semester: string;
  shortTag?: string;
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
    syllabus: string[];
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
      uploadedDate: string;
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
      uploadedDate: string;
      dueDate: string;
      date: string;
      maxPoints: number;
      obtainedScore: number;
      classAverage: number;
      topics: string;
      status: "Pending" | "Submitted" | "Graded";
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
    gdb: {
      id: string;
      title: string;
      topic: string;
      dueDate: string;
      status: "Open" | "Closed";
    }[];
    mdb: {
      id: string;
      title: string;
      prompt: string;
      postsCount: number;
      lastUpdated: string;
    }[];
  };
  attendanceLedger: {
    id: string;
    lectureNo: number;
    sessionType: "Class" | "Lab";
    date: string;
    startTime: string;
    endTime: string;
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
      timestamps: { time: string; label: string }[];
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
    code: "CSC 441",
    title: "Compiler Construction",
    creditHours: 3,
    section: "BCS 7 C",
    semester: "Spring 2025",
    teacher: {
      name: "Prof. Mr. Bilal",
      role: "Senior Lecturer / Compiler Architect",
      avatar: "MB",
      status: "Available in Office",
      office: "C Block, 1st Floor, Room C-109",
      email: "bilal.shabir@cuisahiwal.edu.pk",
      officeHours: "Mon & Wed: 10:00 AM – 12:00 PM",
      bio: "Faculty member in Computer Science specializing in lexical analysis, LL/LR parsing, and runtime compiler optimization."
    },
    attendance: {
      percentage: 67,
      attended: 12,
      total: 18,
      absent: 6,
      late: 0,
      excused: 0,
      requiredConsecutive: 3
    },
    standing: {
      estimatedGrade: "84.5% · A-",
      scorePercentage: 84.5,
      gpa: "3.67",
      nextDeadline: "15 Jan 2025, 11:59 PM"
    },
    overview: {
      description: "Principles of modern compiler design covering lexical analysis, grammars, syntax analysis, semantic checking, intermediate code generation, and target machine optimization.",
      syllabus: [
        "Introduction to Compilers & Phases",
        "Lexical Analysis & Regular Expressions",
        "Syntax Analysis – Top-Down Parsing",
        "Syntax Analysis – Bottom-Up Parsing",
        "Semantic Analysis & Symbol Table",
        "Intermediate Code Generation",
        "Code Optimization Techniques",
        "Code Generation & Target Machine"
      ],
      objectives: [
        "Build lexical analyzers and regular expression recognizers.",
        "Construct LL(1) and LR(1) parsers.",
        "Implement three-address intermediate code generation."
      ],
      prerequisites: "Theory of Automata (CSC-312)",
      textbooks: [
        { title: "Compilers: Principles, Techniques, and Tools", author: "Aho, Lam, Sethi, Ullman", edition: "2nd Edition" },
        { title: "Engineering a Compiler", author: "Cooper & Torczon", edition: "2nd Edition" }
      ],
      gradingPolicy: [
        { item: "Quizzes", weight: "15%", description: "Short conceptual quizzes." },
        { item: "Assignments", weight: "10%", description: "Lab and parser deliverables." },
        { item: "Mid Term", weight: "25%", description: "Mid-semester written exam." },
        { item: "Final Term", weight: "50%", description: "Comprehensive final exam." }
      ],
      announcements: []
    },
    coursework: {
      assignments: [
        {
          id: "as-1",
          title: "Assignment 1 — Lexical Analyzer",
          uploadedDate: "08 Jan 2025, 8:00 AM",
          dueDate: "15 Jan 2025, 11:59 PM",
          maxPoints: 10,
          weight: "5%",
          status: "Pending",
          obtainedScore: 7.5
        },
        {
          id: "as-2",
          title: "Assignment 2 — Syntax Parser Tree",
          uploadedDate: "20 Jan 2025, 9:00 AM",
          dueDate: "28 Jan 2025, 11:59 PM",
          maxPoints: 10,
          weight: "5%",
          status: "Graded",
          submittedFile: "parser_tree.pdf",
          submittedAt: "27 Jan 2025",
          obtainedScore: 9.5
        }
      ],
      quizzes: [
        {
          id: "qz-1",
          title: "Quiz 1 — Tokens & Regular Expressions",
          uploadedDate: "05 Jan 2025, 10:00 AM",
          dueDate: "10 Jan 2025, 12:00 PM",
          date: "April 13, 2025",
          maxPoints: 10,
          obtainedScore: 7.5,
          classAverage: 7.2,
          topics: "Lexical Tokens & DFA",
          status: "Graded"
        },
        {
          id: "qz-2",
          title: "Quiz 2 — Context-Free Grammars",
          uploadedDate: "12 Apr 2025, 10:00 AM",
          dueDate: "13 Apr 2025, 11:30 AM",
          date: "April 13, 2025",
          maxPoints: 10,
          obtainedScore: 9.5,
          classAverage: 7.9,
          topics: "First & Follow Sets",
          status: "Graded"
        }
      ],
      exams: [
        {
          id: "ex-1",
          title: "Mid Term",
          date: "April 13, 2025",
          maxPoints: 25,
          obtainedScore: 18,
          status: "Completed"
        },
        {
          id: "ex-2",
          title: "Final Term",
          date: "June 15, 2025",
          maxPoints: 50,
          obtainedScore: 42,
          status: "Completed"
        }
      ],
      gdb: [
        {
          id: "gdb-1",
          title: "GDB 1 — Compiler vs Interpreter Trade-offs",
          topic: "Compare JIT compilation and ahead-of-time native binaries for mobile workloads.",
          dueDate: "22 May 2025",
          status: "Open"
        }
      ],
      mdb: [
        {
          id: "mdb-1",
          title: "MDB — LL(1) Left Recursion Help Thread",
          prompt: "Share sample grammars and discuss ambiguity removal techniques with your class.",
          postsCount: 14,
          lastUpdated: "2 hours ago"
        }
      ]
    },
    attendanceLedger: [
      { id: "c-att-1", lectureNo: 1, sessionType: "Class", date: "4/3/2026", startTime: "10:00:00 AM", endTime: "11:00:00 AM", day: "Monday", slot: "Slot 1", room: "C-204", topic: "Compiler Phases", status: "PRESENT" },
      { id: "c-att-2", lectureNo: 2, sessionType: "Class", date: "4/4/2026", startTime: "10:00:00 AM", endTime: "11:00:00 AM", day: "Tuesday", slot: "Slot 1", room: "C-204", topic: "Lexical Scanning", status: "PRESENT" },
      { id: "c-att-3", lectureNo: 3, sessionType: "Class", date: "4/5/2026", startTime: "10:00:00 AM", endTime: "11:00:00 AM", day: "Wednesday", slot: "Slot 1", room: "C-204", topic: "Finite Automata", status: "ABSENT" },
      { id: "c-att-4", lectureNo: 4, sessionType: "Class", date: "4/6/2026", startTime: "10:00:00 AM", endTime: "11:00:00 AM", day: "Thursday", slot: "Slot 1", room: "C-204", topic: "Top-Down Parsing", status: "PRESENT" },
      { id: "c-att-5", lectureNo: 5, sessionType: "Class", date: "4/7/2026", startTime: "10:00:00 AM", endTime: "11:00:00 AM", day: "Friday", slot: "Slot 1", room: "C-204", topic: "FIRST & FOLLOW", status: "PRESENT" },
      { id: "c-att-6", lectureNo: 6, sessionType: "Class", date: "4/10/2026", startTime: "10:00:00 AM", endTime: "11:00:00 AM", day: "Monday", slot: "Slot 2", room: "C-204", topic: "LL(1) Table", status: "ABSENT" },
      { id: "c-att-7", lectureNo: 7, sessionType: "Class", date: "4/11/2026", startTime: "10:00:00 AM", endTime: "11:00:00 AM", day: "Tuesday", slot: "Slot 2", room: "C-204", topic: "Shift-Reduce Parsing", status: "PRESENT" },
      { id: "c-att-8", lectureNo: 8, sessionType: "Class", date: "4/12/2026", startTime: "10:00:00 AM", endTime: "11:00:00 AM", day: "Wednesday", slot: "Slot 2", room: "C-204", topic: "LR(0) Items", status: "PRESENT" },
      { id: "c-att-9", lectureNo: 9, sessionType: "Class", date: "4/13/2026", startTime: "10:00:00 AM", endTime: "11:00:00 AM", day: "Thursday", slot: "Slot 2", room: "C-204", topic: "SLR Grammar", status: "PRESENT" },
      { id: "c-att-10", lectureNo: 10, sessionType: "Lab", date: "4/14/2026", startTime: "10:00:00 AM", endTime: "12:00:00 PM", day: "Friday", slot: "Lab 1", room: "Lab 2", topic: "Flex Lab 1", status: "PRESENT" },
      { id: "c-att-11", lectureNo: 11, sessionType: "Lab", date: "4/17/2026", startTime: "10:00:00 AM", endTime: "12:00:00 PM", day: "Monday", slot: "Lab 2", room: "Lab 2", topic: "Flex Tokens Lab", status: "ABSENT" },
      { id: "c-att-12", lectureNo: 12, sessionType: "Lab", date: "4/18/2026", startTime: "10:00:00 AM", endTime: "12:00:00 PM", day: "Tuesday", slot: "Lab 3", room: "Lab 2", topic: "Bison Parser Lab", status: "PRESENT" },
      { id: "c-att-13", lectureNo: 13, sessionType: "Lab", date: "4/19/2026", startTime: "10:00:00 AM", endTime: "12:00:00 PM", day: "Wednesday", slot: "Lab 4", room: "Lab 2", topic: "AST Builder Lab", status: "ABSENT" },
      { id: "c-att-14", lectureNo: 14, sessionType: "Lab", date: "4/20/2026", startTime: "10:00:00 AM", endTime: "12:00:00 PM", day: "Thursday", slot: "Lab 5", room: "Lab 2", topic: "Symbol Table Lab", status: "PRESENT" },
      { id: "c-att-15", lectureNo: 15, sessionType: "Lab", date: "4/21/2026", startTime: "10:00:00 AM", endTime: "12:00:00 PM", day: "Friday", slot: "Lab 6", room: "Lab 2", topic: "Type Check Lab", status: "PRESENT" },
      { id: "c-att-16", lectureNo: 16, sessionType: "Lab", date: "4/24/2026", startTime: "10:00:00 AM", endTime: "12:00:00 PM", day: "Monday", slot: "Lab 7", room: "Lab 2", topic: "TAC Code Lab", status: "ABSENT" },
      { id: "c-att-17", lectureNo: 17, sessionType: "Lab", date: "4/25/2026", startTime: "10:00:00 AM", endTime: "12:00:00 PM", day: "Tuesday", slot: "Lab 8", room: "Lab 2", topic: "Optimization Lab", status: "PRESENT" },
      { id: "c-att-18", lectureNo: 18, sessionType: "Lab", date: "4/26/2026", startTime: "10:00:00 AM", endTime: "12:00:00 PM", day: "Wednesday", slot: "Lab 9", room: "Lab 2", topic: "Final Project Lab", status: "ABSENT" }
    ],
    leaveRequests: [],
    lectureHub: {
      recordings: [
        {
          id: "rec-1",
          lectureNo: 1,
          title: "Introduction to Compilers & Compilation Phases",
          date: "05 Jan 2025",
          duration: "52 min",
          timestamps: [{ time: "00:00", label: "Overview" }]
        },
        {
          id: "rec-2",
          lectureNo: 2,
          title: "Lexical Analysis & Tokenization",
          date: "08 Jan 2025",
          duration: "48 min",
          timestamps: [{ time: "00:00", label: "Tokens & Patterns" }]
        },
        {
          id: "rec-3",
          lectureNo: 3,
          title: "Context-Free Grammars & Parsing Techniques",
          date: "12 Jan 2025",
          duration: "56 min",
          timestamps: [{ time: "00:00", label: "Derivations" }]
        }
      ],
      materials: [
        { id: "mat-1", title: "Dragon Book — Compilers: Principles, Techniques, and Tools", category: "Textbook", format: "PDF", size: "12.4 MB", uploadDate: "05 Jan 2025", downloadsCount: 142 },
        { id: "mat-2", title: "Lexical Analysis & Finite Automata Handbook", category: "Handout", format: "PDF", size: "3.1 MB", uploadDate: "08 Jan 2025", downloadsCount: 98 },
        { id: "mat-3", title: "Engineering a Compiler — Reference Chapters", category: "Textbook", format: "PDF", size: "8.2 MB", uploadDate: "12 Jan 2025", downloadsCount: 74 }
      ]
    }
  },
  {
    id: "infosec",
    code: "CSC 442",
    title: "Information Security",
    creditHours: 3,
    section: "BCS 7 C",
    semester: "Spring 2025",
    teacher: {
      name: "Dr. Ayesha Malik",
      role: "Associate Professor",
      avatar: "AM",
      status: "Available in Office",
      office: "C Block, 2nd Floor, Room C-208",
      email: "ayesha.malik@cuisahiwal.edu.pk",
      officeHours: "Tue & Thu: 10:15 AM – 12:00 PM",
      bio: "Research specialist in applied cryptography, network defense, and web security auditing."
    },
    attendance: {
      percentage: 86,
      attended: 13,
      total: 15,
      absent: 2,
      late: 0,
      excused: 0,
      requiredConsecutive: 0
    },
    standing: {
      estimatedGrade: "88.0% · A",
      scorePercentage: 88,
      gpa: "3.85",
      nextDeadline: "18 Jan 2025, 11:59 PM"
    },
    overview: {
      description: "Foundations of symmetric and public-key cryptography, authentication protocols, access control models, and secure software practices.",
      syllabus: [
        "Security Concepts & Threat Models",
        "Classical & Stream Ciphers",
        "Block Ciphers (DES & AES)",
        "Number Theory & RSA Cryptography",
        "Hash Functions & Digital Signatures",
        "Public Key Infrastructure (PKI)",
        "Network & Transport Layer Security (TLS)",
        "Web Application Security & OWASP"
      ],
      objectives: ["Understand AES and RSA mechanisms", "Evaluate cryptographic protocols"],
      prerequisites: "Computer Networks",
      textbooks: [{ title: "Cryptography and Network Security", author: "William Stallings", edition: "8th Edition" }],
      gradingPolicy: [
        { item: "Quizzes", weight: "15%", description: "Weekly quizzes." },
        { item: "Assignments", weight: "15%", description: "Security labs." },
        { item: "Mid Term", weight: "25%", description: "Midterm exam." },
        { item: "Final Term", weight: "45%", description: "Terminal exam." }
      ],
      announcements: [
        {
          id: "an-sec-1",
          title: "AES Lab Walkthrough Posted",
          date: "09 Jan 2025",
          content: "Please download the starter guide before Thursday's lab session.",
          author: "Dr. Ayesha Malik"
        }
      ]
    },
    coursework: {
      assignments: [
        { id: "as-sec-1", title: "Assignment 1 — AES Implementation", uploadedDate: "09 Jan 2025, 9:00 AM", dueDate: "18 Jan 2025, 11:59 PM", maxPoints: 10, weight: "5%", status: "Pending", obtainedScore: 8.5 }
      ],
      quizzes: [
        { id: "qz-sec-1", title: "Quiz 1 — Classical Ciphers", uploadedDate: "06 Jan 2025, 10:00 AM", dueDate: "11 Jan 2025, 12:00 PM", date: "April 13, 2025", maxPoints: 10, obtainedScore: 9, classAverage: 8.1, topics: "Caesar & Vigenere", status: "Graded" }
      ],
      exams: [
        { id: "ex-sec-1", title: "Mid Term", date: "April 13, 2025", maxPoints: 25, obtainedScore: 22, status: "Completed" },
        { id: "ex-sec-2", title: "Final Term", date: "June 16, 2025", maxPoints: 50, obtainedScore: 44, status: "Completed" }
      ],
      gdb: [{ id: "gdb-sec-1", title: "GDB 1 — Post-Quantum Readiness", topic: "Why migrate RSA keys toward lattice-based key exchange?", dueDate: "25 May 2025", status: "Open" }],
      mdb: [{ id: "mdb-sec-1", title: "MDB — TLS Handshake Clarifications", prompt: "Post questions regarding certificate chains and root anchors.", postsCount: 9, lastUpdated: "Yesterday" }]
    },
    attendanceLedger: [
      { id: "is-1", lectureNo: 1, sessionType: "Class", date: "4/3/2026", startTime: "08:30:00 AM", endTime: "09:30:00 AM", day: "Monday", slot: "Slot 1", room: "C-101", topic: "Threat Modeling", status: "PRESENT" },
      { id: "is-2", lectureNo: 2, sessionType: "Lab", date: "4/5/2026", startTime: "10:00:00 AM", endTime: "12:00:00 PM", day: "Wednesday", slot: "Slot 2", room: "Lab 1", topic: "OpenSSL Lab", status: "PRESENT" },
      { id: "is-3", lectureNo: 3, sessionType: "Class", date: "4/7/2026", startTime: "08:30:00 AM", endTime: "09:30:00 AM", day: "Friday", slot: "Slot 1", room: "C-101", topic: "AES Rounds", status: "ABSENT" },
      { id: "is-4", lectureNo: 4, sessionType: "Lab", date: "4/12/2026", startTime: "10:00:00 AM", endTime: "12:00:00 PM", day: "Wednesday", slot: "Slot 2", room: "Lab 1", topic: "PKI Certificates Lab", status: "ABSENT" }
    ],
    leaveRequests: [],
    lectureHub: {
      recordings: [
        { id: "rec-is-1", lectureNo: 1, title: "Symmetric Encryption & Stream Ciphers", date: "06 Jan 2025", duration: "50 min", timestamps: [{ time: "00:00", label: "Intro" }] },
        { id: "rec-is-2", lectureNo: 2, title: "RSA & Public Key Exchange", date: "10 Jan 2025", duration: "54 min", timestamps: [{ time: "00:00", label: "RSA Math" }] }
      ],
      materials: [
        { id: "mat-is-1", title: "Stallings — Cryptography and Network Security.pdf", category: "Textbook", format: "PDF", size: "9.8 MB", uploadDate: "06 Jan 2025", downloadsCount: 84 }
      ]
    }
  },
  {
    id: "ml",
    code: "CSC 443",
    title: "Machine Learning",
    creditHours: 4,
    section: "BCS 7 C",
    semester: "Spring 2025",
    teacher: {
      name: "Engr. Bilal Khan",
      role: "Lecturer / AI Lab Lead",
      avatar: "BK",
      status: "In Lecture",
      office: "C Block, Ground Floor, Room C-02",
      email: "bilal.khan@cuisahiwal.edu.pk",
      officeHours: "Wed & Fri: 02:00 PM – 03:30 PM",
      bio: "Focused on statistical learning, gradient optimization, and computer vision models."
    },
    attendance: {
      percentage: 72,
      attended: 13,
      total: 18,
      absent: 5,
      late: 0,
      excused: 0,
      requiredConsecutive: 2
    },
    standing: { estimatedGrade: "82.0% · B+", scorePercentage: 82, gpa: "3.45", nextDeadline: "22 Jan 2025, 11:59 PM" },
    overview: {
      description: "Supervised and unsupervised statistical learning algorithms, neural networks, evaluation metrics, and practical model tuning.",
      syllabus: [
        "Introduction to Supervised Learning",
        "Linear & Polynomial Regression",
        "Logistic Regression & Regularization",
        "Decision Trees & Random Forests",
        "Support Vector Machines & Kernels",
        "Clustering & Dimensionality Reduction",
        "Feedforward Neural Networks",
        "Model Evaluation & Cross-Validation"
      ],
      objectives: ["Train and validate classification models", "Implement gradient descent workflows"],
      prerequisites: "Linear Algebra & Probability",
      textbooks: [{ title: "Pattern Recognition and Machine Learning", author: "Christopher Bishop", edition: "1st Edition" }],
      gradingPolicy: [
        { item: "Quizzes", weight: "15%", description: "Concept checks." },
        { item: "Assignments", weight: "15%", description: "Python notebooks." },
        { item: "Mid Term", weight: "25%", description: "Written exam." },
        { item: "Final Term", weight: "45%", description: "Comprehensive exam." }
      ],
      announcements: []
    },
    coursework: {
      assignments: [
        { id: "as-ml-1", title: "Assignment 1 — Linear Regression Pipeline", uploadedDate: "10 Jan 2025, 8:00 AM", dueDate: "22 Jan 2025, 11:59 PM", maxPoints: 10, weight: "5%", status: "Pending", obtainedScore: 8 }
      ],
      quizzes: [
        { id: "qz-ml-1", title: "Quiz 1 — Bias-Variance Tradeoff", uploadedDate: "07 Jan 2025, 11:00 AM", dueDate: "12 Jan 2025, 11:00 AM", date: "April 13, 2025", maxPoints: 10, obtainedScore: 8.5, classAverage: 7.4, topics: "Regularization", status: "Graded" }
      ],
      exams: [
        { id: "ex-ml-1", title: "Mid Term", date: "April 13, 2025", maxPoints: 25, obtainedScore: 20, status: "Completed" },
        { id: "ex-ml-2", title: "Final Term", date: "June 18, 2025", maxPoints: 50, obtainedScore: 41, status: "Completed" }
      ],
      gdb: [{ id: "gdb-ml-1", title: "GDB 1 — Feature Scaling Impact", topic: "When does gradient descent converge significantly faster after standardization?", dueDate: "24 May 2025", status: "Open" }],
      mdb: [{ id: "mdb-ml-1", title: "MDB — Scikit-Learn Pipeline Questions", prompt: "Share dataset preprocessing questions here.", postsCount: 11, lastUpdated: "Today" }]
    },
    attendanceLedger: [
      { id: "ml-1", lectureNo: 1, sessionType: "Class", date: "4/4/2026", startTime: "10:00:00 AM", endTime: "11:30:00 AM", day: "Tuesday", slot: "Slot 2", room: "Lab 1", topic: "Regression Models", status: "PRESENT" },
      { id: "ml-2", lectureNo: 2, sessionType: "Lab", date: "4/6/2026", startTime: "02:00:00 PM", endTime: "03:30:00 PM", day: "Thursday", slot: "Slot 4", room: "Lab 1", topic: "NumPy Matrices Lab", status: "ABSENT" },
      { id: "ml-3", lectureNo: 3, sessionType: "Class", date: "4/11/2026", startTime: "10:00:00 AM", endTime: "11:30:00 AM", day: "Tuesday", slot: "Slot 2", room: "Lab 1", topic: "Logistic Regression", status: "ABSENT" },
      { id: "ml-4", lectureNo: 4, sessionType: "Lab", date: "4/13/2026", startTime: "02:00:00 PM", endTime: "03:30:00 PM", day: "Thursday", slot: "Slot 4", room: "Lab 1", topic: "Decision Trees Lab", status: "PRESENT" }
    ],
    leaveRequests: [],
    lectureHub: {
      recordings: [
        { id: "rec-ml-1", lectureNo: 1, title: "Gradient Descent & Cost Functions", date: "07 Jan 2025", duration: "55 min", timestamps: [{ time: "00:00", label: "Regression" }] }
      ],
      materials: [
        { id: "mat-ml-1", title: "Hands-On Machine Learning Study Guide", category: "Textbook", format: "PDF", size: "11.0 MB", uploadDate: "07 Jan 2025", downloadsCount: 115 }
      ]
    }
  },
  {
    id: "hrm",
    code: "MGT 321",
    title: "HRM",
    creditHours: 3,
    section: "BCS 7 C",
    semester: "Spring 2025",
    teacher: {
      name: "Dr. Sadia Mahmood",
      role: "Head of Department — Management",
      avatar: "SM",
      status: "Available in Office",
      office: "D Block, 1st Floor, Room D-102",
      email: "sadia.mahmood@cuisahiwal.edu.pk",
      officeHours: "Mon & Wed: 12:00 PM – 02:00 PM",
      bio: "Teaches organizational leadership, HR strategy, and workplace policy."
    },
    attendance: { percentage: 91, attended: 20, total: 22, absent: 2, late: 0, excused: 0, requiredConsecutive: 0 },
    standing: { estimatedGrade: "90.0% · A", scorePercentage: 90, gpa: "4.00", nextDeadline: "25 Jan 2025, 11:59 PM" },
    overview: {
      description: "Strategic human resource planning, recruitment, performance appraisal systems, and organizational development.",
      syllabus: [
        "Introduction to Strategic HRM",
        "Job Analysis & Workforce Planning",
        "Recruitment & Selection Interviews",
        "Employee Training & Onboarding",
        "Performance Management Systems",
        "Compensation & Benefits Design",
        "Workplace Ethics & Labor Law",
        "Organizational Culture & Leadership"
      ],
      objectives: ["Draft job descriptions", "Conduct structured appraisal reviews"],
      prerequisites: "Principles of Management",
      textbooks: [{ title: "Human Resource Management", author: "Gary Dessler", edition: "16th Edition" }],
      gradingPolicy: [
        { item: "Quizzes", weight: "15%", description: "Case study quizzes." },
        { item: "Assignments", weight: "15%", description: "Policy briefs." },
        { item: "Mid Term", weight: "25%", description: "Written exam." },
        { item: "Final Term", weight: "45%", description: "Final exam." }
      ],
      announcements: []
    },
    coursework: {
      assignments: [
        { id: "as-hrm-1", title: "Assignment 1 — Hiring Matrix Case Study", uploadedDate: "11 Jan 2025, 9:00 AM", dueDate: "25 Jan 2025, 11:59 PM", maxPoints: 10, weight: "5%", status: "Submitted", submittedFile: "hrm_case.pdf", submittedAt: "15 Jan 2025", obtainedScore: 9 }
      ],
      quizzes: [
        { id: "qz-hrm-1", title: "Quiz 1 — Job Analysis", uploadedDate: "08 Jan 2025, 9:00 AM", dueDate: "13 Jan 2025, 10:00 AM", date: "April 13, 2025", maxPoints: 10, obtainedScore: 9, classAverage: 8.4, topics: "Workforce Planning", status: "Graded" }
      ],
      exams: [
        { id: "ex-hrm-1", title: "Mid Term", date: "April 13, 2025", maxPoints: 25, obtainedScore: 22, status: "Completed" },
        { id: "ex-hrm-2", title: "Final Term", date: "June 19, 2025", maxPoints: 50, obtainedScore: 45, status: "Completed" }
      ],
      gdb: [],
      mdb: []
    },
    attendanceLedger: [
      { id: "hrm-1", lectureNo: 1, sessionType: "Class", date: "4/3/2026", startTime: "10:00:00 AM", endTime: "11:00:00 AM", day: "Monday", slot: "Slot 2", room: "D-101", topic: "Strategic HRM", status: "PRESENT" },
      { id: "hrm-2", lectureNo: 2, sessionType: "Class", date: "4/5/2026", startTime: "10:00:00 AM", endTime: "11:00:00 AM", day: "Wednesday", slot: "Slot 2", room: "D-101", topic: "Job Analysis", status: "ABSENT" },
      { id: "hrm-3", lectureNo: 3, sessionType: "Class", date: "4/10/2026", startTime: "10:00:00 AM", endTime: "11:00:00 AM", day: "Monday", slot: "Slot 2", room: "D-101", topic: "Performance Appraisal", status: "PRESENT" }
    ],
    leaveRequests: [],
    lectureHub: {
      recordings: [{ id: "rec-hrm-1", lectureNo: 1, title: "Foundations of Modern HR", date: "05 Jan 2025", duration: "45 min", timestamps: [{ time: "00:00", label: "Intro" }] }],
      materials: [{ id: "mat-hrm-1", title: "Gary Dessler — HRM Core Textbook", category: "Textbook", format: "PDF", size: "7.5 MB", uploadDate: "05 Jan 2025", downloadsCount: 63 }]
    }
  },
  {
    id: "hci",
    code: "CSC 444",
    title: "HCI",
    creditHours: 3,
    section: "BCS 7 C",
    semester: "Spring 2025",
    teacher: {
      name: "Ms. Hina Qaiser",
      role: "Lecturer",
      avatar: "HQ",
      status: "Available in Office",
      office: "C Block, 1st Floor, Room C-107",
      email: "hina.qaiser@cuisahiwal.edu.pk",
      officeHours: "Wed & Fri: 09:00 AM – 11:00 AM",
      bio: "Focuses on human-computer interaction, usability heuristics, and accessible interaction design."
    },
    attendance: { percentage: 88, attended: 16, total: 18, absent: 2, late: 0, excused: 0, requiredConsecutive: 0 },
    standing: { estimatedGrade: "89.0% · A", scorePercentage: 89, gpa: "3.90", nextDeadline: "27 Jan 2025, 11:59 PM" },
    overview: {
      description: "Usability engineering, user-centered design loops, interaction models, heuristics, and accessibility evaluation.",
      syllabus: [
        "Principles of Human-Computer Interaction",
        "Mental Models & Cognitive Load",
        "Interaction Design & Wireframing",
        "Nielsen's 10 Usability Heuristics",
        "Prototyping & Responsive Layouts",
        "User Testing & Think-Aloud Protocols",
        "Web Accessibility & Inclusive UX",
        "Design Systems & Typography"
      ],
      objectives: ["Conduct heuristic evaluations", "Build accessible UI prototypes"],
      prerequisites: "Software Engineering",
      textbooks: [{ title: "The Design of Everyday Things", author: "Don Norman", edition: "Revised" }],
      gradingPolicy: [
        { item: "Quizzes", weight: "15%", description: "Short theory quizzes." },
        { item: "Assignments", weight: "15%", description: "UI audits." },
        { item: "Mid Term", weight: "25%", description: "Written exam." },
        { item: "Final Term", weight: "45%", description: "Final exam." }
      ],
      announcements: []
    },
    coursework: {
      assignments: [
        { id: "as-hci-1", title: "Assignment 1 — Usability Heuristic Audit", uploadedDate: "12 Jan 2025, 10:00 AM", dueDate: "27 Jan 2025, 11:59 PM", maxPoints: 10, weight: "5%", status: "Pending", obtainedScore: 9 }
      ],
      quizzes: [
        { id: "qz-hci-1", title: "Quiz 1 — Norman's Principles", uploadedDate: "09 Jan 2025, 10:00 AM", dueDate: "14 Jan 2025, 12:00 PM", date: "April 13, 2025", maxPoints: 10, obtainedScore: 9, classAverage: 8.0, topics: "Affordances & Signifiers", status: "Graded" }
      ],
      exams: [
        { id: "ex-hci-1", title: "Mid Term", date: "April 13, 2025", maxPoints: 25, obtainedScore: 21, status: "Completed" },
        { id: "ex-hci-2", title: "Final Term", date: "June 20, 2025", maxPoints: 50, obtainedScore: 44, status: "Completed" }
      ],
      gdb: [],
      mdb: []
    },
    attendanceLedger: [
      { id: "hci-1", lectureNo: 1, sessionType: "Class", date: "4/3/2026", startTime: "12:00:00 PM", endTime: "01:00:00 PM", day: "Wednesday", slot: "Slot 3", room: "C-104", topic: "Usability Principles", status: "PRESENT" },
      { id: "hci-2", lectureNo: 2, sessionType: "Lab", date: "4/5/2026", startTime: "02:00:00 PM", endTime: "03:30:00 PM", day: "Friday", slot: "Slot 4", room: "C Lab-1", topic: "Wireframing Lab", status: "PRESENT" },
      { id: "hci-3", lectureNo: 3, sessionType: "Lab", date: "4/12/2026", startTime: "02:00:00 PM", endTime: "03:30:00 PM", day: "Friday", slot: "Slot 4", room: "C Lab-1", topic: "Usability Audit Lab", status: "ABSENT" }
    ],
    leaveRequests: [],
    lectureHub: {
      recordings: [{ id: "rec-hci-1", lectureNo: 1, title: "Affordances, Feedback & Signifiers", date: "06 Jan 2025", duration: "46 min", timestamps: [{ time: "00:00", label: "Overview" }] }],
      materials: [{ id: "mat-hci-1", title: "Don Norman — Design of Everyday Things", category: "Textbook", format: "PDF", size: "5.8 MB", uploadDate: "06 Jan 2025", downloadsCount: 92 }]
    }
  },
  {
    id: "discrete",
    code: "MTH 231",
    title: "Discrete Mathematics",
    creditHours: 3,
    section: "BCS 7 C",
    semester: "Spring 2025",
    teacher: {
      name: "Dr. Nasir Mehmood",
      role: "Tenured Professor",
      avatar: "NM",
      status: "Consultation Hours",
      office: "A Block, 2nd Floor, Room A-209",
      email: "nasir.mehmood@cuisahiwal.edu.pk",
      officeHours: "Mon & Thu: 11:00 AM – 01:00 PM",
      bio: "Mathematician working on combinatorics, graph theory, and discrete algorithmic proofs."
    },
    attendance: { percentage: 79, attended: 15, total: 19, absent: 4, late: 0, excused: 0, requiredConsecutive: 1 },
    standing: { estimatedGrade: "81.0% · B+", scorePercentage: 81, gpa: "3.35", nextDeadline: "29 Jan 2025, 11:59 PM" },
    overview: {
      description: "Propositional logic, predicate calculus, proof techniques, sets, functions, recurrence relations, and graph theory.",
      syllabus: [
        "Propositional Logic & Truth Tables",
        "Predicate Quantifiers & Inference",
        "Mathematical Induction Proofs",
        "Set Theory, Relations & Equivalence",
        "Counting, Permutations & Combinations",
        "Pigeonhole Principle & Recurrences",
        "Graphs, Paths & Connectivity",
        "Trees & Spanning Structures"
      ],
      objectives: ["Write rigorous inductive proofs", "Solve recurrence and graph problems"],
      prerequisites: "None",
      textbooks: [{ title: "Discrete Mathematics and Its Applications", author: "Kenneth H. Rosen", edition: "8th Edition" }],
      gradingPolicy: [
        { item: "Quizzes", weight: "15%", description: "Proof quizzes." },
        { item: "Assignments", weight: "15%", description: "Problem sets." },
        { item: "Mid Term", weight: "25%", description: "Written exam." },
        { item: "Final Term", weight: "45%", description: "Final exam." }
      ],
      announcements: []
    },
    coursework: {
      assignments: [
        { id: "as-dm-1", title: "Assignment 1 — Logic & Proof Sets", uploadedDate: "14 Jan 2025, 8:00 AM", dueDate: "29 Jan 2025, 11:59 PM", maxPoints: 10, weight: "5%", status: "Pending", obtainedScore: 8 }
      ],
      quizzes: [
        { id: "qz-dm-1", title: "Quiz 1 — Truth Tables & Quantifiers", uploadedDate: "09 Jan 2025, 9:00 AM", dueDate: "15 Jan 2025, 10:00 AM", date: "April 13, 2025", maxPoints: 10, obtainedScore: 8, classAverage: 7.3, topics: "Propositional Logic", status: "Graded" }
      ],
      exams: [
        { id: "ex-dm-1", title: "Mid Term", date: "April 13, 2025", maxPoints: 25, obtainedScore: 19, status: "Completed" },
        { id: "ex-dm-2", title: "Final Term", date: "June 21, 2025", maxPoints: 50, obtainedScore: 40, status: "Completed" }
      ],
      gdb: [],
      mdb: []
    },
    attendanceLedger: [
      { id: "dm-1", lectureNo: 1, sessionType: "Class", date: "4/4/2026", startTime: "08:30:00 AM", endTime: "10:00:00 AM", day: "Tuesday", slot: "Slot 1", room: "A-204", topic: "Propositional Calculus", status: "PRESENT" },
      { id: "dm-2", lectureNo: 2, sessionType: "Class", date: "4/6/2026", startTime: "08:30:00 AM", endTime: "10:00:00 AM", day: "Thursday", slot: "Slot 1", room: "A-204", topic: "Proof by Induction", status: "ABSENT" },
      { id: "dm-3", lectureNo: 3, sessionType: "Class", date: "4/11/2026", startTime: "08:30:00 AM", endTime: "10:00:00 AM", day: "Tuesday", slot: "Slot 1", room: "A-204", topic: "Graph Connectivity", status: "PRESENT" }
    ],
    leaveRequests: [],
    lectureHub: {
      recordings: [{ id: "rec-dm-1", lectureNo: 1, title: "Rules of Inference & Induction", date: "08 Jan 2025", duration: "50 min", timestamps: [{ time: "00:00", label: "Logic" }] }],
      materials: [{ id: "mat-dm-1", title: "Kenneth Rosen — Discrete Math 8th Edition", category: "Textbook", format: "PDF", size: "14.2 MB", uploadDate: "08 Jan 2025", downloadsCount: 130 }]
    }
  }
];

const COURSE_SLUG_ALIASES: Record<string, string> = {
  db: "discrete",
  se: "hci",
  os: "infosec",
  ai: "ml",
  "csc-354": "compiler",
  csc354: "compiler",
  csc441: "compiler",
  csc442: "infosec",
  csc443: "ml",
  mgt321: "hrm",
  csc444: "hci",
  mth231: "discrete"
};

export function getCourseById(id: string): EnrolledCourse | undefined {
  const normalized = id.toLowerCase().replace(/\s+/g, "");
  const aliasId = COURSE_SLUG_ALIASES[normalized] || COURSE_SLUG_ALIASES[id.toLowerCase()];
  if (aliasId) {
    return COURSES_CATALOG.find((c) => c.id === aliasId);
  }
  return COURSES_CATALOG.find(
    (c) =>
      c.id.toLowerCase() === id.toLowerCase() ||
      c.code.toLowerCase().replace(/[\s-]+/g, "") === normalized.replace(/-/g, "")
  );
}
