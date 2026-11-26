import { useState, useEffect, useRef } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  GraduationCap,
  Bus,
  Calendar,
  Clock,
  Trophy,
  Users,
  Building,
  ArrowRight,
  ChevronRight
} from "lucide-react";
import { useAuth } from "../features/auth/useAuth";
import { primaryRole } from "../features/auth/permissions";
import { FreeSlotsNavigator } from "../components/facilities/FreeSlotsNavigator";
import { SmartTransitFleetTelemetry } from "../components/transit/SmartTransitFleetTelemetry";
import { CampusHubWayfindingEngine, type HubTab } from "../components/campushub/CampusHubWayfindingEngine";
import { MarqueeEventsPortal } from "../components/events/MarqueeEventsPortal";
import { TimetableHub } from "../components/timetable/TimetableHub";

type ExplorerTab = "overview" | "hub" | "free_slots" | "timetable" | "transport" | "sports";
const VALID_TABS: ExplorerTab[] = ["overview", "hub", "free_slots", "timetable", "transport", "sports"];
const VALID_HUB_SECTIONS: HubTab[] = [
  "classrooms",
  "labs",
  "faculty",
  "offices",
  "library",
  "statistics",
  "floorplans"
];

const EXPLORER_TABS: Array<{ id: ExplorerTab; label: string; icon: typeof Building }> = [
  { id: "overview", label: "Main Dashboard", icon: Building },
  { id: "free_slots", label: "Free Slots", icon: Clock },
  { id: "timetable", label: "Timetable", icon: Calendar },
  { id: "hub", label: "Campus Hub", icon: Users },
  { id: "transport", label: "Transport Service", icon: Bus },
  { id: "sports", label: "Sports Week", icon: Trophy }
];

export function CampusExplorerPage() {
  const { user, state } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const tabParam = searchParams.get("tab") as ExplorerTab | null;
  const sectionParam = searchParams.get("section") as HubTab | null;
  const activeHubSection =
    sectionParam && VALID_HUB_SECTIONS.includes(sectionParam) ? sectionParam : null;
  const [activeTab, setActiveTab] = useState<ExplorerTab>(() => {
    if (tabParam && VALID_TABS.includes(tabParam)) {
      return tabParam;
    }
    return "overview";
  });

  const subNavRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (tabParam && VALID_TABS.includes(tabParam)) {
      setActiveTab(tabParam);
    } else if (!tabParam) {
      setActiveTab("overview");
    }
  }, [tabParam]);

  useEffect(() => {
    if (activeTab === "overview") return;
    const container = subNavRef.current;
    const activeBtn = container?.querySelector<HTMLButtonElement>("[data-active='true']");
    if (container && activeBtn) {
      container.scrollLeft = Math.max(
        0,
        activeBtn.offsetLeft - container.clientWidth / 2 + activeBtn.clientWidth / 2
      );
    }
  }, [activeTab]);

  const selectTab = (tab: ExplorerTab, section?: HubTab) => {
    setActiveTab(tab);
    if (tab === "overview") {
      setSearchParams({});
    } else if (tab === "hub" && section) {
      setSearchParams({ tab, section });
    } else {
      setSearchParams({ tab });
    }
  };

  const role = user ? primaryRole(user.roles) : null;

  if (activeTab === "free_slots") {
    return <FreeSlotsNavigator onBack={() => selectTab("overview")} />;
  }

  return (
    <div className="min-h-screen bg-background text-ink transition">
      {/* Top Header */}
      <header className="sticky top-0 z-40 border-b border-line bg-panel/95 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-2.5 sm:px-6">
          <button
            type="button"
            onClick={() => selectTab("overview")}
            className="flex items-center gap-2.5 text-left min-w-0 cursor-pointer"
          >
            <span className="flex h-9 w-9 sm:h-10 sm:w-10 shrink-0 items-center justify-center rounded-xl bg-primary text-on-primary shadow-xs">
              <GraduationCap size={20} />
            </span>
            <div className="min-w-0">
              <span className="font-bold tracking-tight text-sm sm:text-lg whitespace-nowrap block">
                COMSATS SmartEdu
              </span>
              <p className="hidden text-xs text-muted sm:block">Sahiwal Campus</p>
            </div>
          </button>

          <div className="flex items-center gap-2 shrink-0">
            {state === "authenticated" && user ? (
              <Link
                to={role ? `/app/${role}` : "/app"}
                className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-3.5 py-2 text-xs sm:text-sm font-semibold text-on-primary shadow-xs hover:bg-primary-hover transition whitespace-nowrap"
              >
                <span>My Dashboard</span>
                <ArrowRight size={14} />
              </Link>
            ) : (
              <Link
                to="/login"
                className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-3.5 py-2 text-xs sm:text-sm font-semibold text-on-primary shadow-xs hover:bg-primary-hover transition whitespace-nowrap"
              >
                <span>Sign In</span>
                <ArrowRight size={14} />
              </Link>
            )}
          </div>
        </div>

        {/* Compact single-row tab bar when viewing a sub-module directly */}
        {activeTab !== "overview" && (
          <nav aria-label="Campus sections" className="border-t border-line/70 bg-subtle/40">
            <div
              ref={subNavRef}
              className="mx-auto flex max-w-7xl items-center gap-2 overflow-x-auto px-4 py-2 sm:px-6"
            >
              {EXPLORER_TABS.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    type="button"
                    data-active={isActive ? "true" : "false"}
                    onClick={() => selectTab(tab.id)}
                    className={`inline-flex shrink-0 items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-semibold transition whitespace-nowrap cursor-pointer ${
                      isActive
                        ? "bg-primary text-on-primary shadow-2xs"
                        : "bg-panel text-muted hover:text-ink border border-line"
                    }`}
                  >
                    <Icon size={14} />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>
          </nav>
        )}
      </header>

      {/* Main Content Area */}
      <main className="mx-auto max-w-7xl px-4 py-5 sm:py-6 sm:px-6">
        {/* ================= SECTION 1: MAIN DASHBOARD (MATCHING WELCOME SCREENSHOT) ================= */}
        {activeTab === "overview" && (
          <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
            {/* Curved Welcome Banner */}
            <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-8 text-hero-fg rounded-b-[2rem] shadow-md space-y-5">
              <div className="pointer-events-none absolute -top-12 -right-12 h-52 w-52 rounded-full bg-hero-fg/10 blur-xl" />
              <div className="pointer-events-none absolute top-4 right-10 h-28 w-28 rounded-full bg-hero-accent/20 blur-md" />

              <div className="relative z-10 flex items-center justify-between gap-4">
                <div>
                  <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-hero-fg leading-tight">
                    Welcome!
                  </h1>
                  <p className="mt-1 text-xs sm:text-sm text-hero-muted">
                    COMSATS University Islamabad
                  </p>
                </div>

                <span
                  className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-secondary text-secondary-fg shadow-sm border border-hero-fg/20"
                  aria-hidden="true"
                >
                  <GraduationCap size={26} />
                </span>
              </div>

              {/* Featured Student Portal Card */}
              <Link
                to={state === "authenticated" && role === "student" ? "/app/student" : "/login/student"}
                className="relative z-10 flex items-center justify-between gap-3 rounded-2xl bg-panel p-4 shadow-sm hover:shadow-md transition group"
              >
                <div className="flex items-center gap-3.5 min-w-0">
                  <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-primary-soft text-primary-ink group-hover:scale-105 transition">
                    <GraduationCap size={22} />
                  </span>
                  <div className="min-w-0">
                    <span className="block font-bold text-sm sm:text-base text-ink leading-snug">
                      Student Portal
                    </span>
                    <span className="block text-xs text-muted mt-0.5 truncate">
                      Access your academic profile
                    </span>
                  </div>
                </div>

                <span
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-subtle text-muted group-hover:text-ink group-hover:translate-x-0.5 transition"
                  aria-hidden="true"
                >
                  <ChevronRight size={16} />
                </span>
              </Link>
            </div>

            {/* Quick Access Header */}
            <div className="px-5 pt-5 pb-3 flex items-center gap-2">
              <span className="h-4 w-1 rounded-full bg-primary" />
              <span className="text-xs font-extrabold uppercase tracking-wider text-muted">
                QUICK ACCESS
              </span>
            </div>

            {/* Minimal Module Grid matching screenshot */}
            <div className="px-4 pb-6 grid grid-cols-2 gap-3.5 sm:gap-4">
              {/* 1. Student Portal */}
              <Link
                to={state === "authenticated" && role === "student" ? "/app/student" : "/login/student"}
                className="rounded-3xl border border-line bg-panel p-4 sm:p-5 text-left shadow-2xs hover:shadow-md hover:border-primary/40 transition flex flex-col justify-between min-h-[126px] group"
              >
                <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-secondary-soft text-secondary-ink group-hover:scale-105 transition">
                  <GraduationCap size={20} />
                </span>
                <div className="mt-4">
                  <span className="block font-bold text-sm text-ink leading-snug">Student Portal</span>
                  <span className="block text-xs text-muted mt-0.5">Grades &amp; results</span>
                </div>
              </Link>

              {/* 2. Time Table */}
              <button
                type="button"
                onClick={() => selectTab("timetable")}
                className="rounded-3xl border border-line bg-panel p-4 sm:p-5 text-left shadow-2xs hover:shadow-md hover:border-primary/40 transition flex flex-col justify-between min-h-[126px] group cursor-pointer"
              >
                <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary-soft text-primary-ink group-hover:scale-105 transition">
                  <Calendar size={20} />
                </span>
                <div className="mt-4">
                  <span className="block font-bold text-sm text-ink leading-snug">Time Table</span>
                  <span className="block text-xs text-muted mt-0.5">Weekly schedule</span>
                </div>
              </button>

              {/* 3. Teachers */}
              <button
                type="button"
                onClick={() => selectTab("hub", "faculty")}
                className="rounded-3xl border border-line bg-panel p-4 sm:p-5 text-left shadow-2xs hover:shadow-md hover:border-primary/40 transition flex flex-col justify-between min-h-[126px] group cursor-pointer"
              >
                <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-warning-soft text-warning-ink group-hover:scale-105 transition">
                  <Users size={20} />
                </span>
                <div className="mt-4">
                  <span className="block font-bold text-sm text-ink leading-snug">Teachers</span>
                  <span className="block text-xs text-muted mt-0.5">Faculty directory</span>
                </div>
              </button>

              {/* 4. Free Slots */}
              <button
                type="button"
                onClick={() => selectTab("free_slots")}
                className="rounded-3xl border border-line bg-panel p-4 sm:p-5 text-left shadow-2xs hover:shadow-md hover:border-primary/40 transition flex flex-col justify-between min-h-[126px] group cursor-pointer"
              >
                <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-danger-soft text-danger-ink group-hover:scale-105 transition">
                  <Clock size={20} />
                </span>
                <div className="mt-4">
                  <span className="block font-bold text-sm text-ink leading-snug">Free Slots</span>
                  <span className="block text-xs text-muted mt-0.5">Available rooms</span>
                </div>
              </button>

              {/* 5. Campus Hub */}
              <button
                type="button"
                onClick={() => selectTab("hub")}
                className="rounded-3xl border border-line bg-panel p-4 sm:p-5 text-left shadow-2xs hover:shadow-md hover:border-primary/40 transition flex flex-col justify-between min-h-[126px] group cursor-pointer"
              >
                <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-accent-soft text-accent-ink group-hover:scale-105 transition">
                  <Building size={20} />
                </span>
                <div className="mt-4">
                  <span className="block font-bold text-sm text-ink leading-snug">Campus Hub</span>
                  <span className="block text-xs text-muted mt-0.5">Explore campus</span>
                </div>
              </button>

              {/* 6. Transport Service */}
              <button
                type="button"
                onClick={() => selectTab("transport")}
                className="rounded-3xl border border-line bg-panel p-4 sm:p-5 text-left shadow-2xs hover:shadow-md hover:border-primary/40 transition flex flex-col justify-between min-h-[126px] group cursor-pointer"
              >
                <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-secondary-soft text-secondary-ink group-hover:scale-105 transition">
                  <Bus size={20} />
                </span>
                <div className="mt-4">
                  <span className="block font-bold text-sm text-ink leading-snug">Transport Service</span>
                  <span className="block text-xs text-muted mt-0.5">Schedule</span>
                </div>
              </button>

              {/* 7. Sports Week (centered bottom card) */}
              <div className="col-span-2 flex justify-center">
                <button
                  type="button"
                  onClick={() => selectTab("sports")}
                  className="w-full max-w-[calc(50%-0.5rem)] rounded-3xl border border-line bg-panel p-4 sm:p-5 text-left shadow-2xs hover:shadow-md hover:border-primary/40 transition flex flex-col justify-between min-h-[126px] group cursor-pointer"
                >
                  <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-warning-soft text-warning-ink group-hover:scale-105 transition">
                    <Trophy size={20} />
                  </span>
                  <div className="mt-4">
                    <span className="block font-bold text-sm text-ink leading-snug">Sports Week</span>
                    <span className="block text-xs text-muted mt-0.5">Schedule</span>
                  </div>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ================= SECTION: TIMETABLE ================= */}
        {activeTab === "timetable" && (
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-bold text-ink">Timetable</h2>
              <p className="text-xs text-muted mt-1">
                Pick Student or Teacher to see weekly classes, lecture times, classrooms, and open seats.
              </p>
            </div>

            <TimetableHub
              signedInRole={role === "student" || role === "teacher" ? role : null}
            />
          </div>
        )}

        {/* ================= SECTION 2: CAMPUS HUB & DIRECTORY ================= */}
        {activeTab === "hub" && (
          <CampusHubWayfindingEngine
            activeSection={activeHubSection}
            onSelectSection={(sec) =>
              setSearchParams(sec ? { tab: "hub", section: sec } : { tab: "hub" })
            }
            onBack={() => selectTab("overview")}
          />
        )}

        {/* ================= SECTION 4: TRANSPORT SERVICE ================= */}
        {activeTab === "transport" && (
          <SmartTransitFleetTelemetry onBack={() => selectTab("overview")} />
        )}

        {/* ================= SECTION 5: SPORTS WEEK ================= */}
        {activeTab === "sports" && (
          <MarqueeEventsPortal onBack={() => selectTab("overview")} />
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
              Sign In
            </Link>
            <span>·</span>
            <Link to="/register" className="hover:underline">
              Create Student Account
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
