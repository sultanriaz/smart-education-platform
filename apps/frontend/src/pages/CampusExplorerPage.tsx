import { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
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
import { DynamicSpaceFinder } from "../components/facilities/DynamicSpaceFinder";
import { SmartTransitFleetTelemetry } from "../components/transit/SmartTransitFleetTelemetry";
import { CampusHubWayfindingEngine } from "../components/campushub/CampusHubWayfindingEngine";
import { MarqueeEventsPortal } from "../components/events/MarqueeEventsPortal";

export function CampusExplorerPage() {
  const { user, state } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get("tab") as ("overview" | "hub" | "free_slots" | "transport" | "sports") | null;
  const [activeTab, setActiveTab] = useState<"overview" | "hub" | "free_slots" | "transport" | "sports">(() => {
    if (tabParam && ["overview", "hub", "free_slots", "transport", "sports"].includes(tabParam)) {
      return tabParam;
    }
    return "overview";
  });

  useEffect(() => {
    if (tabParam && ["overview", "hub", "free_slots", "transport", "sports"].includes(tabParam)) {
      setActiveTab(tabParam);
    }
  }, [tabParam]);

  const selectTab = (tab: "overview" | "hub" | "free_slots" | "transport" | "sports") => {
    setActiveTab(tab);
    setSearchParams(tab === "overview" ? {} : { tab });
  };
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
              { id: "sports", label: "Campus Life & Marquee Gala", icon: Trophy }
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => selectTab(tab.id as typeof activeTab)}
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
                onClick={() => selectTab("free_slots")}
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
                onClick={() => selectTab("hub")}
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
                onClick={() => selectTab("hub")}
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
                onClick={() => selectTab("transport")}
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
                onClick={() => selectTab("sports")}
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
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold">Campus Hub, Directory & Spatial Wayfinding</h2>
              <p className="text-xs text-muted mt-1">
                Faculty directory, administrative queue tickets, equipped classrooms & labs, library seat telemetry, and interactive vector floor blueprints.
              </p>
            </div>

            <CampusHubWayfindingEngine initialTab="faculty" />
          </div>
        )}

        {/* ================= SECTION 3: FREE SLOTS FINDER ================= */}
        {activeTab === "free_slots" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold">Dynamic Space Finder & Free Slots Navigator</h2>
              <p className="text-xs text-muted mt-1">
                Filter available lecture rooms, labs, and study pods block-wise with equipment telemetry and live availability.
              </p>
            </div>

            <DynamicSpaceFinder mode="public" />
          </div>
        )}

        {/* ================= SECTION 4: TRANSPORT SERVICE ================= */}
        {activeTab === "transport" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold">Smart Transit & Fleet Telemetry</h2>
              <p className="text-xs text-muted mt-1">
                Real-time city route networks (Farid Town Point, Mall Road, Canal Line), intra-day campus shuttles, driver telemetry, and live disruption notices.
              </p>
            </div>

            <SmartTransitFleetTelemetry initialCategory="CITY_ROUTE" />
          </div>
        )}

        {/* ================= SECTION 5: CAMPUS LIFE & MARQUEE GALA ================= */}
        {activeTab === "sports" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold">Campus Life, Marquee Events & Sports Olympiad</h2>
              <p className="text-xs text-muted mt-1">
                Live athletic fixtures, knockout elimination brackets, department trophy standings, plus Fall Hackathon and Winter Career Fair modes.
              </p>
            </div>

            <MarqueeEventsPortal initialMode="SPORTS_GALA" />
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
