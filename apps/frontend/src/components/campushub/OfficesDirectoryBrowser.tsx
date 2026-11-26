import { useState, useMemo, useEffect } from "react";
import {
  ChevronLeft,
  ChevronRight,
  GraduationCap,
  Briefcase,
  Building2,
  Search,
  MapPin,
  Clock,
  Phone,
  Mail,
  Ticket,
  CheckCircle2,
  X
} from "lucide-react";

import {
  FACULTY_DIRECTORY,
  ADMINISTRATIVE_OFFICES,
  type FacultyProfile,
  type AdministrativeOffice
} from "../../features/campushub/campus-hub-data";

type DirectoryCategory = "faculty" | "admin";

const FACULTY_CARD_ACCENTS = [
  {
    avatar: "bg-primary-soft border-primary/25 text-primary-ink",
    pill: "bg-primary-soft text-primary-ink",
    arrow: "bg-primary-soft text-primary-ink"
  },
  {
    avatar: "bg-secondary-soft border-secondary/25 text-secondary-ink",
    pill: "bg-secondary-soft text-secondary-ink",
    arrow: "bg-secondary-soft text-secondary-ink"
  },
  {
    avatar: "bg-warning-soft border-warning/25 text-warning-ink",
    pill: "bg-warning-soft text-warning-ink",
    arrow: "bg-warning-soft text-warning-ink"
  }
] as const;

const ADMIN_CARD_ACCENTS = [
  {
    outerIconBox: "bg-warning-soft",
    innerIconBox: "bg-warning text-warning-fg",
    miniIconBox: "bg-warning-soft text-warning-ink"
  },
  {
    outerIconBox: "bg-secondary-soft",
    innerIconBox: "bg-secondary text-secondary-fg",
    miniIconBox: "bg-secondary-soft text-secondary-ink"
  },
  {
    outerIconBox: "bg-accent-soft",
    innerIconBox: "bg-accent text-accent-fg",
    miniIconBox: "bg-accent-soft text-accent-ink"
  },
  {
    outerIconBox: "bg-primary-soft",
    innerIconBox: "bg-primary text-on-primary",
    miniIconBox: "bg-primary-soft text-primary-ink"
  }
] as const;

function formatShortBlock(block: string): string {
  const m = block.match(/^Block\s+([A-Z])$/i);
  return m ? `${m[1]!.toUpperCase()} Block` : block;
}

function getSearchableBlockText(block: string, floor: string): string {
  const shortBlock = formatShortBlock(block);
  return `${block} ${shortBlock} ${floor}`.toLowerCase();
}

interface Props {
  onBack?: () => void;
  onShowOnBlueprint?: (blueprintKey: string, roomCode: string) => void;
}

/** Displays Offices Directory selector (Faculty Offices / Administrative Offices) and each directory list matching the mobile UI. */
export function OfficesDirectoryBrowser({ onBack, onShowOnBlueprint }: Props) {
  const [selectedDirectory, setSelectedDirectory] = useState<DirectoryCategory | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [detailFaculty, setDetailFaculty] = useState<FacultyProfile | null>(null);
  const [detailAdmin, setDetailAdmin] = useState<AdministrativeOffice | null>(null);
  const [ticketIssuedForId, setTicketIssuedForId] = useState<string | null>(null);

  useEffect(() => {
    if (!detailFaculty && !detailAdmin) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setDetailFaculty(null);
        setDetailAdmin(null);
        setTicketIssuedForId(null);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [detailFaculty, detailAdmin]);

  const filteredFacultyOffices = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return FACULTY_DIRECTORY;
    return FACULTY_DIRECTORY.filter(
      (f) =>
        f.name.toLowerCase().includes(q) ||
        f.designation.toLowerCase().includes(q) ||
        f.department.toLowerCase().includes(q) ||
        f.officeRoom.toLowerCase().includes(q) ||
        getSearchableBlockText(f.block, f.floor).includes(q)
    );
  }, [searchQuery]);

  const filteredAdminOffices = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return ADMINISTRATIVE_OFFICES;
    return ADMINISTRATIVE_OFFICES.filter(
      (off) =>
        off.name.toLowerCase().includes(q) ||
        off.headOfficer.toLowerCase().includes(q) ||
        off.category.toLowerCase().includes(q) ||
        off.officeRoom.toLowerCase().includes(q) ||
        (off.phone?.toLowerCase().includes(q) ?? false) ||
        getSearchableBlockText(off.block, off.floor).includes(q) ||
        off.servicesOffered.some((s) => s.toLowerCase().includes(q))
    );
  }, [searchQuery]);

  const openDirectory = (dir: DirectoryCategory) => {
    setSelectedDirectory(dir);
    setSearchQuery("");
  };

  // ================= VIEW 1: OFFICES DIRECTORY PICKER =================
  if (!selectedDirectory) {
    return (
      <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
        <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-8 text-hero-fg rounded-b-[2rem] shadow-md">
          <div className="pointer-events-none absolute -top-12 -right-12 h-52 w-52 rounded-full bg-hero-fg/10 blur-xl" />
          <div className="pointer-events-none absolute top-4 right-10 h-28 w-28 rounded-full bg-hero-accent/20 blur-md" />

          {onBack && (
            <div className="relative z-10 mb-5">
              <button
                type="button"
                onClick={onBack}
                aria-label="Back to Campus Portal"
                className="flex h-10 w-10 items-center justify-center rounded-full bg-hero-fg/15 backdrop-blur-md text-hero-fg hover:bg-hero-fg/25 transition cursor-pointer"
              >
                <ChevronLeft size={22} strokeWidth={2.5} />
              </button>
            </div>
          )}

          <div className="relative z-10 space-y-1.5">
            <p className="text-xs font-medium text-hero-muted">Campus Portal</p>
            <h3 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-hero-fg leading-tight">
              Offices Directory
            </h3>
            <span className="inline-flex rounded-full bg-hero-fg/15 border border-hero-fg/20 px-3.5 py-1 text-xs font-semibold text-hero-fg mt-1">
              University Directory
            </span>
          </div>
        </div>

        <div className="p-5 space-y-4">
          <h4 className="text-base font-bold text-ink">Select a Directory</h4>

          <div className="grid grid-cols-2 gap-3.5 sm:gap-4">
            <button
              type="button"
              onClick={() => openDirectory("faculty")}
              aria-label="Faculty Offices"
              className="overflow-hidden rounded-3xl border border-line bg-panel text-left shadow-sm hover:shadow-md hover:border-warning/50 transition flex flex-col cursor-pointer group"
            >
              <div className="bg-warning-soft/55 px-4 py-6 sm:py-7 flex items-center justify-center">
                <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-warning text-warning-fg shadow-sm group-hover:scale-105 transition">
                  <GraduationCap size={26} />
                </span>
              </div>

              <div className="p-4 flex-1 flex flex-col justify-between bg-panel">
                <div>
                  <span className="block font-bold text-sm sm:text-base text-ink leading-snug">
                    Faculty Offices
                  </span>
                  <span className="block text-xs text-muted mt-1 leading-snug">
                    Academic staff &amp; department offices
                  </span>
                </div>

                <span
                  className="mt-3 ml-auto flex h-8 w-8 items-center justify-center rounded-full bg-warning-soft text-warning-ink group-hover:translate-x-0.5 transition"
                  aria-hidden="true"
                >
                  <ChevronRight size={16} />
                </span>
              </div>
            </button>

            <button
              type="button"
              onClick={() => openDirectory("admin")}
              aria-label="Administrative Offices"
              className="overflow-hidden rounded-3xl border border-line bg-panel text-left shadow-sm hover:shadow-md hover:border-secondary/50 transition flex flex-col cursor-pointer group"
            >
              <div className="bg-secondary-soft/55 px-4 py-6 sm:py-7 flex items-center justify-center">
                <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-secondary text-secondary-fg shadow-sm group-hover:scale-105 transition">
                  <Briefcase size={24} />
                </span>
              </div>

              <div className="p-4 flex-1 flex flex-col justify-between bg-panel">
                <div>
                  <span className="block font-bold text-sm sm:text-base text-ink leading-snug">
                    Administrative Offices
                  </span>
                  <span className="block text-xs text-muted mt-1 leading-snug">
                    Admin, accounts &amp; registrar offices
                  </span>
                </div>

                <span
                  className="mt-3 ml-auto flex h-8 w-8 items-center justify-center rounded-full bg-secondary-soft text-secondary-ink group-hover:translate-x-0.5 transition"
                  aria-hidden="true"
                >
                  <ChevronRight size={16} />
                </span>
              </div>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ================= VIEW 2A: ADMINISTRATIVE OFFICES (MATCHING SCREENSHOT) =================
  if (selectedDirectory === "admin") {
    return (
      <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
        {/* Curved Hero Banner */}
        <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-8 text-hero-fg rounded-b-[2rem] shadow-md">
          <div className="pointer-events-none absolute -top-12 -right-12 h-52 w-52 rounded-full bg-hero-fg/10 blur-xl" />
          <div className="pointer-events-none absolute top-4 right-10 h-28 w-28 rounded-full bg-hero-accent/20 blur-md" />

          <div className="relative z-10 mb-5">
            <button
              type="button"
              onClick={() => {
                setSelectedDirectory(null);
                setSearchQuery("");
              }}
              aria-label="Back to Offices Directory"
              className="flex h-10 w-10 items-center justify-center rounded-full bg-hero-fg/15 backdrop-blur-md text-hero-fg hover:bg-hero-fg/25 transition cursor-pointer"
            >
              <ChevronLeft size={22} strokeWidth={2.5} />
            </button>
          </div>

          <div className="relative z-10 space-y-1.5">
            <p className="text-xs font-medium text-hero-muted">Campus Portal</p>
            <h3 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-hero-fg leading-tight">
              Administrative Offices
            </h3>
            <span className="inline-flex rounded-full bg-hero-fg/15 border border-hero-fg/20 px-3.5 py-1 text-xs font-semibold text-hero-fg mt-1">
              University Directory
            </span>
          </div>
        </div>

        {/* Search + Count + Minimal Cards */}
        <div className="p-4 sm:p-5 space-y-4">
          <div className="flex items-center gap-2.5 rounded-2xl border border-line bg-panel px-4 py-2.5 shadow-2xs">
            <Search size={16} className="shrink-0 text-primary-ink" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              aria-label="Search offices, blocks"
              placeholder="Search offices, blocks..."
              className="flex-1 min-w-0 bg-transparent py-0.5 text-sm text-ink placeholder:text-muted focus:outline-hidden"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                aria-label="Clear office search"
                className="rounded-full p-1 text-muted hover:text-ink cursor-pointer"
              >
                <X size={14} />
              </button>
            )}
          </div>

          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-medium text-muted">
              {filteredAdminOffices.length}{" "}
              {filteredAdminOffices.length === 1 ? "office found" : "offices found"}
            </span>
            {searchQuery.trim() && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                className="text-xs font-bold text-primary-ink hover:underline cursor-pointer"
              >
                Reset
              </button>
            )}
          </div>

          {filteredAdminOffices.length === 0 ? (
            <div className="rounded-3xl border border-line bg-panel p-8 text-center space-y-3">
              <p className="text-sm font-bold text-ink">No matching offices found</p>
              <p className="text-xs text-muted">
                Try another office name or block (for example Admission, Exam, A Block).
              </p>
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                className="rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition cursor-pointer"
              >
                Show All Offices
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredAdminOffices.map((off, idx) => {
                const theme = ADMIN_CARD_ACCENTS[idx % ADMIN_CARD_ACCENTS.length]!;
                return (
                  <button
                    key={off.id}
                    type="button"
                    onClick={() => {
                      setDetailAdmin(off);
                      setTicketIssuedForId(null);
                    }}
                    className="w-full rounded-3xl border border-line bg-panel p-3 sm:p-3.5 shadow-2xs hover:shadow-md hover:border-primary/40 transition flex items-center gap-3.5 text-left cursor-pointer group"
                  >
                    {/* Left Building Icon Tile */}
                    <span
                      className={`flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl ${theme.outerIconBox}`}
                    >
                      <span
                        className={`flex h-11 w-11 items-center justify-center rounded-xl shadow-xs ${theme.innerIconBox}`}
                      >
                        <Building2 size={20} />
                      </span>
                    </span>

                    {/* Middle 3-Line Content (Name, Location, Phone ONLY) */}
                    <div className="min-w-0 flex-1 space-y-1.5">
                      <h4 className="font-bold text-sm sm:text-base text-ink leading-snug group-hover:text-primary-ink transition">
                        {off.name}
                      </h4>

                      <div className="flex items-center gap-2 text-xs text-muted">
                        <span
                          className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-lg ${theme.miniIconBox}`}
                        >
                          <MapPin size={12} />
                        </span>
                        <span className="truncate">
                          {formatShortBlock(off.block)} — {off.floor}
                        </span>
                      </div>

                      <div className="flex items-center gap-2 text-xs text-muted">
                        <span
                          className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-lg ${theme.miniIconBox}`}
                        >
                          <Phone size={12} />
                        </span>
                        <span>{off.phone ?? off.phoneExtension}</span>
                      </div>
                    </div>

                    <ChevronRight
                      size={16}
                      className="shrink-0 text-muted group-hover:text-ink group-hover:translate-x-0.5 transition"
                      aria-hidden="true"
                    />
                  </button>
                );
              })}
            </div>
          )}
        </div>

        {/* Administrative Office Details & Queue Modal */}
        {detailAdmin && (
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="office-admin-detail-title"
            onClick={() => {
              setDetailAdmin(null);
              setTicketIssuedForId(null);
            }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-overlay/65 backdrop-blur-xs p-4 animate-in fade-in duration-200"
          >
            <div
              onClick={(e) => e.stopPropagation()}
              className="w-full max-w-md rounded-3xl border border-line bg-panel p-6 shadow-2xl space-y-4 animate-in zoom-in-95 duration-200"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <span className="rounded-md bg-secondary-soft px-2.5 py-0.5 text-[11px] font-bold text-secondary-ink">
                    {detailAdmin.category}
                  </span>
                  <h4 id="office-admin-detail-title" className="font-bold text-base text-ink mt-1.5">
                    {detailAdmin.name}
                  </h4>
                  <p className="text-xs text-muted mt-0.5">
                    In-charge: <strong className="text-ink">{detailAdmin.headOfficer}</strong> ({detailAdmin.headTitle})
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setDetailAdmin(null);
                    setTicketIssuedForId(null);
                  }}
                  aria-label="Close modal"
                  className="rounded-xl p-1.5 text-muted hover:text-ink cursor-pointer"
                >
                  <X size={16} />
                </button>
              </div>

              {ticketIssuedForId === detailAdmin.id ? (
                <div className="rounded-2xl border-2 border-dashed border-secondary/40 bg-surface/80 p-5 text-center space-y-2.5">
                  <span className="text-xs font-extrabold text-muted uppercase tracking-wider">
                    Your Queue Number
                  </span>
                  <div className="font-mono font-black text-4xl text-secondary-ink">
                    #{detailAdmin.currentTicketServing + detailAdmin.queueLength + 1}
                  </div>
                  <p className="text-xs text-muted">
                    Now Serving: <strong className="text-ink">#{detailAdmin.currentTicketServing}</strong>
                  </p>
                  <div className="inline-flex items-center gap-1.5 rounded-xl bg-panel border border-line px-3 py-1.5 text-xs text-secondary-ink font-semibold">
                    <CheckCircle2 size={14} />
                    <span>Estimated wait: ~{detailAdmin.avgWaitMinutes + 4} mins</span>
                  </div>
                </div>
              ) : (
                <>
                  <div className="rounded-2xl border border-line/60 bg-surface/70 p-4 space-y-2.5 text-xs">
                    <div className="flex items-center justify-between gap-2">
                      <span className="flex items-center gap-2 font-semibold text-ink">
                        <MapPin size={14} className="text-secondary-ink shrink-0" />
                        <span>
                          {formatShortBlock(detailAdmin.block)}, {detailAdmin.floor} · {detailAdmin.officeRoom}
                        </span>
                      </span>
                      <span className="font-mono text-[11px] text-muted shrink-0">
                        {detailAdmin.phone ?? detailAdmin.phoneExtension}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-muted pt-1 border-t border-line/50">
                      <Clock size={13} className="text-success-ink shrink-0" />
                      <span>{detailAdmin.workingHours}</span>
                    </div>

                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {detailAdmin.servicesOffered.map((service) => (
                        <span
                          key={service}
                          className="rounded-lg border border-line/60 bg-panel px-2.5 py-1 text-[11px] text-ink"
                        >
                          {service}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center justify-between gap-2">
                    {onShowOnBlueprint ? (
                      <button
                        type="button"
                        onClick={() => {
                          const room = detailAdmin.officeRoom.includes("A-101")
                            ? "Room A-101"
                            : detailAdmin.officeRoom.includes("A-105")
                            ? "Room A-105"
                            : "Room C-204";
                          const key = `${detailAdmin.block} - ${detailAdmin.floor}`;
                          setDetailAdmin(null);
                          onShowOnBlueprint(key, room);
                        }}
                        className="rounded-xl border border-line bg-surface px-3.5 py-2 text-xs font-bold text-ink hover:border-secondary/50 transition cursor-pointer"
                      >
                        View on Floor Map
                      </button>
                    ) : (
                      <span />
                    )}

                    <button
                      type="button"
                      onClick={() => setTicketIssuedForId(detailAdmin.id)}
                      className="inline-flex items-center gap-1.5 rounded-xl bg-secondary px-4 py-2 text-xs font-bold text-secondary-fg hover:opacity-90 transition cursor-pointer"
                    >
                      <Ticket size={14} />
                      <span>Get Queue Number</span>
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    );
  }

  // ================= VIEW 2B: FACULTY OFFICES DIRECTORY =================
  return (
    <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
      <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-6 text-hero-fg rounded-b-[2rem] shadow-md space-y-4">
        <div className="pointer-events-none absolute -top-10 -right-10 h-44 w-44 rounded-full bg-hero-fg/10 blur-xl" />
        <div className="pointer-events-none absolute top-4 right-12 h-24 w-24 rounded-full bg-hero-accent/20 blur-md" />

        <div className="relative z-10 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <button
              type="button"
              onClick={() => {
                setSelectedDirectory(null);
                setSearchQuery("");
              }}
              aria-label="Back to Offices Directory"
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-hero-fg/15 backdrop-blur-md text-hero-fg hover:bg-hero-fg/25 transition cursor-pointer"
            >
              <ChevronLeft size={20} strokeWidth={2.5} />
            </button>

            <div className="min-w-0">
              <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-hero-fg leading-tight">
                Faculty Offices
              </h3>
              <p className="text-xs text-hero-muted mt-0.5">
                Find faculty by name or department
              </p>
            </div>
          </div>

          <span className="shrink-0 rounded-full border border-hero-fg/25 bg-hero-fg/15 px-3.5 py-1.5 text-xs font-semibold text-hero-fg whitespace-nowrap">
            {FACULTY_DIRECTORY.length} Faculty
          </span>
        </div>

        <div className="relative z-10 flex items-center gap-2 rounded-2xl bg-panel border border-line p-1.5 shadow-sm">
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-subtle text-muted">
            <Search size={16} />
          </span>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search by teacher or department"
            placeholder="Search by teacher or department"
            className="flex-1 min-w-0 bg-transparent px-1 py-1.5 text-sm text-ink placeholder:text-muted focus:outline-hidden"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              aria-label="Clear office search"
              className="mr-1 rounded-full p-1 text-muted hover:text-ink cursor-pointer"
            >
              <X size={14} />
            </button>
          )}
        </div>
      </div>

      <div className="px-5 pt-4 pb-3 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="h-4 w-1 rounded-full bg-primary" />
          <span className="text-xs font-extrabold uppercase tracking-wider text-muted">
            DIRECTORY
          </span>
        </div>
        <div className="flex items-center gap-3">
          {searchQuery.trim() && (
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              className="text-xs font-bold text-primary-ink hover:underline cursor-pointer"
            >
              Reset
            </button>
          )}
          <span className="text-xs font-bold text-primary-ink">
            {filteredFacultyOffices.length}{" "}
            {filteredFacultyOffices.length === 1 ? "entry" : "entries"}
          </span>
        </div>
      </div>

      <div className="px-4 pb-6 space-y-3.5">
        {filteredFacultyOffices.length === 0 ? (
          <div className="rounded-3xl border border-line bg-panel p-8 text-center space-y-3">
            <p className="text-sm font-bold text-ink">No matching faculty offices found</p>
            <p className="text-xs text-muted">
              Try another name, department, block, or clear your search.
            </p>
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              className="rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition cursor-pointer"
            >
              Show All
            </button>
          </div>
        ) : (
          filteredFacultyOffices.map((person, index) => {
            const accent = FACULTY_CARD_ACCENTS[index % FACULTY_CARD_ACCENTS.length]!;
            return (
              <button
                key={`fac-off-${person.id}`}
                type="button"
                onClick={() => setDetailFaculty(person)}
                className="w-full rounded-3xl border border-line bg-panel p-4 shadow-2xs hover:shadow-md hover:border-primary/40 transition text-left space-y-3 cursor-pointer group"
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3.5 min-w-0">
                    <span
                      className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full border font-bold text-sm ${accent.avatar}`}
                    >
                      {person.avatarInitials}
                    </span>
                    <div className="min-w-0">
                      <h4 className="font-bold text-sm sm:text-base text-ink leading-snug group-hover:text-primary-ink transition">
                        {person.name}
                      </h4>
                      <span
                        className={`inline-block mt-1 rounded-full px-2.5 py-0.5 text-[11px] font-semibold ${accent.pill}`}
                      >
                        {person.department}
                      </span>
                    </div>
                  </div>

                  <span
                    className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${accent.arrow} group-hover:translate-x-0.5 transition`}
                    aria-hidden="true"
                  >
                    <ChevronRight size={16} />
                  </span>
                </div>

                <div className="border-t border-line/60 pt-2.5 flex items-center gap-2.5">
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-warning-soft text-warning-ink">
                    <MapPin size={15} />
                  </span>
                  <span className="text-xs font-medium text-ink truncate">
                    {formatShortBlock(person.block)} · {person.floor} · {person.officeRoom}
                  </span>
                </div>
              </button>
            );
          })
        )}
      </div>

      {/* Faculty Office Details Modal */}
      {detailFaculty && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="office-faculty-detail-title"
          onClick={() => setDetailFaculty(null)}
          className="fixed inset-0 z-50 flex items-center justify-center bg-overlay/65 backdrop-blur-xs p-4 animate-in fade-in duration-200"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-md rounded-3xl border border-line bg-panel p-6 shadow-2xl space-y-4 animate-in zoom-in-95 duration-200"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-3 min-w-0">
                <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-primary text-on-primary font-extrabold text-sm">
                  {detailFaculty.avatarInitials}
                </span>
                <div className="min-w-0">
                  <span className="rounded-md bg-primary-soft px-2 py-0.5 text-[11px] font-bold text-primary-ink">
                    {detailFaculty.department}
                  </span>
                  <h4 id="office-faculty-detail-title" className="font-bold text-base text-ink mt-1">
                    {detailFaculty.name}
                  </h4>
                  <p className="text-xs text-muted">{detailFaculty.designation}</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setDetailFaculty(null)}
                aria-label="Close modal"
                className="rounded-xl p-1.5 text-muted hover:text-ink cursor-pointer"
              >
                <X size={16} />
              </button>
            </div>

            <div className="rounded-2xl border border-line/60 bg-surface/70 p-4 space-y-2.5 text-xs">
              <div className="flex items-center justify-between gap-2">
                <span className="flex items-center gap-2 font-semibold text-ink">
                  <MapPin size={14} className="text-primary-ink shrink-0" />
                  <span>
                    {formatShortBlock(detailFaculty.block)}, {detailFaculty.floor} · {detailFaculty.officeRoom}
                  </span>
                </span>
                <span className="inline-flex items-center gap-1 font-mono text-[11px] text-muted shrink-0">
                  <Phone size={11} />
                  {detailFaculty.phoneExtension}
                </span>
              </div>

              <div className="flex items-center gap-2 text-muted pt-1.5 border-t border-line/50">
                <Clock size={13} className="text-success-ink shrink-0" />
                <span>
                  Office Hours: <strong className="text-ink">{detailFaculty.consultationHours}</strong>
                </span>
              </div>

              <div className="flex items-center gap-2 text-muted">
                <Mail size={13} className="text-primary-ink shrink-0" />
                <a
                  href={`mailto:${detailFaculty.email}`}
                  className="font-mono text-[11px] text-primary-ink hover:underline truncate"
                >
                  {detailFaculty.email}
                </a>
              </div>
            </div>

            {onShowOnBlueprint && (
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={() => {
                    const room =
                      detailFaculty.officeRoom.match(/Room\s+[A-Z]-\d+/i)?.[0] ||
                      detailFaculty.officeRoom.split("(")[0]?.trim() ||
                      "Room C-204";
                    const key = `${detailFaculty.block} - ${detailFaculty.floor}`;
                    setDetailFaculty(null);
                    onShowOnBlueprint(key, room);
                  }}
                  className="rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition cursor-pointer"
                >
                  View on Floor Map
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
