import { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  GraduationCap,
  Bus,
  Calendar,
  Clock,
  Compass,
  Sparkles,
  Trophy,
  Users,
  Building,
  ArrowRight,
  Lock,
  ChevronRight
} from "lucide-react";
import { useAuth } from "../features/auth/useAuth";
import { primaryRole } from "../features/auth/permissions";
import { FreeSlotsNavigator } from "../components/facilities/FreeSlotsNavigator";
import { SmartTransitFleetTelemetry } from "../components/transit/SmartTransitFleetTelemetry";
import { CampusHubWayfindingEngine } from "../components/campushub/CampusHubWayfindingEngine";
import { MarqueeEventsPortal } from "../components/events/MarqueeEventsPortal";
import { TimetableHub } from "../components/timetable/TimetableHub";

type ExplorerTab = "overview" | "hub" | "free_slots" | "timetable" | "transport" | "sports";
const VALID_TABS: ExplorerTab[] = ["overview", "hub", "free_slots", "timetable", "transport", "sports"];

export function CampusExplorerPage() {
  const { user, state } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get("tab") as ExplorerTab | null;
  const [activeTab, setActiveTab] = useState<ExplorerTab>(() => {
    if (tabParam && VALID_TABS.includes(tabParam)) {
      return tabParam;
    }
    return "overview";
  });

  useEffect(() => {
    if (tabParam && VALID_TABS.includes(tabParam)) {
      setActiveTab(tabParam);
    }
  }, [tabParam]);

  const selectTab = (tab: ExplorerTab) => {
    setActiveTab(tab);
    setSearchParams(tab === "overview" ? {} : { tab });
  };

  const role = user ? primaryRole(user.roles) : null;

  if (activeTab === "free_slots") {
    return <FreeSlotsNavigator onBack={() => selectTab("overview")} />;
  }

  return (
    <div className="min-h-screen bg-background text-ink transition">
      {/* Top Universal Header */}
      <header className="sticky top-0 z-40 border-b border-line bg-panel/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
          <div className="flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-on-primary shadow-xs">
              <GraduationCap size={22} />
            </span>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold tracking-tight text-base sm:text-lg">COMSATS SmartEdu</span>
                <span className="rounded-full bg-secondary-soft px-2 py-0.5 text-[11px] font-semibold text-secondary-ink">
                  Open Campus
                </span>
              </div>
              <p className="hidden text-xs text-muted sm:block">Sahiwal Campus · Academic &amp; Facilities Portal</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {state === "authenticated" && user ? (
              <Link
                to={role ? `/app/${role}` : "/app"}
                className="inline-flex items-center gap-2 rounded-xl bg-primary px-3.5 py-2 text-xs sm:text-sm font-semibold text-on-primary shadow-xs hover:bg-primary-hover transition"
              >
                <span>Workspace ({role})</span>
                <ArrowRight size={14} />
              </Link>
            ) : (
              <Link
                to="/login"
                className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-xs sm:text-sm font-semibold text-on-primary shadow-xs hover:bg-primary-hover transition"
              >
                <span>Universal Sign In</span>
                <ArrowRight size={14} />
              </Link>
            )}
          </div>
        </div>
      </header>

      {/* Hero Welcome Banner */}
      <div className="border-b border-line bg-subtle/40">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 sm:py-12">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary-soft px-3 py-1 text-xs font-semibold text-primary-ink mb-3">
              <Compass size={14} />
              <span>Universal Adaptive Campus Gateway</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-ink">
              One Connected Campus.<br />
              <span className="text-primary-ink">Every resource at your fingertips.</span>
            </h1>
            <p className="mt-3 text-sm sm:text-base text-muted leading-relaxed">
              Explore public transit shuttle schedules, free study rooms across blocks, university directory, sports week fixtures, and curriculum portals without credentials.
            </p>
          </div>

          {/* Quick Tab Switcher */}
          <div className="mt-8 flex flex-wrap gap-2 border-b border-line pb-px">
            {[
              { id: "overview", label: "Main Dashboard", icon: Building },
              { id: "free_slots", label: "Free Slots", icon: Clock },
              { id: "timetable", label: "Timetable", icon: Calendar },
              { id: "hub", label: "Campus Hub", icon: Users },
              { id: "transport", label: "Transport Service", icon: Bus },
              { id: "sports", label: "Sports Week", icon: Trophy }
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => selectTab(tab.id as ExplorerTab)}
                  className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs sm:text-sm font-semibold transition ${
                    isActive
                      ? "bg-primary text-on-primary shadow-xs"
                      : "bg-panel text-muted hover:text-ink hover:bg-subtle/60 border border-line"
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
        {/* ================= SECTION 1: MAIN DASHBOARD MODULES ================= */}
        {activeTab === "overview" && (
          <div className="space-y-8">
            <div>
              <h2 className="text-xl font-bold text-ink">Main Dashboard</h2>
              <p className="text-xs text-muted mt-1">Select any module card below to open its screen.</p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {/* 1. Student Portal */}
              <Link
                to={state === "authenticated" && role === "student" ? "/app/student" : "/login/student"}
                className="rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-primary transition flex flex-col justify-between group"
              >
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-soft text-primary-ink mb-4 group-hover:scale-105 transition">
                    <GraduationCap size={24} />
                  </div>
                  <h3 className="font-bold text-base text-ink">Student Portal</h3>
                  <p className="mt-1.5 text-xs text-muted leading-relaxed">
                    Sign in with Department &amp; Reg No to view subjects, attendance bars, assignments, quizzes, marks &amp; resources.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between">
                  <span className="text-xs font-semibold text-primary-ink">Student Login</span>
                  <span className="inline-flex items-center gap-1 text-xs font-bold text-primary-ink">
                    <span>Open</span>
                    <ArrowRight size={13} />
                  </span>
                </div>
              </Link>

              {/* 2. Free Slots */}
              <button
                type="button"
                onClick={() => selectTab("free_slots")}
                className="text-left cursor-pointer rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-accent transition flex flex-col justify-between group"
              >
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent-soft text-accent-ink mb-4 group-hover:scale-105 transition">
                    <Clock size={24} />
                  </div>
                  <h3 className="font-bold text-base text-ink">Free Slots</h3>
                  <p className="mt-1.5 text-xs text-muted leading-relaxed">
                    Free slots for the week filtered by day and lecture slot, grouped block-wise with student capacity.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between w-full">
                  <span className="text-xs font-semibold text-accent-ink">Block-Wise Rooms</span>
                  <span className="inline-flex items-center gap-1 text-xs font-bold text-accent-ink">
                    <span>View Slots</span>
                    <ChevronRight size={14} />
                  </span>
                </div>
              </button>

              {/* 3. Timetable */}
              <button
                type="button"
                onClick={() => selectTab("timetable")}
                className="text-left cursor-pointer rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-secondary transition flex flex-col justify-between group"
              >
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-secondary-soft text-secondary-ink mb-4 group-hover:scale-105 transition">
                    <Calendar size={24} />
                  </div>
                  <h3 className="font-bold text-base text-ink">Timetable</h3>
                  <p className="mt-1.5 text-xs text-muted leading-relaxed">
                    Student &amp; Teacher weekly timetables with lecture counts per day, slots, subjects, classrooms &amp; sections.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between w-full">
                  <span className="text-xs font-semibold text-secondary-ink">Student &amp; Teacher</span>
                  <span className="inline-flex items-center gap-1 text-xs font-bold text-secondary-ink">
                    <span>Inspect</span>
                    <ChevronRight size={14} />
                  </span>
                </div>
              </button>

              {/* 4. Campus Hub */}
              <button
                type="button"
                onClick={() => selectTab("hub")}
                className="text-left cursor-pointer rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-primary transition flex flex-col justify-between group"
              >
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-soft text-primary-ink mb-4 group-hover:scale-105 transition">
                    <Building size={24} />
                  </div>
                  <h3 className="font-bold text-base text-ink">Campus Hub</h3>
                  <p className="mt-1.5 text-xs text-muted leading-relaxed">
                    Lab Directory, Classrooms, Faculty &amp; Teachers, Office Directory, Library, and Campus Statistics.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between w-full">
                  <span className="text-xs font-semibold text-primary-ink">6 Directories</span>
                  <span className="inline-flex items-center gap-1 text-xs font-bold text-primary-ink">
                    <span>Explore</span>
                    <ChevronRight size={14} />
                  </span>
                </div>
              </button>

              {/* 5. Transport Service */}
              <button
                type="button"
                onClick={() => selectTab("transport")}
                className="text-left cursor-pointer rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-secondary transition flex flex-col justify-between group"
              >
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-secondary-soft text-secondary-ink mb-4 group-hover:scale-105 transition">
                    <Bus size={24} />
                  </div>
                  <h3 className="font-bold text-base text-ink">Transport Service</h3>
                  <p className="mt-1.5 text-xs text-muted leading-relaxed">
                    Planned Routes and Shuttle Schedule with bus numbers, locations, and complete stop arrival times.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between w-full">
                  <span className="text-xs font-semibold text-secondary-ink">Routes &amp; Shuttles</span>
                  <span className="inline-flex items-center gap-1 text-xs font-bold text-secondary-ink">
                    <span>View Bus Info</span>
                    <ChevronRight size={14} />
                  </span>
                </div>
              </button>

              {/* 6. Faculty */}
              <Link
                to={state === "authenticated" && role === "teacher" ? "/app/teacher" : "/login/faculty"}
                className="rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-primary transition flex flex-col justify-between group"
              >
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-subtle text-ink border border-line mb-4 group-hover:scale-105 transition">
                    <Lock size={24} />
                  </div>
                  <h3 className="font-bold text-base text-ink">Faculty</h3>
                  <p className="mt-1.5 text-xs text-muted leading-relaxed">
                    Dedicated teacher-only login for faculty schedules, attendance marking, grading, and room reservations.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between">
                  <span className="text-xs font-semibold text-primary-ink">Teachers Only</span>
                  <span className="inline-flex items-center gap-1 text-xs font-bold text-primary-ink">
                    <span>Faculty Sign In</span>
                    <ArrowRight size={13} />
                  </span>
                </div>
              </Link>

              {/* 7. Sports Week */}
              <button
                type="button"
                onClick={() => selectTab("sports")}
                className="text-left cursor-pointer rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-accent transition flex flex-col justify-between group"
              >
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent-soft text-accent-ink mb-4 group-hover:scale-105 transition">
                    <Trophy size={24} />
                  </div>
                  <h3 className="font-bold text-base text-ink">Sports Week</h3>
                  <p className="mt-1.5 text-xs text-muted leading-relaxed">
                    Day-by-day game schedules with ground locations, match timings, scoreboards, and top day selector.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between w-full">
                  <span className="text-xs font-semibold text-accent-ink">Day-by-Day</span>
                  <span className="inline-flex items-center gap-1 text-xs font-bold text-accent-ink">
                    <span>Fixtures</span>
                    <ChevronRight size={14} />
                  </span>
                </div>
              </button>

              {/* 8. Self Assessment */}
              <Link
                to="/app/student/learning"
                className="rounded-2xl border border-line bg-panel p-5 shadow-2xs hover:border-secondary transition flex flex-col justify-between group"
              >
                <div>
                  <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-secondary-soft text-secondary-ink mb-4 group-hover:scale-105 transition">
                    <Sparkles size={24} />
                  </div>
                  <h3 className="font-bold text-base text-ink">Self Assessment</h3>
                  <p className="mt-1.5 text-xs text-muted leading-relaxed">
                    AI practice test generator from uploaded study notes, KaTeX numerical proofs, and topic mastery radar.
                  </p>
                </div>
                <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between">
                  <span className="text-xs font-semibold text-secondary-ink">Adaptive AI</span>
                  <span className="inline-flex items-center gap-1 text-xs font-bold text-secondary-ink">
                    <span>Practice Now</span>
                    <ArrowRight size={13} />
                  </span>
                </div>
              </Link>
            </div>
          </div>
        )}

        {/* ================= SECTION: TIMETABLE ================= */}
        {activeTab === "timetable" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-ink">Timetable</h2>
              <p className="text-xs text-muted mt-1">
                Choose Student or Teacher to inspect the full weekly schedule with lecture counts, slots, classrooms, and sections.
              </p>
            </div>

            <TimetableHub />
          </div>
        )}

        {/* ================= SECTION 2: CAMPUS HUB & DIRECTORY ================= */}
        {activeTab === "hub" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-ink">Campus Hub, Directory &amp; Spatial Wayfinding</h2>
              <p className="text-xs text-muted mt-1">
                Faculty directory, administrative queue tickets, equipped classrooms &amp; labs, library seat telemetry, and interactive vector floor blueprints.
              </p>
            </div>

            <CampusHubWayfindingEngine initialTab="faculty" />
          </div>
        )}


        {/* ================= SECTION 4: TRANSPORT SERVICE ================= */}
        {activeTab === "transport" && (
          <div className="space-y-6">
            <div>
              <h2 className="text-xl font-bold text-ink">Smart Transit &amp; Fleet Telemetry</h2>
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
              <h2 className="text-xl font-bold text-ink">Campus Life, Marquee Events &amp; Sports Olympiad</h2>
              <p className="text-xs text-muted mt-1">
                Live athletic fixtures, knockout elimination brackets, department trophy standings, plus Fall Hackathon and Winter Career Fair modes.
              </p>
            </div>

            <MarqueeEventsPortal initialMode="SPORTS_GALA" />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-line bg-panel pt-8 pb-24 sm:pb-10">
        <div className="mx-auto max-w-7xl px-4 text-center sm:px-6">
          <p className="text-xs text-muted">
            COMSATS University Islamabad · Sahiwal Campus · Smart Education Platform 2026
          </p>
          <div className="mt-2 flex items-center justify-center gap-4 text-xs font-semibold text-primary-ink">
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
