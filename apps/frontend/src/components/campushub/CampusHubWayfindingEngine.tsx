import { useState } from "react";
import {
  MapPin,
  Users,
  Building,
  BookOpen,
  Compass,
  BarChart3,
  DoorClosed,
  FlaskConical,
  ChevronLeft,
  ChevronRight,
  User
} from "lucide-react";

import {
  CAMPUS_LIBRARY_INFO,
  FLOOR_BLUEPRINTS,
  CAMPUS_STATISTICS
} from "../../features/campushub/campus-hub-data";
import { BlockClassroomsBrowser } from "./BlockClassroomsBrowser";
import { LabsDirectoryBrowser } from "./LabsDirectoryBrowser";
import { FacultyDirectoryBrowser } from "./FacultyDirectoryBrowser";
import { OfficesDirectoryBrowser } from "./OfficesDirectoryBrowser";

export type HubTab =
  | "labs"
  | "classrooms"
  | "faculty"
  | "offices"
  | "library"
  | "statistics"
  | "floorplans";

interface Props {
  initialTab?: HubTab | null;
  activeSection?: HubTab | null;
  onSelectSection?: (section: HubTab | null) => void;
  onBack?: () => void;
}

export function CampusHubWayfindingEngine({
  initialTab = null,
  activeSection,
  onSelectSection,
  onBack
}: Props) {
  const [internalTab, setInternalTab] = useState<HubTab | null>(initialTab);
  const currentSection = activeSection !== undefined ? activeSection : internalTab;

  const setActiveTab = (next: HubTab | null) => {
    if (onSelectSection) {
      onSelectSection(next);
    } else {
      setInternalTab(next);
    }
  };

  // Floor plan wayfinding states
  const [selectedBlueprintKey, setSelectedBlueprintKey] = useState<string>("Block C - 2nd Floor");
  const [highlightedRoomCode, setHighlightedRoomCode] = useState<string | null>("Room C-204");

  // Helper to jump to floor plan and highlight a room
  const locateOnFloorBlueprint = (blueprintKey: string, roomCode: string) => {
    setSelectedBlueprintKey(blueprintKey);
    setHighlightedRoomCode(roomCode);
    setActiveTab("floorplans");
  };

  const activeBlueprint = FLOOR_BLUEPRINTS[selectedBlueprintKey] || FLOOR_BLUEPRINTS["Block C - 2nd Floor"]!;

  const SECTION_META: Record<HubTab, { title: string; subtitle: string }> = {
    classrooms: { title: "Class Rooms", subtitle: "Select a block to view classrooms floor by floor" },
    labs: { title: "Labs Directory", subtitle: "All campus laboratories" },
    faculty: { title: "Faculty & Teachers", subtitle: "Teachers, HODs, Director & Batch Advisors" },
    offices: { title: "Offices Directory", subtitle: "Find teacher and campus office locations" },
    library: { title: "Library System", subtitle: "Live seats, study rooms & books" },
    statistics: { title: "Statistics", subtitle: "Campus numbers & department totals" },
    floorplans: { title: "Floor Blueprints", subtitle: "Interactive building floor map" }
  };

  if (currentSection === null) {
    const HUB_CARDS: Array<{
      id: HubTab;
      label: string;
      icon: typeof DoorClosed;
      iconStyle: string;
    }> = [
      {
        id: "classrooms",
        label: "Class Rooms",
        icon: DoorClosed,
        iconStyle: "bg-warning-soft text-warning-ink"
      },
      {
        id: "labs",
        label: "Labs Directory",
        icon: FlaskConical,
        iconStyle: "bg-secondary-soft text-secondary-ink"
      },
      {
        id: "faculty",
        label: "Faculty & Teachers",
        icon: Users,
        iconStyle: "bg-primary-soft text-primary-ink"
      },
      {
        id: "offices",
        label: "Offices Directory",
        icon: Building,
        iconStyle: "bg-secondary-soft text-secondary-ink"
      },
      {
        id: "library",
        label: "Library System",
        icon: BookOpen,
        iconStyle: "bg-danger-soft text-danger-ink"
      },
      {
        id: "statistics",
        label: "Statistics",
        icon: BarChart3,
        iconStyle: "bg-success-soft text-success-ink"
      }
    ];

    return (
      <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
        {/* Hero Welcome Banner matching Campus Portal screenshot */}
        <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-8 text-hero-fg rounded-b-[2rem] shadow-md">
          <div className="pointer-events-none absolute -top-12 -right-12 h-52 w-52 rounded-full bg-hero-fg/10 blur-xl" />
          <div className="pointer-events-none absolute top-4 right-10 h-28 w-28 rounded-full bg-hero-accent/20 blur-md" />

          <div className="relative z-10 flex items-center justify-between gap-3 mb-5">
            {onBack ? (
              <button
                type="button"
                onClick={onBack}
                aria-label="Back to Main Dashboard"
                className="flex h-10 w-10 items-center justify-center rounded-full bg-hero-fg/15 backdrop-blur-md text-hero-fg hover:bg-hero-fg/25 transition cursor-pointer"
              >
                <ChevronLeft size={22} strokeWidth={2.5} />
              </button>
            ) : (
              <span
                className="flex h-10 w-10 items-center justify-center rounded-full bg-hero-fg/15 backdrop-blur-md text-hero-fg"
                aria-hidden="true"
              >
                <User size={18} />
              </span>
            )}
          </div>

          <div className="relative z-10 space-y-1.5">
            <p className="text-xs font-medium text-hero-muted">Welcome back,</p>
            <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-hero-fg leading-tight">
              Campus Portal
            </h2>
            <span className="inline-flex rounded-full bg-hero-fg/15 border border-hero-fg/20 px-3.5 py-1 text-xs font-semibold text-hero-fg mt-1">
              University Directory
            </span>
          </div>
        </div>

        {/* Quick Access Header */}
        <div className="px-5 pt-5 pb-3 flex items-center justify-between">
          <h3 className="text-base font-bold text-ink">Quick Access</h3>
          <span className="text-xs font-medium text-muted">6 modules</span>
        </div>

        {/* Minimal 6-Card Grid matching screenshot */}
        <div className="px-4 pb-6 grid grid-cols-2 gap-3.5 sm:gap-4">
          {HUB_CARDS.map((card) => {
            const Icon = card.icon;
            return (
              <button
                key={card.id}
                type="button"
                onClick={() => setActiveTab(card.id)}
                className="rounded-3xl border border-line bg-panel p-4 sm:p-5 text-left shadow-2xs hover:shadow-md hover:border-primary/40 transition flex flex-col justify-between min-h-[132px] group cursor-pointer"
              >
                <span
                  className={`flex h-11 w-11 items-center justify-center rounded-2xl ${card.iconStyle} transition group-hover:scale-105`}
                >
                  <Icon size={21} />
                </span>

                <div className="mt-4 flex items-end justify-between gap-2 w-full">
                  <span className="font-bold text-sm text-ink leading-snug">
                    {card.label}
                  </span>
                  <ChevronRight
                    size={16}
                    className="shrink-0 text-muted group-hover:text-ink group-hover:translate-x-0.5 transition mb-0.5"
                    aria-hidden="true"
                  />
                </div>
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Shared Back Bar for sub-pages without their own top hero back button */}
      {currentSection !== "classrooms" &&
        currentSection !== "labs" &&
        currentSection !== "faculty" &&
        currentSection !== "offices" &&
        currentSection !== "library" && (
        <div className="rounded-2xl border border-line bg-panel px-4 py-3 shadow-2xs flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <button
              type="button"
              onClick={() => setActiveTab(null)}
              aria-label="Back to Campus Portal"
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-subtle text-ink hover:bg-primary hover:text-on-primary transition cursor-pointer"
            >
              <ChevronLeft size={20} strokeWidth={2.5} />
            </button>
            <div className="min-w-0">
              <h3 className="font-bold text-base text-ink leading-tight">
                {SECTION_META[currentSection].title}
              </h3>
              <p className="text-xs text-muted truncate">
                {SECTION_META[currentSection].subtitle}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* ================= TAB 1: FACULTY & TEACHERS (QUICK ACCESS -> OFFICE LIST) ================= */}
      {currentSection === "faculty" && (
        <div className="animate-in fade-in duration-200">
          <FacultyDirectoryBrowser
            onBack={() => setActiveTab(null)}
            onShowOnBlueprint={locateOnFloorBlueprint}
          />
        </div>
      )}

      {/* ================= TAB 2: OFFICES DIRECTORY ================= */}
      {currentSection === "offices" && (
        <div className="animate-in fade-in duration-200">
          <OfficesDirectoryBrowser
            onBack={() => setActiveTab(null)}
            onShowOnBlueprint={locateOnFloorBlueprint}
          />
        </div>
      )}

      {/* ================= TAB: LAB DIRECTORY ================= */}
      {currentSection === "labs" && <LabsDirectoryBrowser onBack={() => setActiveTab(null)} />}

      {/* ================= TAB: CAMPUS STATISTICS ================= */}
      {currentSection === "statistics" && (
        <div className="space-y-6 animate-in fade-in duration-200">
          <div>
            <h3 className="text-base font-extrabold text-ink">Campus Statistics &amp; Overview</h3>
            <p className="text-xs text-muted">
              Institutional headcount, academic blocks, laboratories, library capacity, and departmental breakdown.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {CAMPUS_STATISTICS.overview.map((stat) => (
              <div key={stat.label} className="rounded-2xl border border-line bg-panel p-5 shadow-2xs space-y-1">
                <p className="text-xs font-semibold text-muted">{stat.label}</p>
                <p className="font-mono text-2xl font-black text-brand-600">{stat.value}</p>
                <p className="text-2xs text-muted">{stat.sublabel}</p>
              </div>
            ))}
          </div>

          <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs overflow-x-auto">
            <h4 className="font-extrabold text-sm text-ink mb-3">Department-Wise Enrollment &amp; Facilities</h4>
            <table className="w-full min-w-[520px] border-collapse text-xs">
              <thead>
                <tr className="border-b border-line text-left text-2xs uppercase tracking-wider text-muted">
                  <th className="py-2 pr-3 font-bold">Department</th>
                  <th className="px-3 py-2 font-bold">Programs</th>
                  <th className="px-3 py-2 text-right font-bold">Students</th>
                  <th className="px-3 py-2 text-right font-bold">Faculty</th>
                  <th className="pl-3 py-2 text-right font-bold">Labs</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-line/60">
                {CAMPUS_STATISTICS.departments.map((d) => (
                  <tr key={d.department}>
                    <td className="py-2.5 pr-3 font-bold text-ink">{d.department}</td>
                    <td className="px-3 py-2.5 font-mono text-muted">{d.code}</td>
                    <td className="px-3 py-2.5 text-right font-mono font-bold text-ink">{d.students.toLocaleString()}</td>
                    <td className="px-3 py-2.5 text-right font-mono text-ink">{d.faculty}</td>
                    <td className="pl-3 py-2.5 text-right font-mono font-bold text-brand-600">{d.labs}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ================= TAB 3: CLASSROOMS (BLOCK A/B/C -> FLOOR-WISE CLASSROOMS) ================= */}
      {currentSection === "classrooms" && <BlockClassroomsBrowser onBack={() => setActiveTab(null)} />}

      {/* ================= TAB 4: LIBRARY (LOCATION & BLOCK NAME ONLY) ================= */}
      {currentSection === "library" && (
        <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm animate-in fade-in duration-200">
          <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-8 text-hero-fg rounded-b-[2rem] shadow-md">
            <div className="pointer-events-none absolute -top-10 -right-10 h-44 w-44 rounded-full bg-hero-fg/10 blur-xl" />
            <div className="pointer-events-none absolute top-4 right-12 h-24 w-24 rounded-full bg-hero-accent/20 blur-md" />

            <div className="relative z-10 flex items-center gap-3">
              <button
                type="button"
                onClick={() => setActiveTab(null)}
                aria-label="Back to Campus Portal"
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-hero-fg/15 backdrop-blur-md text-hero-fg hover:bg-hero-fg/25 transition cursor-pointer"
              >
                <ChevronLeft size={20} strokeWidth={2.5} />
              </button>

              <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-hero-fg/15 backdrop-blur-md text-hero-fg shadow-xs">
                <BookOpen size={21} />
              </span>

              <div className="min-w-0">
                <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-hero-fg leading-tight">
                  Library System
                </h3>
                <p className="text-xs text-hero-muted mt-0.5">Campus library</p>
              </div>
            </div>
          </div>

          <div className="p-5">
            <div className="rounded-3xl border border-line bg-panel p-5 shadow-2xs space-y-4">
              <div className="flex items-center gap-3.5">
                <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-danger-soft text-danger-ink">
                  <Building size={20} />
                </span>
                <div>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-muted block">
                    Block Name
                  </span>
                  <p className="font-bold text-base text-ink mt-0.5">
                    {CAMPUS_LIBRARY_INFO.blockName}
                  </p>
                </div>
              </div>

              <div className="border-t border-line/60 pt-4 flex items-center gap-3.5">
                <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-primary-soft text-primary-ink">
                  <MapPin size={20} />
                </span>
                <div>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-muted block">
                    Library Location
                  </span>
                  <p className="font-semibold text-sm sm:text-base text-ink mt-0.5">
                    {CAMPUS_LIBRARY_INFO.location}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ================= TAB 5: INTERACTIVE FLOOR PLANS & SPATIAL BLUEPRINTS ================= */}
      {currentSection === "floorplans" && (
        <div className="space-y-6 animate-in fade-in duration-200">
          {/* Blueprint Selector Bar */}
          <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs flex flex-wrap items-center justify-between gap-4">
            <div>
              <label className="block text-xs font-bold text-ink mb-1.5 flex items-center gap-1.5">
                <Compass size={14} className="text-primary-ink" />
                <span>Select Building Sector & Floor Blueprint</span>
              </label>
              <div className="flex flex-wrap gap-2">
                {Object.keys(FLOOR_BLUEPRINTS).map((key) => (
                  <button
                    key={key}
                    onClick={() => {
                      setSelectedBlueprintKey(key);
                      setHighlightedRoomCode(null);
                    }}
                    className={`rounded-xl px-3.5 py-2 text-xs font-bold transition border ${
                      selectedBlueprintKey === key
                        ? "border-primary bg-primary text-on-primary shadow-xs"
                        : "border-line bg-surface text-muted hover:text-ink"
                    }`}
                  >
                    {key}
                  </button>
                ))}
              </div>
            </div>

            <div className="text-right text-xs text-muted hidden sm:block">
              <p className="font-bold text-ink">{activeBlueprint.block}</p>
              <p>{activeBlueprint.floor} Architecture</p>
            </div>
          </div>

          {/* Spatial Blueprint Container */}
          <div className="grid gap-6 lg:grid-cols-[1.5fr_1fr]">
            {/* Left: Vector Graphical Blueprint Matrix */}
            <div className="rounded-3xl border border-line bg-panel p-6 shadow-2xs space-y-5">
              <div className="flex items-center justify-between border-b border-line pb-3">
                <div>
                  <h4 className="font-extrabold text-base text-ink">
                    {activeBlueprint.block} — {activeBlueprint.floor} Layout Blueprint
                  </h4>
                  <p className="text-xs text-muted mt-0.5">{activeBlueprint.corridorDescription}</p>
                </div>
                <span className="rounded-md bg-primary-soft px-2.5 py-1 text-2xs font-bold text-primary-ink">
                  Interactive Wayfinding
                </span>
              </div>

              {/* Floor Plan Blueprint Grid */}
              <div className="rounded-2xl border-2 border-dashed border-line bg-surface/60 p-5 space-y-4">
                <div className="flex items-center justify-between text-2xs font-mono text-muted uppercase tracking-wider">
                  <span>← West Wing</span>
                  <span>Central Academic Corridor</span>
                  <span>East Wing →</span>
                </div>

                <div className="grid grid-cols-3 gap-3">
                  {activeBlueprint.rooms.map((room) => {
                    const isSelected = highlightedRoomCode === room.code;

                    return (
                      <div
                        key={room.code}
                        onClick={() => setHighlightedRoomCode(room.code)}
                        className={`cursor-pointer rounded-2xl border p-4 transition text-center space-y-1 ${room.gridCol} ${
                          isSelected
                            ? "border-primary bg-primary-soft ring-2 ring-primary/50 shadow-md scale-[1.02]"
                            : room.type === "classroom"
                            ? "border-line bg-panel hover:border-primary/60 hover:bg-surface"
                            : room.type === "office"
                            ? "border-secondary/35 bg-secondary-soft/45 hover:border-secondary"
                            : room.type === "lab"
                            ? "border-success/35 bg-success-soft/45 hover:border-success"
                            : "border-line/60 bg-surface/80 opacity-75"
                        }`}
                      >
                        {isSelected && (
                          <span className="inline-flex items-center gap-1 text-[10px] font-extrabold text-primary-ink animate-pulse">
                            📍 YOU ARE LOCATING
                          </span>
                        )}
                        <p className="font-mono font-extrabold text-sm text-ink">{room.code}</p>
                        <p className="text-2xs text-muted line-clamp-1">{room.name}</p>
                        {room.statusText && (
                          <span className="inline-block rounded-md bg-surface border border-line/60 px-2 py-0.5 text-[10px] font-bold text-ink mt-1">
                            {room.statusText}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>

                <div className="flex items-center justify-between text-2xs text-muted pt-2 border-t border-line/40">
                  <span>🚨 Emergency Exits: {activeBlueprint.emergencyExits}</span>
                  <span>Click any room box to show turn-by-turn walking steps</span>
                </div>
              </div>
            </div>

            {/* Right: Turn-by-Turn Wayfinding Guidance */}
            <div className="rounded-3xl border border-line bg-panel p-6 shadow-2xs space-y-5 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="flex items-center gap-2.5">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-soft text-primary-ink">
                    <Compass size={20} />
                  </div>
                  <div>
                    <h4 className="font-extrabold text-sm text-ink">Turn-by-Turn Walking Directions</h4>
                    <p className="text-2xs text-muted">From Campus Main Entrance Gate 1</p>
                  </div>
                </div>

                {highlightedRoomCode ? (
                  <div className="space-y-4">
                    <div className="rounded-2xl border border-primary/40 bg-primary-soft p-4 space-y-1">
                      <span className="text-2xs font-extrabold text-primary-ink uppercase tracking-wider">
                        Destination Target
                      </span>
                      <h4 className="font-extrabold text-base text-ink">{highlightedRoomCode}</h4>
                      <p className="text-xs text-muted">
                        {activeBlueprint.block} · {activeBlueprint.floor}
                      </p>
                    </div>

                    <div className="space-y-3 relative pl-5 border-l-2 border-primary/40 text-xs">
                      <div className="relative">
                        <span className="absolute -left-[25px] top-1 h-3 w-3 rounded-full bg-primary ring-4 ring-panel" />
                        <strong className="text-ink block">Step 1: Arrive at Sector Arch</strong>
                        <p className="text-2xs text-muted mt-0.5">
                          Walk past the Central Fountain towards {activeBlueprint.block} Portico entrance.
                        </p>
                      </div>

                      <div className="relative">
                        <span className="absolute -left-[25px] top-1 h-3 w-3 rounded-full bg-primary ring-4 ring-panel" />
                        <strong className="text-ink block">Step 2: Ascend to {activeBlueprint.floor}</strong>
                        <p className="text-2xs text-muted mt-0.5">
                          Take the West Wing Elevator or Central Fire Staircase to {activeBlueprint.floor}.
                        </p>
                      </div>

                      <div className="relative">
                        <span className="absolute -left-[25px] top-1 h-3 w-3 rounded-full bg-success ring-4 ring-panel" />
                        <strong className="text-success-ink block">
                          Step 3: Arrive at {highlightedRoomCode}
                        </strong>
                        <p className="text-2xs text-muted mt-0.5">
                          Follow the main corridor. Door sign and room tablet display {highlightedRoomCode}.
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="rounded-2xl border border-line bg-surface/60 p-8 text-center space-y-2">
                    <Compass size={24} className="mx-auto text-muted" />
                    <p className="text-xs font-bold text-ink">Select a room from the blueprint</p>
                    <p className="text-2xs text-muted">
                      Click any room on the left vector blueprint to compute pedestrian walking routes and floor elevation.
                    </p>
                  </div>
                )}
              </div>

              <div className="pt-3 border-t border-line/60 text-2xs text-muted flex items-center justify-between">
                <span>Accessibility: ADA Ramps & Elevators</span>
                <span className="text-success-ink font-bold">100% Barrier-Free Access</span>
              </div>
            </div>
          </div>
        </div>
      )}

      </div>
  );
}
