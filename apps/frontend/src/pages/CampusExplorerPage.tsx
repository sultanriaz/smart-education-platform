import { useState } from "react";
import { Link } from "react-router-dom";
import {
  GraduationCap,
  Bus,
  Calendar,
  Clock,
  Compass,
  MapPin,
  Search,
  Sparkles,
  Trophy,
  Users,
  Building,
  BookOpen,
  ArrowRight,
  Lock,
  CheckCircle2,
  Moon,
  Sun,
  ShieldCheck,
  ChevronRight
} from "lucide-react";
import { useAuth } from "../features/auth/useAuth";
import { primaryRole } from "../features/auth/permissions";

// Static campus data matching the real university profile
const CAMPUS_BLOCKS = [
  {
    block: "A Block",
    name: "Engineering & Natural Sciences Block",
    floors: [
      {
        floor: "Ground Floor",
        rooms: [
          { room: "A-01", type: "Physics Lab", capacity: 45 },
          { room: "A-02", type: "Lecture Hall", capacity: 70 },
          { room: "A-03", type: "Faculty Lounge", capacity: 25 }
        ]
      },
      {
        floor: "1st Floor",
        rooms: [
          { room: "A-101", type: "Computer Lab 1", capacity: 50 },
          { room: "A-102", type: "Smart Classroom", capacity: 60 },
          { room: "A-103", type: "Hardware Lab", capacity: 40 }
        ]
      },
      {
        floor: "2nd Floor",
        rooms: [
          { room: "A-201", type: "Lecture Hall", capacity: 65 },
          { room: "A-202", type: "Lecture Hall", capacity: 65 },
          { room: "A-203", type: "Seminar Room", capacity: 55 }
        ]
      },
      {
        floor: "3rd Floor",
        rooms: [
          { room: "A-301", type: "Faculty Offices (CS)", capacity: 20 },
          { room: "A-302", type: "HOD Computer Science", capacity: 15 },
          { room: "A-303", type: "Dean Academic Office", capacity: 20 }
        ]
      }
    ]
  },
  {
    block: "C Block",
    name: "Computer Science & IT Block",
    floors: [
      {
        floor: "Ground Floor",
        rooms: [
          { room: "C-01", type: "Software Engineering Lab", capacity: 55 },
          { room: "C-02", type: "AI & Robotics Lab", capacity: 45 },
          { room: "C-03", type: "Lecture Theater 1", capacity: 120 }
        ]
      },
      {
        floor: "1st Floor",
        rooms: [
          { room: "C-101", type: "Classroom BCS-5A", capacity: 65 },
          { room: "C-102", type: "Classroom BCS-5B", capacity: 65 },
          { room: "C-103", type: "Graduate Research Lab", capacity: 35 }
        ]
      },
      {
        floor: "2nd Floor",
        rooms: [
          { room: "C-201", type: "Classroom BCS-7A", capacity: 65 },
          { room: "C-204", type: "Classroom BCS-7C", capacity: 60 },
          { room: "C-205", type: "Data Science Lab", capacity: 45 }
        ]
      }
    ]
  },
  {
    block: "D Block",
    name: "Management Sciences & Humanities Block",
    floors: [
      {
        floor: "Ground Floor",
        rooms: [
          { room: "D-01", type: "Central Library & E-Resource Center", capacity: 250 },
          { room: "D-02", type: "Auditorium Hall", capacity: 350 }
        ]
      },
      {
        floor: "1st Floor",
        rooms: [
          { room: "D-101", type: "BBA Lecture Room", capacity: 60 },
          { room: "D-102", type: "Incubation Center", capacity: 40 }
        ]
      }
    ]
  }
];

const FACULTY_DIRECTORY = [
  {
    name: "Prof. Dr. Saleem Farooq Shaukat",
    role: "Campus Director",
    department: "Executive Administration",
    office: "Directorate, Admin Block Ground Floor",
    email: "director@cuisahiwal.edu.pk"
  },
  {
    name: "Dr. Munir Ahmad",
    role: "Associate Professor / Batch Advisor",
    department: "Computer Science",
    office: "A Block, 3rd Floor, Room A-301",
    email: "drmunir@cuisahiwal.edu.pk"
  },
  {
    name: "Dr. Majid Hussain",
    role: "Head of Department (HOD)",
    department: "Computer Science",
    office: "A Block, 3rd Floor, Room A-302",
    email: "hod-cs@cuisahiwal.edu.pk"
  },
  {
    name: "Dr. Muhammad Asim",
    role: "Assistant Professor",
    department: "Computer Science",
    office: "C Block, 2nd Floor, Room C-203",
    email: "masim@cuisahiwal.edu.pk"
  },
  {
    name: "Dr. Raja Rizwan",
    role: "In-charge Student Affairs",
    department: "Management Sciences",
    office: "D Block, 1st Floor, Room D-104",
    email: "studentaffairs@cuisahiwal.edu.pk"
  }
];

const BUS_SCHEDULES = [
  {
    busNo: "Bus #04",
    route: "Farid Town & Girls Hostel Express",
    departure: "07:30 AM",
    stops: [
      { stop: "Farid Town Point", arrivalTime: "07:45 AM" },
      { stop: "Jinnah Hall Chowk", arrivalTime: "07:55 AM" },
      { stop: "Girls Hostel", arrivalTime: "08:10 AM" },
      { stop: "Campus Main Gate", arrivalTime: "08:25 AM" }
    ]
  },
  {
    busNo: "Bus #07",
    route: "High Court & College Road Shuttle",
    departure: "07:35 AM",
    stops: [
      { stop: "High Court Chowk", arrivalTime: "07:50 AM" },
      { stop: "College Road Point", arrivalTime: "08:00 AM" },
      { stop: "Arifwala By-pass", arrivalTime: "08:15 AM" },
      { stop: "Campus Main Gate", arrivalTime: "08:25 AM" }
    ]
  },
  {
    busNo: "Bus #12",
    route: "City Terminal & Chichawatni Feeder",
    departure: "07:15 AM",
    stops: [
      { stop: "Chichawatni Station", arrivalTime: "07:25 AM" },
      { stop: "Harappa Station Point", arrivalTime: "07:50 AM" },
      { stop: "Campus Main Gate", arrivalTime: "08:25 AM" }
    ]
  }
];

const SPORTS_WEEK_EVENTS = [
  {
    day: "Day 1 (Monday)",
    matches: [
      { sport: "Cricket Gala (Opening Match)", ground: "Main Oval Cricket Ground", time: "10:00 AM – 01:00 PM" },
      { sport: "Table Tennis Singles (Men)", ground: "Gymnasium Hall 1", time: "11:30 AM – 02:00 PM" }
    ]
  },
  {
    day: "Day 2 (Tuesday)",
    matches: [
      { sport: "Football Championship (BCS vs BSE)", ground: "Sports Complex Football Field", time: "11:00 AM – 01:00 PM" },
      { sport: "Badminton Tournament (Girls)", ground: "Student Activity Center", time: "02:00 PM – 04:30 PM" }
    ]
  },
  {
    day: "Day 3 (Wednesday)",
    matches: [
      { sport: "Cricket Semi-Finals", ground: "Main Oval Cricket Ground", time: "09:30 AM – 01:00 PM" },
      { sport: "Volleyball Invitational", ground: "Outdoor Volleyball Court", time: "02:30 PM – 04:30 PM" }
    ]
  },
  {
    day: "Day 4 (Thursday)",
    matches: [
      { sport: "Athletics 100m & 400m Sprints", ground: "Athletics Track", time: "10:30 AM – 12:30 PM" },
      { sport: "Basketball Finals", ground: "Hard-court Basketball Arena", time: "02:00 PM – 04:00 PM" }
    ]
  },
  {
    day: "Day 5 (Friday)",
    matches: [
      { sport: "Cricket Grand Final & Awards Ceremony", ground: "Main Oval Cricket Ground", time: "02:30 PM – 05:30 PM" }
    ]
  }
];

export function CampusExplorerPage() {
  const { user, state } = useAuth();
  const [activeTab, setActiveTab] = useState<"overview" | "hub" | "free_slots" | "transport" | "sports">("overview");
  const [facultySearch, setFacultySearch] = useState("");
  const [selectedSportDay, setSelectedSportDay] = useState(0);
  const [selectedSlotDay, setSelectedSlotDay] = useState("Wednesday");
  const [selectedSlot, setSelectedSlot] = useState("Slot 2 (10:15 - 11:45)");
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme ?? "light");

  const toggleTheme = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem("sep-theme", next);
    } catch {
      // ignore
    }
  };

  const filteredFaculty = FACULTY_DIRECTORY.filter(
    (f) =>
      f.name.toLowerCase().includes(facultySearch.toLowerCase()) ||
      f.department.toLowerCase().includes(facultySearch.toLowerCase()) ||
      f.role.toLowerCase().includes(facultySearch.toLowerCase())
  );

  const role = user ? primaryRole(user.roles) : null;

  return (
    <div className="min-h-screen bg-bg text-ink transition">
      {/* Top Universal Header */}
      <header className="sticky top-0 z-40 border-b border-line bg-panel/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-600 text-white shadow-xs">
              <GraduationCap size={22} />
            </span>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold tracking-tight text-base sm:text-lg">COMSATS SmartEdu</span>
                <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400">
                  Open Campus
                </span>
              </div>
              <p className="hidden text-xs text-muted sm:block">Sahiwal Campus · Academic & Facilities Portal</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={toggleTheme}
              aria-label="Toggle theme"
              className="flex h-9 w-9 items-center justify-center rounded-xl border border-line bg-surface text-muted hover:text-ink transition shadow-2xs"
            >
              {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
            </button>

            {state === "authenticated" && user ? (
              <Link
                to={role ? `/app/${role}` : "/app"}
                className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-3.5 py-2 text-xs sm:text-sm font-semibold text-white shadow-xs hover:bg-brand-700 transition"
              >
                <span>Workspace ({role})</span>
                <ArrowRight size={14} />
              </Link>
            ) : (
              <Link
                to="/login"
                className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-4 py-2 text-xs sm:text-sm font-semibold text-white shadow-xs hover:bg-brand-700 transition"
              >
                <span>Universal Sign In</span>
                <ArrowRight size={14} />
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Hero Welcome Banner */}
      <div className="border-b border-line bg-surface/50">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 sm:py-12">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-brand-500/30 bg-brand-500/10 px-3 py-1 text-xs font-semibold text-brand-700 dark:text-brand-300 mb-3">
              <Compass size={14} />
              <span>Universal Adaptive Campus Gateway</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight">
              One Connected Campus.<br />
              <span className="text-brand-600 dark:text-brand-400">Every resource at your fingertips.</span>
            </h1>
            <p className="mt-3 text-sm sm:text-base text-muted leading-relaxed">
              Explore public transit shuttle schedules, free study rooms across blocks, university directory, sports week fixtures, and curriculum portals without credentials.
            </p>
          </div>

          {/* Quick Tab Switcher */}
          <div className="mt-8 flex flex-wrap gap-2 border-b border-line pb-px">
            {[
              { id: "overview", label: "Dashboard Modules", icon: Building },
              { id: "hub", label: "Campus Hub & Directory", icon: Users },
              { id: "free_slots", label: "Free Slots & Rooms", icon: Clock },
              { id: "transport", label: "Transport Service", icon: Bus },
              { id: "sports", label: "Sports Week 2026", icon: Trophy }
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as typeof activeTab)}
                  className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs sm:text-sm font-semibold transition ${
                    isActive
                      ? "bg-brand-600 text-white shadow-xs"
                      : "bg-panel text-muted hover:text-ink hover:bg-surface border border-line"
                  }`}
                >
                  <Icon size={16} />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        {/* ================= SECTION 1: OVERVIEW MODULES ================= */}
        {activeTab === "overview" && (
          <div className="space-y-8">
            <div>
              <h2 className="text-xl font-bold">University Modules</h2>
              <p className="text-xs text-muted mt-1">Select a module to view live schedules, directions, or access your workspace.</p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {/* Student Portal Card */}
              <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-brand-500/80 transition flex flex-col justify-between group">
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-50 text-blue-600 dark:bg-blue-950/60 mb-4 group-hover:scale-105 transition">
                    <GraduationCap size={24} />
                  </div>
                  <h3 className="font-bold text-base text-ink">Student Portal</h3>
                  <p className="mt-1.5 text-xs text-muted leading-relaxed">
                    Attendance progress bar, enrolled courses (Compiler, OS, SE), assignments, lecture hub & quiz marks.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between">
                  <span className="text-xs font-semibold text-brand-600">Enter with Reg No</span>
                  <Link
                    to="/login"
                    className="inline-flex items-center gap-1 text-xs font-bold text-brand-600 hover:underline"
                  >
                    <span>Sign In</span>
                    <ArrowRight size={13} />
                  </Link>
                </div>
              </div>

              {/* Free Slots Card */}
              <div
                onClick={() => setActiveTab("free_slots")}
                className="cursor-pointer rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-brand-500/80 transition flex flex-col justify-between group"
              >
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-50 text-amber-600 dark:bg-amber-950/60 mb-4 group-hover:scale-105 transition">
                    <Clock size={24} />
                  </div>
                  <h3 className="font-bold text-base text-ink">Free Slots Finder</h3>
                  <p className="mt-1.5 text-xs text-muted leading-relaxed">
                    Block-wise available rooms (A Block, C Block, D Block) filtered by day and lecture slot with capacity.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between">
                  <span className="text-xs font-semibold text-amber-600">Public Explorer</span>
                  <span className="inline-flex items-center gap-1 text-xs font-bold text-amber-600">
                    <span>View Slots</span>
                    <ChevronRight size={14} />
                  </span>
                </div>
              </div>

              {/* Timetable Card */}
              <div
                onClick={() => setActiveTab("hub")}
                className="cursor-pointer rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-brand-500/80 transition flex flex-col justify-between group"
              >
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 dark:bg-emerald-950/60 mb-4 group-hover:scale-105 transition">
                    <Calendar size={24} />
                  </div>
                  <h3 className="font-bold text-base text-ink">Timetable Schedule</h3>
                  <p className="mt-1.5 text-xs text-muted leading-relaxed">
                    Weekly student & teacher lecture schedule, lecture slots, teachers, classrooms, and section rosters.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between">
                  <span className="text-xs font-semibold text-emerald-600">Student & Faculty</span>
                  <span className="inline-flex items-center gap-1 text-xs font-bold text-emerald-600">
                    <span>Inspect</span>
                    <ChevronRight size={14} />
                  </span>
                </div>
              </div>

              {/* Campus Hub Card */}
              <div
                onClick={() => setActiveTab("hub")}
                className="cursor-pointer rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-brand-500/80 transition flex flex-col justify-between group"
              >
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-50 text-purple-600 dark:bg-purple-950/60 mb-4 group-hover:scale-105 transition">
                    <Building size={24} />
                  </div>
                  <h3 className="font-bold text-base text-ink">Campus Hub</h3>
                  <p className="mt-1.5 text-xs text-muted leading-relaxed">
                    Directory for classrooms by floor/block, faculty offices, HODs, library, and lab directories.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between">
                  <span className="text-xs font-semibold text-purple-600">Directory</span>
                  <span className="inline-flex items-center gap-1 text-xs font-bold text-purple-600">
                    <span>Explore</span>
                    <ChevronRight size={14} />
                  </span>
                </div>
              </div>

              {/* Transport Service Card */}
              <div
                onClick={() => setActiveTab("transport")}
                className="cursor-pointer rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-brand-500/80 transition flex flex-col justify-between group"
              >
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-50 text-cyan-600 dark:bg-cyan-950/60 mb-4 group-hover:scale-105 transition">
                    <Bus size={24} />
                  </div>
                  <h3 className="font-bold text-base text-ink">Transport Service</h3>
                  <p className="mt-1.5 text-xs text-muted leading-relaxed">
                    Planned bus routes, shuttle arrival times at Farid Town, High Court, and live stop sequences.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between">
                  <span className="text-xs font-semibold text-cyan-600">Live Routes</span>
                  <span className="inline-flex items-center gap-1 text-xs font-bold text-cyan-600">
                    <span>View Bus Info</span>
                    <ChevronRight size={14} />
                  </span>
                </div>
              </div>

              {/* Sports Week Card */}
              <div
                onClick={() => setActiveTab("sports")}
                className="cursor-pointer rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-brand-500/80 transition flex flex-col justify-between group"
              >
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-rose-50 text-rose-600 dark:bg-rose-950/60 mb-4 group-hover:scale-105 transition">
                    <Trophy size={24} />
                  </div>
                  <h3 className="font-bold text-base text-ink">Sports Week 2026</h3>
                  <p className="mt-1.5 text-xs text-muted leading-relaxed">
                    Daily game fixtures, match timings, ground locations (Main Oval, Football Complex, Gym Hall).
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between">
                  <span className="text-xs font-semibold text-rose-600">Day-by-Day</span>
                  <span className="inline-flex items-center gap-1 text-xs font-bold text-rose-600">
                    <span>Fixtures</span>
                    <ChevronRight size={14} />
                  </span>
                </div>
              </div>

              {/* Faculty Portal Card */}
              <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-brand-500/80 transition flex flex-col justify-between group">
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 dark:bg-indigo-950/60 mb-4 group-hover:scale-105 transition">
                    <Lock size={24} />
                  </div>
                  <h3 className="font-bold text-base text-ink">Faculty Workspace</h3>
                  <p className="mt-1.5 text-xs text-muted leading-relaxed">
                    Dedicated instructor portal for lecture timetable, instant class attendance, grading, and room booking.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between">
                  <span className="text-xs font-semibold text-indigo-600">Teacher Login</span>
                  <Link
                    to="/login"
                    className="inline-flex items-center gap-1 text-xs font-bold text-indigo-600 hover:underline"
                  >
                    <span>Faculty Sign In</span>
                    <ArrowRight size={13} />
                  </Link>
                </div>
              </div>

              {/* AI Self Assessment Card */}
              <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-brand-500/80 transition flex flex-col justify-between group">
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-violet-50 text-violet-600 dark:bg-violet-950/60 mb-4 group-hover:scale-105 transition">
                    <Sparkles size={24} />
                  </div>
                  <h3 className="font-bold text-base text-ink">AI Self-Assessment</h3>
                  <p className="mt-1.5 text-xs text-muted leading-relaxed">
                    Adaptive test generation from lecture notes, KaTeX formula solutions, and smart topic mastery profiler.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between">
                  <span className="text-xs font-semibold text-violet-600">Adaptive AI</span>
                  <Link
                    to="/login"
                    className="inline-flex items-center gap-1 text-xs font-bold text-violet-600 hover:underline"
                  >
                    <span>Practice Now</span>
                    <ArrowRight size={13} />
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ================= SECTION 2: CAMPUS HUB & DIRECTORY ================= */}
        {activeTab === "hub" && (
          <div className="space-y-8">
            <div>
              <h2 className="text-xl font-bold">Campus Hub & Directory</h2>
              <p className="text-xs text-muted mt-1">
                Find faculty members, departmental offices, classroom layouts, and research facilities.
              </p>
            </div>

            {/* Search Faculty */}
            <div className="rounded-2xl border border-line bg-panel p-4 shadow-2xs">
              <div className="flex items-center gap-3">
                <Search size={18} className="text-muted" />
                <input
                  type="text"
                  placeholder="Search faculty by name, department, or office (e.g. Dr. Munir, Computer Science, A-301)..."
                  value={facultySearch}
                  onChange={(e) => setFacultySearch(e.target.value)}
                  className="w-full bg-transparent text-sm text-ink placeholder:text-muted focus:outline-hidden"
                />
              </div>
            </div>

            {/* Faculty List Grid */}
            <div>
              <h3 className="text-sm font-bold uppercase tracking-wider text-muted mb-3">Faculty & Office Directory</h3>
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {filteredFaculty.map((f, i) => (
                  <div key={i} className="rounded-xl border border-line bg-panel p-4 shadow-2xs">
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-semibold text-sm text-ink">{f.name}</p>
                        <p className="text-xs text-brand-600 font-medium">{f.role}</p>
                      </div>
                      <span className="rounded-lg bg-surface px-2 py-0.5 text-[11px] font-medium text-muted">
                        {f.department}
                      </span>
                    </div>
                    <div className="mt-3 space-y-1 text-xs text-muted">
                      <p className="flex items-center gap-1.5">
                        <MapPin size={13} className="text-brand-600 shrink-0" />
                        <span>{f.office}</span>
                      </p>
                      <p className="font-mono text-[11px] text-muted">{f.email}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Classrooms Block-wise Directory */}
            <div className="mt-8">
              <h3 className="text-sm font-bold uppercase tracking-wider text-muted mb-3">Classrooms & Laboratories (Block-wise)</h3>
              <div className="grid gap-6 lg:grid-cols-3">
                {CAMPUS_BLOCKS.map((blk) => (
                  <div key={blk.block} className="rounded-2xl border border-line bg-panel p-5 shadow-2xs space-y-4">
                    <div className="border-b border-line pb-3">
                      <span className="inline-block rounded-md bg-brand-500/10 px-2 py-0.5 text-xs font-bold text-brand-600">
                        {blk.block}
                      </span>
                      <h4 className="font-bold text-sm text-ink mt-1">{blk.name}</h4>
                    </div>

                    <div className="space-y-4">
                      {blk.floors.map((flr) => (
                        <div key={flr.floor}>
                          <p className="text-xs font-bold text-muted mb-1.5">{flr.floor}</p>
                          <div className="space-y-1.5">
                            {flr.rooms.map((r) => (
                              <div
                                key={r.room}
                                className="flex items-center justify-between rounded-lg border border-line/60 bg-surface/50 px-2.5 py-1.5 text-xs"
                              >
                                <div>
                                  <span className="font-mono font-semibold text-ink">{r.room}</span>
                                  <span className="text-muted ml-2">{r.type}</span>
                                </div>
                                <span className="text-[11px] text-muted">{r.capacity} seats</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ================= SECTION 3: FREE SLOTS FINDER ================= */}
        {activeTab === "free_slots" && (
          <div className="space-y-8">
            <div>
              <h2 className="text-xl font-bold">Free Slots & Room Availability</h2>
              <p className="text-xs text-muted mt-1">
                Filter available lecture rooms and study halls block-wise for group studies, makeup lectures, or events.
              </p>
            </div>

            {/* Slot Filter Bar */}
            <div className="rounded-2xl border border-line bg-panel p-4 shadow-2xs flex flex-wrap items-center gap-4">
              <div>
                <label className="block text-xs font-semibold text-muted mb-1">Select Day</label>
                <select
                  value={selectedSlotDay}
                  onChange={(e) => setSelectedSlotDay(e.target.value)}
                  className="rounded-xl border border-line bg-surface px-3 py-1.5 text-xs text-ink focus:outline-hidden"
                >
                  {["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].map((d) => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-muted mb-1">Select Lecture Slot</label>
                <select
                  value={selectedSlot}
                  onChange={(e) => setSelectedSlot(e.target.value)}
                  className="rounded-xl border border-line bg-surface px-3 py-1.5 text-xs text-ink focus:outline-hidden"
                >
                  {[
                    "Slot 1 (08:30 - 10:00)",
                    "Slot 2 (10:15 - 11:45)",
                    "Slot 3 (12:00 - 01:30)",
                    "Slot 4 (02:00 - 03:30)",
                    "Slot 5 (03:45 - 05:15)"
                  ].map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
              </div>

              <div className="ml-auto text-xs text-muted self-end py-1.5">
                Showing availability for: <strong className="text-brand-600">{selectedSlotDay}</strong> · {selectedSlot}
              </div>
            </div>

            {/* Available Rooms Block-wise Cards */}
            <div className="grid gap-6 md:grid-cols-3">
              {/* A Block Free Rooms */}
              <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs space-y-3">
                <div className="flex items-center justify-between border-b border-line pb-2.5">
                  <div>
                    <h3 className="font-bold text-ink">A Block</h3>
                    <p className="text-xs text-muted">Engineering & Science</p>
                  </div>
                  <span className="rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-600">
                    3 Rooms Free
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="rounded-xl border border-line/60 bg-surface/50 p-3 flex items-center justify-between">
                    <div>
                      <p className="font-bold text-sm text-ink">Room A-102</p>
                      <p className="text-xs text-muted">1st Floor · Smart Classroom</p>
                    </div>
                    <span className="text-xs font-medium text-emerald-600">Capacity: 60</span>
                  </div>

                  <div className="rounded-xl border border-line/60 bg-surface/50 p-3 flex items-center justify-between">
                    <div>
                      <p className="font-bold text-sm text-ink">Room A-202</p>
                      <p className="text-xs text-muted">2nd Floor · Lecture Hall</p>
                    </div>
                    <span className="text-xs font-medium text-emerald-600">Capacity: 65</span>
                  </div>

                  <div className="rounded-xl border border-line/60 bg-surface/50 p-3 flex items-center justify-between">
                    <div>
                      <p className="font-bold text-sm text-ink">Room A-203</p>
                      <p className="text-xs text-muted">2nd Floor · Seminar Room</p>
                    </div>
                    <span className="text-xs font-medium text-emerald-600">Capacity: 55</span>
                  </div>
                </div>
              </div>

              {/* C Block Free Rooms */}
              <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs space-y-3">
                <div className="flex items-center justify-between border-b border-line pb-2.5">
                  <div>
                    <h3 className="font-bold text-ink">C Block</h3>
                    <p className="text-xs text-muted">Computer Science & IT</p>
                  </div>
                  <span className="rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-600">
                    2 Rooms Free
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="rounded-xl border border-line/60 bg-surface/50 p-3 flex items-center justify-between">
                    <div>
                      <p className="font-bold text-sm text-ink">Room C-102</p>
                      <p className="text-xs text-muted">1st Floor · Standard Classroom</p>
                    </div>
                    <span className="text-xs font-medium text-emerald-600">Capacity: 65</span>
                  </div>

                  <div className="rounded-xl border border-line/60 bg-surface/50 p-3 flex items-center justify-between">
                    <div>
                      <p className="font-bold text-sm text-ink">Room C-201</p>
                      <p className="text-xs text-muted">2nd Floor · Lecture Room</p>
                    </div>
                    <span className="text-xs font-medium text-emerald-600">Capacity: 65</span>
                  </div>
                </div>
              </div>

              {/* D Block Free Rooms */}
              <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs space-y-3">
                <div className="flex items-center justify-between border-b border-line pb-2.5">
                  <div>
                    <h3 className="font-bold text-ink">D Block</h3>
                    <p className="text-xs text-muted">Library & Management</p>
                  </div>
                  <span className="rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-600">
                    2 Rooms Free
                  </span>
                </div>

                <div className="space-y-2">
                  <div className="rounded-xl border border-line/60 bg-surface/50 p-3 flex items-center justify-between">
                    <div>
                      <p className="font-bold text-sm text-ink">Room D-101</p>
                      <p className="text-xs text-muted">1st Floor · Lecture Room</p>
                    </div>
                    <span className="text-xs font-medium text-emerald-600">Capacity: 60</span>
                  </div>

                  <div className="rounded-xl border border-line/60 bg-surface/50 p-3 flex items-center justify-between">
                    <div>
                      <p className="font-bold text-sm text-ink">Library Study Hall B</p>
                      <p className="text-xs text-muted">Ground Floor · Silent Wing</p>
                    </div>
                    <span className="text-xs font-medium text-emerald-600">Capacity: 80</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ================= SECTION 4: TRANSPORT SERVICE ================= */}
        {activeTab === "transport" && (
          <div className="space-y-8">
            <div>
              <h2 className="text-xl font-bold">University Transport Service</h2>
              <p className="text-xs text-muted mt-1">
                Real-time planned routes, shuttle timings, bus numbers, and arrival estimations across Sahiwal stops.
              </p>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
              {BUS_SCHEDULES.map((bus) => (
                <div key={bus.busNo} className="rounded-2xl border border-line bg-panel p-5 shadow-2xs flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between border-b border-line pb-3">
                      <div>
                        <span className="font-mono font-bold text-brand-600 text-sm">{bus.busNo}</span>
                        <h3 className="font-bold text-ink text-sm mt-0.5">{bus.route}</h3>
                      </div>
                      <span className="rounded-md bg-surface px-2 py-1 text-xs font-semibold text-muted">
                        Dep: {bus.departure}
                      </span>
                    </div>

                    <div className="mt-4 space-y-3">
                      <p className="text-xs font-bold text-muted uppercase tracking-wider">Stop Arrival Schedule</p>
                      <div className="space-y-2 relative pl-4 border-l-2 border-brand-500/40">
                        {bus.stops.map((s, idx) => (
                          <div key={idx} className="relative">
                            <span className="absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full bg-brand-600 ring-4 ring-panel" />
                            <div className="flex items-center justify-between text-xs">
                              <span className="font-medium text-ink">{s.stop}</span>
                              <span className="font-mono text-muted">{s.arrivalTime}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="mt-5 pt-3 border-t border-line text-xs text-muted flex items-center justify-between">
                    <span>Terminal: Campus North Bay</span>
                    <span className="text-emerald-600 font-semibold flex items-center gap-1">
                      <CheckCircle2 size={12} /> On Schedule
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ================= SECTION 5: SPORTS WEEK ================= */}
        {activeTab === "sports" && (
          <div className="space-y-8">
            <div>
              <h2 className="text-xl font-bold">Annual Sports Week & Gala 2026</h2>
              <p className="text-xs text-muted mt-1">
                Daily match schedules, venue grounds, and game timing for all departmental competitions.
              </p>
            </div>

            {/* Day Selector Buttons */}
            <div className="flex flex-wrap gap-2">
              {SPORTS_WEEK_EVENTS.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedSportDay(idx)}
                  className={`rounded-xl px-4 py-2 text-xs font-semibold transition ${
                    selectedSportDay === idx
                      ? "bg-brand-600 text-white shadow-xs"
                      : "bg-panel text-muted hover:text-ink border border-line"
                  }`}
                >
                  {item.day}
                </button>
              ))}
            </div>

            {/* Day Fixtures */}
            <div className="rounded-2xl border border-line bg-panel p-6 shadow-2xs">
              <h3 className="font-bold text-base text-ink mb-4">
                Schedule for {SPORTS_WEEK_EVENTS[selectedSportDay]?.day ?? "Day 1"}
              </h3>

              <div className="grid gap-4 md:grid-cols-2">
                {(SPORTS_WEEK_EVENTS[selectedSportDay]?.matches ?? []).map((m, i) => (
                  <div key={i} className="rounded-xl border border-line bg-surface/50 p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-sm text-ink">{m.sport}</span>
                      <span className="rounded-md bg-brand-500/10 px-2 py-0.5 text-xs font-semibold text-brand-600">
                        Official Fixture
                      </span>
                    </div>
                    <div className="space-y-1 text-xs text-muted">
                      <p className="flex items-center gap-1.5">
                        <MapPin size={13} className="text-brand-600 shrink-0" />
                        <span>{m.ground}</span>
                      </p>
                      <p className="flex items-center gap-1.5">
                        <Clock size={13} className="text-brand-600 shrink-0" />
                        <span>{m.time}</span>
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-line bg-panel py-8">
        <div className="mx-auto max-w-7xl px-4 text-center sm:px-6">
          <p className="text-xs text-muted">
            COMSATS University Islamabad · Sahiwal Campus · Smart Education Platform 2026
          </p>
          <div className="mt-2 flex items-center justify-center gap-4 text-xs font-semibold text-brand-600">
            <Link to="/login" className="hover:underline">
              Universal Sign In
            </Link>
            <span>·</span>
            <Link to="/register" className="hover:underline">
              Student Registration
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
