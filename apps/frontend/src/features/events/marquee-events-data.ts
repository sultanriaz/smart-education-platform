export type MarqueeSeasonMode = "SPORTS_GALA" | "TECH_GALA" | "CAREER_CONVOCATION";

export interface TournamentMatch {
  id: string;
  sport: "Cricket" | "Futsal" | "Badminton" | "Basketball" | "Table Tennis" | "Chess" | "Athletics";
  stage: "Round of 16" | "Quarter Final" | "Semi Final" | "Grand Final" | "Group Stage";
  day: "Day 1 (Monday)" | "Day 2 (Tuesday)" | "Day 3 (Wednesday)" | "Day 4 (Thursday)" | "Day 5 (Friday)";
  time: string;
  venue: string;
  groundMapZone: string;
  teamA: {
    name: string;
    department: "Computer Science" | "Software Engineering" | "Electrical Engineering" | "Management Sciences" | "Natural Sciences";
    score?: string;
    isWinner?: boolean;
    jerseyColor: string;
  };
  teamB: {
    name: string;
    department: "Computer Science" | "Software Engineering" | "Electrical Engineering" | "Management Sciences" | "Natural Sciences";
    score?: string;
    isWinner?: boolean;
    jerseyColor: string;
  };
  status: "LIVE_NOW" | "UPCOMING" | "COMPLETED";
  summaryResult?: string;
  mvpPlayer?: string;
}

export interface DepartmentStanding {
  rank: number;
  department: string;
  code: string;
  goldMedals: number;
  silverMedals: number;
  bronzeMedals: number;
  totalPoints: number;
  keyStrength: string;
  colorScheme: {
    badge: string;
    border: string;
  };
}

export interface BracketNode {
  round: "Quarter Finals" | "Semi Finals" | "Grand Final";
  matches: {
    id: string;
    team1: string;
    score1: string;
    team2: string;
    score2: string;
    winner: string;
    timing: string;
  }[];
}

export interface TechGalaCompetition {
  id: string;
  title: string;
  category: "Competitive Programming" | "AI & Machine Learning" | "Hackathon 48h" | "Cyber Security CTF" | "UI/UX Redesign";
  venue: string;
  timeWindow: string;
  prizePool: string;
  registeredTeams: number;
  status: "REGISTRATION_OPEN" | "HACKING_IN_PROGRESS" | "JUDGING" | "CONCLUDED";
  mentor: string;
}

export interface CareerFairCompany {
  id: string;
  companyName: string;
  boothNumber: string;
  sector: "Software Engineering & AI" | "Fintech & Banking" | "Cloud & DevOps" | "Telecom & Networks";
  openRoles: string[];
  interviewSlots: string;
  hiringTarget: string;
}

// ================= DATASETS =================

export const SPORTS_FIXTURES: TournamentMatch[] = [
  {
    id: "match-cricket-final",
    sport: "Cricket",
    stage: "Grand Final",
    day: "Day 5 (Friday)",
    time: "02:30 PM – 05:30 PM",
    venue: "Main Oval Cricket Ground",
    groundMapZone: "Oval Center Pitch",
    teamA: {
      name: "CS Cyber Knights",
      department: "Computer Science",
      score: "162/4 (19.1 ov)",
      isWinner: true,
      jerseyColor: "bg-primary text-on-primary"
    },
    teamB: {
      name: "EE Spark Warriors",
      department: "Electrical Engineering",
      score: "158/8 (20.0 ov)",
      isWinner: false,
      jerseyColor: "bg-accent text-accent-fg"
    },
    status: "COMPLETED",
    summaryResult: "CS Cyber Knights won by 6 wickets with 5 balls remaining",
    mvpPlayer: "Hamza Tariq (CS) — 68 runs (41b) & 2 wickets"
  },
  {
    id: "match-futsal-semi",
    sport: "Futsal",
    stage: "Semi Final",
    day: "Day 3 (Wednesday)",
    time: "11:00 AM – 12:30 PM",
    venue: "Sports Complex Futsal Turf Court 1",
    groundMapZone: "Turf Arena A",
    teamA: {
      name: "SE Agile Strikers",
      department: "Software Engineering",
      score: "3",
      isWinner: true,
      jerseyColor: "bg-success text-success-fg"
    },
    teamB: {
      name: "MS Business Titans",
      department: "Management Sciences",
      score: "1",
      isWinner: false,
      jerseyColor: "bg-secondary text-secondary-fg"
    },
    status: "COMPLETED",
    summaryResult: "SE Agile Strikers advance to Grand Final (3 - 1)",
    mvpPlayer: "Daniyal Shah (SE) — 2 Goals, 1 Assist"
  },
  {
    id: "match-cricket-live",
    sport: "Cricket",
    stage: "Semi Final",
    day: "Day 3 (Wednesday)",
    time: "10:00 AM – 01:00 PM",
    venue: "Main Oval Cricket Ground",
    groundMapZone: "Oval Center Pitch",
    teamA: {
      name: "CS Cyber Knights",
      department: "Computer Science",
      score: "134/2 (14.4 ov)",
      jerseyColor: "bg-primary text-on-primary"
    },
    teamB: {
      name: "MS Business Titans",
      department: "Management Sciences",
      score: "130/10 (18.3 ov)",
      jerseyColor: "bg-secondary text-secondary-fg"
    },
    status: "LIVE_NOW",
    summaryResult: "CS needs 0 runs to win; targeted run rate 0.00",
    mvpPlayer: "Live Match in Progress"
  },
  {
    id: "match-badminton-live",
    sport: "Badminton",
    stage: "Quarter Final",
    day: "Day 2 (Tuesday)",
    time: "02:00 PM – 03:30 PM",
    venue: "Gymnasium Indoor Arena (Court 2)",
    groundMapZone: "Gym Court 2",
    teamA: {
      name: "CS Smashers (Girls)",
      department: "Computer Science",
      score: "21-18, 19-21, 14-11",
      jerseyColor: "bg-primary text-on-primary"
    },
    teamB: {
      name: "EE Volts (Girls)",
      department: "Electrical Engineering",
      score: "18-21, 21-19, 11-14",
      jerseyColor: "bg-accent text-accent-fg"
    },
    status: "LIVE_NOW",
    summaryResult: "Set 3 deciding set currently in play at Court 2",
    mvpPlayer: "Aiman Noor (CS)"
  },
  {
    id: "match-basketball-up",
    sport: "Basketball",
    stage: "Grand Final",
    day: "Day 4 (Thursday)",
    time: "02:00 PM – 04:00 PM",
    venue: "Hard-court Outdoor Basketball Arena",
    groundMapZone: "East Basketball Hardcourt",
    teamA: {
      name: "SE Agile Strikers",
      department: "Software Engineering",
      jerseyColor: "bg-success text-success-fg"
    },
    teamB: {
      name: "CS Cyber Knights",
      department: "Computer Science",
      jerseyColor: "bg-primary text-on-primary"
    },
    status: "UPCOMING",
    summaryResult: "Grand Final Clash scheduled for Thursday afternoon"
  },
  {
    id: "match-table-tennis-qf",
    sport: "Table Tennis",
    stage: "Quarter Final",
    day: "Day 1 (Monday)",
    time: "11:30 AM – 02:00 PM",
    venue: "Student Activity Center (SAC Hall 1)",
    groundMapZone: "SAC Ground Floor Hall",
    teamA: {
      name: "MS Business Titans",
      department: "Management Sciences",
      score: "3 Sets",
      isWinner: true,
      jerseyColor: "bg-secondary text-secondary-fg"
    },
    teamB: {
      name: "NS Science Guild",
      department: "Natural Sciences",
      score: "1 Set",
      isWinner: false,
      jerseyColor: "bg-subtle text-ink border border-line"
    },
    status: "COMPLETED",
    summaryResult: "MS Titans won 3-1 sets"
  },
  {
    id: "match-chess-final",
    sport: "Chess",
    stage: "Grand Final",
    day: "Day 4 (Thursday)",
    time: "10:30 AM – 01:00 PM",
    venue: "Central Library Silent Annex",
    groundMapZone: "Library Chess Room",
    teamA: {
      name: "CS Grandmasters",
      department: "Computer Science",
      jerseyColor: "bg-primary text-on-primary"
    },
    teamB: {
      name: "SE Logic Masters",
      department: "Software Engineering",
      jerseyColor: "bg-success text-success-fg"
    },
    status: "UPCOMING",
    summaryResult: "Best of 3 Classical FIDE Rapid 15+10 time control"
  }
];

export const DEPARTMENT_STANDINGS: DepartmentStanding[] = [
  {
    rank: 1,
    department: "Computer Science",
    code: "CS",
    goldMedals: 3,
    silverMedals: 2,
    bronzeMedals: 1,
    totalPoints: 185,
    keyStrength: "Cricket Champions, Badminton & Chess Dominance",
    colorScheme: {
      badge: "bg-primary-soft text-primary-ink",
      border: "border-primary/40"
    }
  },
  {
    rank: 2,
    department: "Software Engineering",
    code: "SE",
    goldMedals: 2,
    silverMedals: 3,
    bronzeMedals: 2,
    totalPoints: 155,
    keyStrength: "Futsal Champions & Basketball Finalists",
    colorScheme: {
      badge: "bg-success-soft text-success-ink",
      border: "border-success/40"
    }
  },
  {
    rank: 3,
    department: "Electrical Engineering",
    code: "EE",
    goldMedals: 1,
    silverMedals: 2,
    bronzeMedals: 3,
    totalPoints: 120,
    keyStrength: "Volleyball Winners & Cricket Runners-up",
    colorScheme: {
      badge: "bg-accent-soft text-accent-ink",
      border: "border-accent/40"
    }
  },
  {
    rank: 4,
    department: "Management Sciences",
    code: "MS",
    goldMedals: 1,
    silverMedals: 1,
    bronzeMedals: 2,
    totalPoints: 95,
    keyStrength: "Table Tennis Champions & Athletics Sprints",
    colorScheme: {
      badge: "bg-secondary-soft text-secondary-ink",
      border: "border-secondary/40"
    }
  },
  {
    rank: 5,
    department: "Natural Sciences & Math",
    code: "NS",
    goldMedals: 0,
    silverMedals: 1,
    bronzeMedals: 2,
    totalPoints: 60,
    keyStrength: "Athletics 400m Silver & Relay",
    colorScheme: {
      badge: "bg-subtle text-ink border border-line",
      border: "border-line"
    }
  }
];

export const TOURNAMENT_BRACKETS: BracketNode[] = [
  {
    round: "Quarter Finals",
    matches: [
      { id: "qf-1", team1: "CS Knights", score1: "154/6", team2: "NS Guild", score2: "112/9", winner: "CS Knights", timing: "Day 1 (Mon)" },
      { id: "qf-2", team1: "MS Titans", score1: "142/7", team2: "Bio Sci", score2: "138/8", winner: "MS Titans", timing: "Day 1 (Mon)" },
      { id: "qf-3", team1: "SE Strikers", score1: "160/5", team2: "Civil Eng", score2: "120/10", winner: "SE Strikers", timing: "Day 2 (Tue)" },
      { id: "qf-4", team1: "EE Warriors", score1: "172/4", team2: "Mech Eng", score2: "155/6", winner: "EE Warriors", timing: "Day 2 (Tue)" }
    ]
  },
  {
    round: "Semi Finals",
    matches: [
      { id: "sf-1", team1: "CS Knights", score1: "134/2", team2: "MS Titans", score2: "130/10", winner: "CS Knights", timing: "Day 3 (Wed)" },
      { id: "sf-2", team1: "EE Warriors", score1: "165/5", team2: "SE Strikers", score2: "162/8", winner: "EE Warriors", timing: "Day 3 (Wed)" }
    ]
  },
  {
    round: "Grand Final",
    matches: [
      { id: "gf-1", team1: "CS Knights", score1: "162/4", team2: "EE Warriors", score2: "158/8", winner: "CS Knights 🏆", timing: "Day 5 (Fri)" }
    ]
  }
];

export const TECH_GALA_EVENTS: TechGalaCompetition[] = [
  {
    id: "tg-1",
    title: "HackCOMSATS 2026: 48-Hour AI Product Sprint",
    category: "Hackathon 48h",
    venue: "Software Engineering Lab 1 & 2 (Engineering Labs Ground Floor)",
    timeWindow: "Friday 05:00 PM – Sunday 05:00 PM",
    prizePool: "PKR 250,000 + Incubation Grant",
    registeredTeams: 28,
    status: "HACKING_IN_PROGRESS",
    mentor: "Dr. Munir Ahmad & Industry Mentors from Systems Ltd"
  },
  {
    id: "tg-2",
    title: "CodeSpree: ICPC-Style Algorithmic Speed Challenge",
    category: "Competitive Programming",
    venue: "Auditorium C-301 (Block C 3rd Floor)",
    timeWindow: "Saturday 10:00 AM – 02:00 PM",
    prizePool: "PKR 100,000 + Fast-Track Job Offers",
    registeredTeams: 45,
    status: "REGISTRATION_OPEN",
    mentor: "Dr. Javed Iqbal"
  },
  {
    id: "tg-3",
    title: "CyberDefend CTF: Capture-The-Flag Security Siege",
    category: "Cyber Security CTF",
    venue: "Networks & Cyber Security Lab (Engineering Labs 1st Floor)",
    timeWindow: "Saturday 02:30 PM – 07:00 PM",
    prizePool: "PKR 80,000 + Cisco Certified Vouchers",
    registeredTeams: 18,
    status: "REGISTRATION_OPEN",
    mentor: "Engr. Bilal Khalid"
  },
  {
    id: "tg-4",
    title: "DesignMatrix: 6-Hour Figma to Fullstack Redesign",
    category: "UI/UX Redesign",
    venue: "AI & Robotics Lab (Engineering Labs Ground Floor)",
    timeWindow: "Sunday 11:00 AM – 05:00 PM",
    prizePool: "PKR 70,000 + Design Agency Contracts",
    registeredTeams: 22,
    status: "REGISTRATION_OPEN",
    mentor: "Ms. Hina Qaiser"
  }
];

export const CAREER_FAIR_COMPANIES: CareerFairCompany[] = [
  {
    id: "co-1",
    companyName: "Systems Limited",
    boothNumber: "Stall #01 (Main Auditorium Center)",
    sector: "Software Engineering & AI",
    openRoles: ["Associate Software Engineer (Fullstack)", "Junior Cloud DevOps", "Data Scientist"],
    interviewSlots: "Walk-in Screening: 09:30 AM – 04:30 PM",
    hiringTarget: "25 Fresh Graduates"
  },
  {
    id: "co-2",
    companyName: "NetSol Technologies",
    boothNumber: "Stall #04 (Main Auditorium West Wing)",
    sector: "Fintech & Banking",
    openRoles: ["C# / .NET Core Engineer", "QA Automation Tester", "Security Analyst"],
    interviewSlots: "On-spot Technical Tests: 10:00 AM – 03:00 PM",
    hiringTarget: "18 Graduates"
  },
  {
    id: "co-3",
    companyName: "Devsinc",
    boothNumber: "Stall #08 (Auditorium East Corridor)",
    sector: "Software Engineering & AI",
    openRoles: ["React / TypeScript Frontend Dev", "Python FastAPI / AI Engineer", "Mobile Flutter Dev"],
    interviewSlots: "Portfolio Review & Coding Viva: 11:00 AM – 04:00 PM",
    hiringTarget: "30 Interns & Hires"
  },
  {
    id: "co-4",
    companyName: "Jazz Telecom",
    boothNumber: "Stall #12 (D Block Incubation Center)",
    sector: "Telecom & Networks",
    openRoles: ["NOC Operations Engineer", "Cyber Defense Trainee", "Business Analyst"],
    interviewSlots: "HR Panel Interviews: 10:00 AM – 02:30 PM",
    hiringTarget: "12 Management & EE Grads"
  }
];
