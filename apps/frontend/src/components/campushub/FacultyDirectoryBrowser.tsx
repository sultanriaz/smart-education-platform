import { useState, useMemo, useEffect } from "react";
import {
  ChevronLeft,
  ChevronRight,
  Landmark,
  GraduationCap,
  Users,
  Headset,
  Search,
  MapPin,
  Clock,
  Mail,
  Calendar,
  CheckCircle2,
  X,
  Phone,
  TrendingUp,
  Award
} from "lucide-react";

import {
  CAMPUS_TOTAL_TEACHERS,
  FACULTY_DIRECTORY,
  type FacultyProfile
} from "../../features/campushub/campus-hub-data";

export type FacultyCategoryKey = "director" | "hods" | "teachers" | "advisors";
export type TeacherSubgroupKey = "lecturers" | "phd";

interface FacultyCategoryMeta {
  key: FacultyCategoryKey;
  title: string;
  subtitle: string;
  icon: typeof Landmark;
  iconStyle: string;
  countLabel: (count: number) => string;
}

const FACULTY_CATEGORIES: FacultyCategoryMeta[] = [
  {
    key: "director",
    title: "Director",
    subtitle: "Office of the Director",
    icon: Landmark,
    iconStyle: "bg-secondary-soft text-secondary-ink",
    countLabel: (n) => (n === 1 ? "1 Office" : `${n} Offices`)
  },
  {
    key: "hods",
    title: "HODs",
    subtitle: "Heads of Departments",
    icon: GraduationCap,
    iconStyle: "bg-danger-soft text-danger-ink",
    countLabel: (n) => (n === 1 ? "1 HOD" : `${n} HODs`)
  },
  {
    key: "teachers",
    title: "Teachers",
    subtitle: "Faculty offices",
    icon: Users,
    iconStyle: "bg-subtle text-ink",
    countLabel: (n) => (n === 1 ? "1 Teacher" : `${n} Teachers`)
  },
  {
    key: "advisors",
    title: "Batch Advisors",
    subtitle: "Student advisory",
    icon: Headset,
    iconStyle: "bg-primary-soft text-primary-ink",
    countLabel: (n) => (n === 1 ? "1 Advisor" : `${n} Advisors`)
  }
];

const TEACHER_SUBGROUPS: Array<{
  key: TeacherSubgroupKey;
  title: string;
  cardSubtitle: string;
  sectionSubtitle: string;
  icon: typeof GraduationCap;
  iconStyle: string;
}> = [
  {
    key: "lecturers",
    title: "Lecturers",
    cardSubtitle: "Teaching faculty",
    sectionSubtitle: "Teaching faculty directory",
    icon: GraduationCap,
    iconStyle: "bg-success-soft text-success-ink"
  },
  {
    key: "phd",
    title: "PHD Faculty",
    cardSubtitle: "Doctoral researchers",
    sectionSubtitle: "Doctoral researchers directory",
    icon: Award,
    iconStyle: "bg-danger-soft text-danger-ink"
  }
];

const LECTURER_DISPLAY_ORDER = [
  "Mr. Bilal Shabir Qaisar",
  "Ms. Ayesha Tariq",
  "Mr. Hassan Raza",
  "Ms. Sana Malik",
  "Mr. Ali Shahzad"
];

const ADVISOR_BATCH_ORDER = [
  "SP23-BCS",
  "Fa24-BCS",
  "Fa23-FSN",
  "Fa22-BCS",
  "SP24-BSE",
  "SP25-BBA"
];

const ADVISOR_CARD_THEMES = [
  {
    avatarStyle: "bg-primary-soft border-primary/25 text-primary-ink",
    pillStyle: "bg-primary-soft text-primary-ink",
    arrowStyle: "bg-primary-soft text-primary-ink",
    batchPillStyle: "bg-primary-soft/80 border-primary/15 text-primary-ink"
  },
  {
    avatarStyle: "bg-secondary-soft border-secondary/25 text-secondary-ink",
    pillStyle: "bg-secondary-soft text-secondary-ink",
    arrowStyle: "bg-secondary-soft text-secondary-ink",
    batchPillStyle: "bg-secondary-soft/80 border-secondary/15 text-secondary-ink"
  }
] as const;

const HOD_ROW_THEMES = [
  {
    iconBg: "bg-primary-soft text-primary-ink",
    pillStyle: "bg-primary-soft/65 border-primary/15 text-primary-ink"
  },
  {
    iconBg: "bg-danger-soft text-danger-ink",
    pillStyle: "bg-danger-soft/65 border-danger/15 text-danger-ink"
  },
  {
    iconBg: "bg-accent-soft text-accent-ink",
    pillStyle: "bg-accent-soft/65 border-accent/20 text-accent-ink"
  },
  {
    iconBg: "bg-success-soft text-success-ink",
    pillStyle: "bg-success-soft/65 border-success/15 text-success-ink"
  }
] as const;

const HOD_DISPLAY_ORDER = [
  "Computer Science",
  "Food Science",
  "Chemistry",
  "Civil Engineering"
];

function getFacultyCategory(profile: FacultyProfile): FacultyCategoryKey {
  if (profile.designation === "Campus Director") return "director";
  if (profile.designation === "Head of Department (HOD)") return "hods";
  if (profile.designation === "Batch Advisor") return "advisors";
  return "teachers";
}

function getTeacherSubgroup(profile: FacultyProfile): TeacherSubgroupKey {
  if (
    profile.designation === "Dean of Faculty" ||
    profile.designation === "Tenured Professor" ||
    profile.designation === "Associate Professor"
  ) {
    return "phd";
  }
  return "lecturers";
}

function getBlueprintRoomTarget(profile: FacultyProfile): string {
  const match = profile.officeRoom.match(/Room\s+[A-Z]-\d+/i);
  if (match) return match[0];
  return profile.officeRoom.split("(")[0]?.trim() || "Room C-204";
}

function matchesSearchQuery(person: FacultyProfile, query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  return (
    person.name.toLowerCase().includes(q) ||
    person.designation.toLowerCase().includes(q) ||
    person.department.toLowerCase().includes(q) ||
    person.officeRoom.toLowerCase().includes(q) ||
    person.block.toLowerCase().includes(q) ||
    person.floor.toLowerCase().includes(q) ||
    person.researchFocus.toLowerCase().includes(q) ||
    (person.advisoryBatch?.toLowerCase().includes(q) ?? false) ||
    (person.advisorySeason?.toLowerCase().includes(q) ?? false)
  );
}

interface Props {
  onBack?: () => void;
  onShowOnBlueprint?: (blueprintKey: string, roomCode: string) => void;
}

/** Displays Faculty & Teachers Quick Access cards, HODs Directory, Teachers breakdown (Lecturers & PHD Faculty), and office lists. */
export function FacultyDirectoryBrowser({ onBack, onShowOnBlueprint }: Props) {
  const [selectedCategory, setSelectedCategory] = useState<FacultyCategoryKey | null>(null);
  const [selectedTeacherGroup, setSelectedTeacherGroup] = useState<TeacherSubgroupKey | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [departmentFilter, setDepartmentFilter] = useState("All");

  // Detail modal (used when tapping a minimal HOD card)
  const [detailPerson, setDetailPerson] = useState<FacultyProfile | null>(null);

  // Meeting Request modal state
  const [meetingFaculty, setMeetingFaculty] = useState<FacultyProfile | null>(null);
  const [meetingDay, setMeetingDay] = useState("Wednesday");
  const [meetingTime, setMeetingTime] = useState("11:30 AM");
  const [meetingNote, setMeetingNote] = useState("");
  const [meetingSent, setMeetingSent] = useState(false);

  useEffect(() => {
    if (!meetingFaculty && !detailPerson) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        if (meetingFaculty) {
          setMeetingFaculty(null);
        } else {
          setDetailPerson(null);
        }
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [meetingFaculty, detailPerson]);

  const activeCategoryMeta = useMemo(
    () => FACULTY_CATEGORIES.find((cat) => cat.key === selectedCategory) ?? null,
    [selectedCategory]
  );

  const activeTeacherSubgroupMeta = useMemo(
    () => TEACHER_SUBGROUPS.find((grp) => grp.key === selectedTeacherGroup) ?? null,
    [selectedTeacherGroup]
  );

  const categoryMembers = useMemo(() => {
    if (!selectedCategory) return [];
    if (selectedCategory === "hods") {
      return FACULTY_DIRECTORY.filter((f) => getFacultyCategory(f) === "hods").sort((a, b) => {
        const idxA = HOD_DISPLAY_ORDER.indexOf(a.department);
        const idxB = HOD_DISPLAY_ORDER.indexOf(b.department);
        const rankA = idxA === -1 ? 99 : idxA;
        const rankB = idxB === -1 ? 99 : idxB;
        return rankA - rankB;
      });
    }
    if (selectedCategory === "teachers") {
      const teachers = FACULTY_DIRECTORY.filter((f) => getFacultyCategory(f) === "teachers");
      if (!selectedTeacherGroup) return teachers;
      const filteredGroup = teachers.filter((f) => getTeacherSubgroup(f) === selectedTeacherGroup);
      if (selectedTeacherGroup === "lecturers") {
        return filteredGroup.sort((a, b) => {
          const idxA = LECTURER_DISPLAY_ORDER.indexOf(a.name);
          const idxB = LECTURER_DISPLAY_ORDER.indexOf(b.name);
          const rankA = idxA === -1 ? 99 : idxA;
          const rankB = idxB === -1 ? 99 : idxB;
          return rankA - rankB;
        });
      }
      return filteredGroup;
    }
    if (selectedCategory === "advisors") {
      return FACULTY_DIRECTORY.filter((f) => getFacultyCategory(f) === "advisors").sort((a, b) => {
        const idxA = ADVISOR_BATCH_ORDER.indexOf(a.advisoryBatch ?? "");
        const idxB = ADVISOR_BATCH_ORDER.indexOf(b.advisoryBatch ?? "");
        const rankA = idxA === -1 ? 99 : idxA;
        const rankB = idxB === -1 ? 99 : idxB;
        return rankA - rankB;
      });
    }
    return FACULTY_DIRECTORY.filter((f) => getFacultyCategory(f) === selectedCategory);
  }, [selectedCategory, selectedTeacherGroup]);

  const departmentOptions = useMemo(() => {
    const depts = new Set(categoryMembers.map((m) => m.department));
    return ["All", ...Array.from(depts)];
  }, [categoryMembers]);

  const filteredMembers = useMemo(() => {
    return categoryMembers.filter((f) => {
      if (departmentFilter !== "All" && f.department !== departmentFilter) return false;
      return matchesSearchQuery(f, searchQuery);
    });
  }, [categoryMembers, departmentFilter, searchQuery]);

  const openCategory = (catKey: FacultyCategoryKey) => {
    setSelectedCategory(catKey);
    setSelectedTeacherGroup(null);
    setSearchQuery("");
    setDepartmentFilter("All");
  };

  const openTeacherSubgroup = (groupKey: TeacherSubgroupKey) => {
    setSelectedTeacherGroup(groupKey);
    setSearchQuery("");
    setDepartmentFilter("All");
  };

  const openMeetingModal = (faculty: FacultyProfile) => {
    setDetailPerson(null);
    setMeetingFaculty(faculty);
    setMeetingSent(false);
    setMeetingNote("");
  };

  const renderDialogs = () => (
    <>
      {/* Office Details Modal (triggered from minimal HOD cards) */}
      {detailPerson && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="hod-detail-title"
          onClick={() => setDetailPerson(null)}
          className="fixed inset-0 z-50 flex items-center justify-center bg-overlay/65 backdrop-blur-xs p-4 animate-in fade-in duration-200"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-md rounded-3xl border border-line bg-panel p-6 shadow-2xl space-y-4 animate-in zoom-in-95 duration-200"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-3 min-w-0">
                <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-primary text-on-primary font-extrabold text-sm">
                  {detailPerson.avatarInitials}
                </span>
                <div className="min-w-0">
                  <span className="rounded-md bg-primary-soft px-2 py-0.5 text-[11px] font-bold text-primary-ink">
                    {detailPerson.department}
                  </span>
                  <h4 id="hod-detail-title" className="font-bold text-base text-ink mt-1">
                    {detailPerson.name}
                  </h4>
                  <p className="text-xs text-muted">{detailPerson.designation}</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setDetailPerson(null)}
                aria-label="Close office details"
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
                    {detailPerson.block}, {detailPerson.floor} · {detailPerson.officeRoom}
                  </span>
                </span>
                <span className="font-mono text-[11px] text-muted shrink-0">
                  {detailPerson.phoneExtension}
                </span>
              </div>

              <div className="flex items-center gap-2 text-muted pt-1.5 border-t border-line/50">
                <Clock size={13} className="text-success-ink shrink-0" />
                <span>
                  Office Hours: <strong className="text-ink">{detailPerson.consultationHours}</strong>
                </span>
              </div>

              <div className="flex items-center gap-2 text-muted">
                <Mail size={13} className="text-primary-ink shrink-0" />
                <a
                  href={`mailto:${detailPerson.email}`}
                  className="font-mono text-[11px] text-primary-ink hover:underline truncate"
                >
                  {detailPerson.email}
                </a>
              </div>
            </div>

            <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
              {onShowOnBlueprint ? (
                <button
                  type="button"
                  onClick={() => {
                    const target = getBlueprintRoomTarget(detailPerson);
                    const key = `${detailPerson.block} - ${detailPerson.floor}`;
                    setDetailPerson(null);
                    onShowOnBlueprint(key, target);
                  }}
                  className="rounded-xl border border-line bg-surface px-3.5 py-2 text-xs font-bold text-ink hover:border-primary/50 transition cursor-pointer"
                >
                  View on Floor Map
                </button>
              ) : (
                <span />
              )}

              <button
                type="button"
                onClick={() => openMeetingModal(detailPerson)}
                className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition cursor-pointer"
              >
                <Calendar size={13} />
                <span>Request Meeting</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Meeting Request Modal */}
      {meetingFaculty && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="faculty-meeting-title"
          onClick={() => setMeetingFaculty(null)}
          className="fixed inset-0 z-50 flex items-center justify-center bg-overlay/65 backdrop-blur-xs p-4 animate-in fade-in duration-200"
        >
          <div
            onClick={(e) => e.stopPropagation()}
            className="w-full max-w-md rounded-3xl border border-line bg-panel p-6 shadow-2xl space-y-5 animate-in zoom-in-95 duration-200"
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <span className="rounded-full bg-primary-soft px-2.5 py-0.5 text-[11px] font-extrabold text-primary-ink uppercase">
                  Meeting Request
                </span>
                <h3 id="faculty-meeting-title" className="font-bold text-base text-ink mt-1.5">
                  Meet with {meetingFaculty.name}
                </h3>
                <p className="text-xs text-muted mt-0.5">
                  {meetingFaculty.designation} · {meetingFaculty.officeRoom}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setMeetingFaculty(null)}
                aria-label="Close modal"
                className="rounded-xl p-1.5 text-muted hover:text-ink cursor-pointer"
              >
                <X size={16} />
              </button>
            </div>

            {meetingSent ? (
              <div className="rounded-2xl border border-success/40 bg-success-soft p-5 text-center space-y-2.5">
                <div className="inline-flex items-center gap-1.5 text-xs font-extrabold text-success-ink">
                  <CheckCircle2 size={18} />
                  <span>Request Sent!</span>
                </div>
                <p className="text-xs text-success-ink">
                  Sent to {meetingFaculty.email} for {meetingDay} at {meetingTime}.
                </p>
                <button
                  type="button"
                  onClick={() => setMeetingFaculty(null)}
                  className="rounded-xl bg-success px-4 py-2 text-xs font-bold text-success-fg hover:opacity-90 mt-1 cursor-pointer"
                >
                  Done
                </button>
              </div>
            ) : (
              <div className="space-y-4 text-xs">
                <div>
                  <span className="block font-bold text-ink mb-1">Office Hours</span>
                  <div className="rounded-xl border border-line bg-surface p-2.5 font-semibold text-ink text-xs">
                    {meetingFaculty.consultationHours}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label htmlFor="meeting-day-select" className="block font-bold text-ink mb-1">
                      Pick a Day
                    </label>
                    <select
                      id="meeting-day-select"
                      value={meetingDay}
                      onChange={(e) => setMeetingDay(e.target.value)}
                      className="w-full rounded-xl border border-line bg-surface px-3 py-2 text-xs font-semibold text-ink"
                    >
                      <option value="Monday">Monday</option>
                      <option value="Tuesday">Tuesday</option>
                      <option value="Wednesday">Wednesday</option>
                      <option value="Thursday">Thursday</option>
                      <option value="Friday">Friday</option>
                    </select>
                  </div>
                  <div>
                    <label htmlFor="meeting-time-select" className="block font-bold text-ink mb-1">
                      Pick a Time
                    </label>
                    <select
                      id="meeting-time-select"
                      value={meetingTime}
                      onChange={(e) => setMeetingTime(e.target.value)}
                      className="w-full rounded-xl border border-line bg-surface px-3 py-2 text-xs font-semibold text-ink"
                    >
                      <option value="11:30 AM">11:30 AM</option>
                      <option value="12:00 PM">12:00 PM</option>
                      <option value="01:30 PM">01:30 PM</option>
                      <option value="02:30 PM">02:30 PM</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label htmlFor="meeting-note-input" className="block font-bold text-ink mb-1">
                    What would you like to discuss?
                  </label>
                  <textarea
                    id="meeting-note-input"
                    rows={3}
                    placeholder="Write a short note (e.g. Course guidance, project question, grade review)..."
                    value={meetingNote}
                    onChange={(e) => setMeetingNote(e.target.value)}
                    className="w-full rounded-xl border border-line bg-surface p-2.5 text-xs text-ink placeholder:text-muted focus:outline-hidden focus:ring-2 focus:ring-primary/40"
                  />
                </div>

                <div className="flex items-center justify-end gap-2 pt-2 border-t border-line/60">
                  <button
                    type="button"
                    onClick={() => setMeetingFaculty(null)}
                    className="rounded-xl border border-line bg-surface px-4 py-2 text-xs font-bold text-muted hover:text-ink cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={() => setMeetingSent(true)}
                    disabled={!meetingNote.trim()}
                    className="rounded-xl bg-primary px-5 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover disabled:opacity-50 cursor-pointer"
                  >
                    Send Request
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );

  // ================= VIEW 1: FACULTY & TEACHERS (4 OFFICES GRID) =================
  if (!activeCategoryMeta) {
    return (
      <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
        <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-11 text-hero-fg rounded-b-[2rem] shadow-md">
          <div className="pointer-events-none absolute -top-10 -right-10 h-44 w-44 rounded-full bg-hero-fg/10 blur-xl" />
          <div className="pointer-events-none absolute top-4 right-12 h-24 w-24 rounded-full bg-hero-accent/20 blur-md" />

          <div className="relative z-10 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 min-w-0">
              {onBack && (
                <button
                  type="button"
                  onClick={onBack}
                  aria-label="Back to Campus Portal"
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-hero-fg/15 backdrop-blur-md text-hero-fg hover:bg-hero-fg/25 transition cursor-pointer"
                >
                  <ChevronLeft size={22} strokeWidth={2.5} />
                </button>
              )}

              <div className="min-w-0">
                <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-hero-fg leading-tight">
                  Faculty &amp; Teachers
                </h3>
                <p className="text-xs text-hero-muted mt-0.5">
                  Campus administrative offices
                </p>
              </div>
            </div>

            <span className="shrink-0 rounded-full border border-hero-fg/25 bg-hero-fg/15 px-3.5 py-1.5 text-xs font-semibold text-hero-fg whitespace-nowrap">
              {FACULTY_CATEGORIES.length} Offices
            </span>
          </div>

          <div className="relative z-10 mt-6 flex items-center gap-2">
            <span className="h-3.5 w-1 rounded-full bg-hero-accent/80" />
            <span className="text-xs font-extrabold uppercase tracking-wider text-hero-fg/90">
              QUICK ACCESS
            </span>
          </div>
        </div>

        <div className="relative z-10 -mt-5 px-4 pb-6 grid grid-cols-2 gap-3.5 sm:gap-4">
          {FACULTY_CATEGORIES.map((category) => {
            const Icon = category.icon;
            return (
              <button
                key={category.key}
                type="button"
                onClick={() => openCategory(category.key)}
                aria-label={category.title}
                className="rounded-3xl border border-line bg-panel p-4 sm:p-5 text-left shadow-sm hover:shadow-md hover:border-primary/40 transition flex flex-col justify-between min-h-[144px] cursor-pointer group"
              >
                <span
                  className={`flex h-11 w-11 items-center justify-center rounded-2xl ${category.iconStyle} transition group-hover:scale-105`}
                >
                  <Icon size={21} />
                </span>

                <div className="mt-4 space-y-1">
                  <span className="block font-bold text-base text-ink leading-snug">
                    {category.title}
                  </span>
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs text-muted leading-snug">
                      {category.subtitle}
                    </span>
                    <ChevronRight
                      size={15}
                      className="shrink-0 text-muted group-hover:text-ink group-hover:translate-x-0.5 transition"
                      aria-hidden="true"
                    />
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  // ================= VIEW 2A: HODS DIRECTORY (MATCHING 1ST SCREENSHOT) =================
  if (selectedCategory === "hods") {
    return (
      <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
        <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-6 text-hero-fg rounded-b-[2rem] shadow-md space-y-4">
          <div className="pointer-events-none absolute -top-10 -right-10 h-44 w-44 rounded-full bg-hero-fg/10 blur-xl" />
          <div className="pointer-events-none absolute top-4 right-12 h-24 w-24 rounded-full bg-hero-accent/20 blur-md" />

          <div className="relative z-10 flex items-center gap-3.5">
            <button
              type="button"
              onClick={() => setSelectedCategory(null)}
              aria-label="Back to Faculty & Teachers"
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-hero-fg/15 backdrop-blur-md text-hero-fg hover:bg-hero-fg/25 transition cursor-pointer"
            >
              <ChevronLeft size={20} strokeWidth={2.5} />
            </button>

            <div className="min-w-0">
              <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-hero-fg leading-tight">
                HODs Directory
              </h3>
              <p className="text-xs text-hero-muted mt-0.5">
                Heads of Departments
              </p>
            </div>
          </div>

          <div className="relative z-10 flex items-center gap-2 rounded-2xl bg-panel border border-line p-1.5 shadow-sm">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-subtle text-muted">
              <Search size={16} />
            </span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              aria-label="Search HODs by department or name"
              placeholder="Search by Department or Name..."
              className="flex-1 min-w-0 bg-transparent px-1 py-1.5 text-sm text-ink placeholder:text-muted focus:outline-hidden"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                aria-label="Clear search"
                className="mr-1 rounded-full p-1 text-muted hover:text-ink cursor-pointer"
              >
                <X size={14} />
              </button>
            )}
          </div>
        </div>

        {/* Count Strip */}
        <div className="px-5 pt-4 pb-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="h-4 w-1 rounded-full bg-primary" />
            <span className="text-xs font-extrabold uppercase tracking-wider text-muted">
              {filteredMembers.length} {filteredMembers.length === 1 ? "HOD FOUND" : "HODS FOUND"}
            </span>
          </div>
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

        {/* Stacked Minimal HOD Cards matching Screenshot 1 */}
        <div className="px-4 pb-6 space-y-3.5">
          {filteredMembers.length === 0 ? (
            <div className="rounded-3xl border border-line bg-panel p-8 text-center space-y-3">
              <p className="text-sm font-bold text-ink">No matching HOD found</p>
              <p className="text-xs text-muted">
                Try another department name or clear your search.
              </p>
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                className="rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition cursor-pointer"
              >
                Show All HODs
              </button>
            </div>
          ) : (
            filteredMembers.map((hod, index) => {
              const rowTheme = HOD_ROW_THEMES[index % HOD_ROW_THEMES.length]!;
              return (
                <button
                  key={hod.id}
                  type="button"
                  onClick={() => setDetailPerson(hod)}
                  className="w-full overflow-hidden rounded-3xl border border-line bg-panel text-left shadow-xs hover:shadow-md hover:border-primary/40 transition cursor-pointer group"
                >
                  {/* Blue Top Strip */}
                  <div className="bg-hero-bg px-4 py-3 text-hero-fg flex items-center gap-3">
                    <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-hero-fg/15 border border-hero-fg/25 text-xs font-bold text-hero-fg">
                      {hod.avatarInitials}
                    </span>
                    <span className="font-bold text-base text-hero-fg leading-snug truncate">
                      {hod.name}
                    </span>
                  </div>

                  {/* White Bottom Department Strip */}
                  <div className="px-4 py-3.5 bg-panel flex items-center gap-3">
                    <span
                      className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${rowTheme.iconBg}`}
                    >
                      <GraduationCap size={18} />
                    </span>
                    <span
                      className={`flex-1 rounded-xl border px-3.5 py-2 text-xs sm:text-sm font-semibold ${rowTheme.pillStyle} group-hover:opacity-90 transition`}
                    >
                      {hod.department}
                    </span>
                  </div>
                </button>
              );
            })
          )}
        </div>

        {renderDialogs()}
      </div>
    );
  }

  // ================= VIEW 2B: TEACHERS OVERVIEW (+ INLINE LECTURERS / PHD FACULTY DETAILS BELOW) =================
  if (selectedCategory === "teachers") {
    const ActiveGroupIcon = activeTeacherSubgroupMeta?.icon;

    return (
      <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
        {/* Top Curved Header */}
        <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-8 text-hero-fg rounded-b-[2rem] shadow-md">
          <div className="pointer-events-none absolute -top-10 -right-10 h-44 w-44 rounded-full bg-hero-fg/10 blur-xl" />
          <div className="pointer-events-none absolute top-4 right-12 h-24 w-24 rounded-full bg-hero-accent/20 blur-md" />

          <div className="relative z-10 flex items-center justify-between gap-3 mb-5">
            <button
              type="button"
              onClick={() => setSelectedCategory(null)}
              aria-label="Back to Faculty & Teachers"
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-hero-fg/15 backdrop-blur-md text-hero-fg hover:bg-hero-fg/25 transition cursor-pointer"
            >
              <ChevronLeft size={20} strokeWidth={2.5} />
            </button>

            <span className="shrink-0 rounded-full border border-hero-fg/25 bg-hero-fg/15 px-3.5 py-1.5 text-xs font-semibold text-hero-fg whitespace-nowrap">
              {TEACHER_SUBGROUPS.length} Categories
            </span>
          </div>

          <div className="relative z-10">
            <h3 className="text-2xl sm:text-3xl font-bold tracking-tight text-hero-fg leading-tight">
              Teachers
            </h3>
            <p className="text-xs text-hero-muted mt-1">
              Faculty offices &amp; staff directory
            </p>
          </div>
        </div>

        {/* Summary Card + Quick Access 2 Categories */}
        <div className="p-4 sm:p-5 space-y-5">
          <div className="rounded-3xl border border-line bg-panel p-4 sm:p-5 shadow-xs flex items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-primary-soft text-primary-ink">
                <Users size={22} />
              </span>
              <div>
                <p className="text-2xl sm:text-3xl font-extrabold text-ink leading-none">
                  {CAMPUS_TOTAL_TEACHERS}
                </p>
                <p className="text-xs font-medium text-muted mt-1.5">Total Teachers</p>
              </div>
            </div>

            <span
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-success-soft text-success-ink"
              aria-hidden="true"
            >
              <TrendingUp size={18} />
            </span>
          </div>

          <div className="space-y-3">
            <h4 className="px-1 text-xs font-extrabold uppercase tracking-wider text-muted">
              QUICK ACCESS
            </h4>

            <div className="grid grid-cols-2 gap-3.5 sm:gap-4">
              {TEACHER_SUBGROUPS.map((group) => {
                const GroupIcon = group.icon;
                const isSelected = selectedTeacherGroup === group.key;
                return (
                  <button
                    key={group.key}
                    type="button"
                    aria-pressed={isSelected}
                    onClick={() => openTeacherSubgroup(group.key)}
                    aria-label={group.title}
                    className={`rounded-3xl border bg-panel p-4 sm:p-5 text-left transition flex flex-col justify-between min-h-[144px] cursor-pointer group ${
                      isSelected
                        ? "border-primary ring-2 ring-primary/20 shadow-md"
                        : "border-line shadow-sm hover:shadow-md hover:border-primary/40"
                    }`}
                  >
                    <span
                      className={`flex h-11 w-11 items-center justify-center rounded-2xl ${group.iconStyle} transition group-hover:scale-105`}
                    >
                      <GroupIcon size={21} />
                    </span>

                    <div className="mt-4 space-y-1">
                      <span className="block font-bold text-base text-ink leading-snug">
                        {group.title}
                      </span>
                      <span className="block text-xs text-muted leading-snug">
                        {group.cardSubtitle}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Inline Selected Category List (shown below Quick Access on the same screen when clicked) */}
          {activeTeacherSubgroupMeta && ActiveGroupIcon && (
            <div className="space-y-4 pt-2 border-t border-line/60 animate-in fade-in duration-200">
              {/* Sub-header banner matching screenshot */}
              <div className="rounded-3xl bg-hero-bg px-4 sm:px-5 py-4 text-hero-fg flex items-center justify-between gap-3 shadow-sm">
                <div className="flex items-center gap-3 min-w-0">
                  <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-hero-fg/15 backdrop-blur-md text-hero-fg">
                    <ActiveGroupIcon size={21} />
                  </span>
                  <div className="min-w-0">
                    <h4 className="text-lg sm:text-xl font-bold text-hero-fg leading-tight">
                      {activeTeacherSubgroupMeta.title}
                    </h4>
                    <p className="text-xs text-hero-muted mt-0.5">
                      {activeTeacherSubgroupMeta.sectionSubtitle}
                    </p>
                  </div>
                </div>

                <span className="shrink-0 rounded-full border border-hero-fg/25 bg-hero-fg/15 px-3.5 py-1.5 text-xs font-semibold text-hero-fg whitespace-nowrap">
                  {categoryMembers.length} {categoryMembers.length === 1 ? "Member" : "Members"}
                </span>
              </div>

              {/* Rounded Search Input matching screenshot */}
              <div className="flex items-center gap-2 rounded-2xl border border-line bg-panel px-3.5 py-2 shadow-2xs">
                <Search size={16} className="shrink-0 text-primary-ink" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  aria-label={`Search ${activeTeacherSubgroupMeta.title}`}
                  placeholder="Search by teacher or department"
                  className="flex-1 min-w-0 bg-transparent py-1 text-sm text-ink placeholder:text-muted focus:outline-hidden"
                />
                {searchQuery && (
                  <button
                    type="button"
                    onClick={() => setSearchQuery("")}
                    aria-label="Clear search"
                    className="rounded-full p-1 text-muted hover:text-ink cursor-pointer"
                  >
                    <X size={14} />
                  </button>
                )}
              </div>

              {/* Result count */}
              <div className="flex items-center justify-between px-1">
                <span className="text-xs font-medium text-muted">
                  {filteredMembers.length} {filteredMembers.length === 1 ? "result" : "results"}
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

              {/* Stacked Minimal Teacher Cards matching screenshot */}
              {filteredMembers.length === 0 ? (
                <div className="rounded-3xl border border-line bg-panel p-8 text-center space-y-3">
                  <p className="text-sm font-bold text-ink">No matching teachers found</p>
                  <p className="text-xs text-muted">
                    Try another teacher name or department.
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
                <div className="space-y-3">
                  {filteredMembers.map((person) => (
                    <button
                      key={person.id}
                      type="button"
                      onClick={() => setDetailPerson(person)}
                      className="w-full rounded-3xl border border-line bg-panel p-4 shadow-2xs hover:shadow-md hover:border-primary/40 transition flex items-center gap-3.5 text-left cursor-pointer group"
                    >
                      <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-primary-soft text-primary-ink font-bold text-sm">
                        {person.avatarInitials}
                      </span>

                      <div className="min-w-0 flex-1">
                        <h5 className="font-bold text-sm sm:text-base text-ink leading-snug group-hover:text-primary-ink transition">
                          {person.name}
                        </h5>
                        <p className="text-xs text-muted mt-0.5">{person.department}</p>
                        <span className="inline-block mt-1.5 rounded-full bg-primary-soft px-3 py-0.5 text-[11px] font-semibold text-primary-ink">
                          {person.designation}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>

        {renderDialogs()}
      </div>
    );
  }

  // ================= VIEW 2C: BATCH ADVISORS (CORRECTED SCREENSHOT UI) =================
  if (selectedCategory === "advisors") {
    return (
      <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
        {/* Top Curved Header */}
        <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-6 text-hero-fg rounded-b-[2rem] shadow-md space-y-4">
          <div className="pointer-events-none absolute -top-10 -right-10 h-44 w-44 rounded-full bg-hero-fg/10 blur-xl" />
          <div className="pointer-events-none absolute top-4 right-12 h-24 w-24 rounded-full bg-hero-accent/20 blur-md" />

          <div className="relative z-10 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 min-w-0">
              <button
                type="button"
                onClick={() => setSelectedCategory(null)}
                aria-label="Back to Faculty & Teachers"
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-hero-fg/15 backdrop-blur-md text-hero-fg hover:bg-hero-fg/25 transition cursor-pointer"
              >
                <ChevronLeft size={20} strokeWidth={2.5} />
              </button>

              <div className="min-w-0">
                <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-hero-fg leading-tight">
                  Batch Advisors
                </h3>
                <p className="text-xs text-hero-muted mt-0.5">
                  Find your batch advisor
                </p>
              </div>
            </div>

            <span className="shrink-0 rounded-full border border-hero-fg/25 bg-hero-fg/15 px-3.5 py-1.5 text-xs font-semibold text-hero-fg whitespace-nowrap">
              {categoryMembers.length} {categoryMembers.length === 1 ? "Batch" : "Batches"}
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
              aria-label="Search by teacher or batch"
              placeholder="Search by Teacher or Batch"
              className="flex-1 min-w-0 bg-transparent px-1 py-1.5 text-sm text-ink placeholder:text-muted focus:outline-hidden"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                aria-label="Clear search"
                className="mr-1 rounded-full p-1 text-muted hover:text-ink cursor-pointer"
              >
                <X size={14} />
              </button>
            )}
          </div>
        </div>

        {/* Section Strip: properly spaced below hero curve (unclipped) */}
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
              {filteredMembers.length} {filteredMembers.length === 1 ? "entry" : "entries"}
            </span>
          </div>
        </div>

        {/* Stacked Batch Advisor Cards */}
        <div className="px-4 pb-6 space-y-3.5">
          {filteredMembers.length === 0 ? (
            <div className="rounded-3xl border border-line bg-panel p-8 text-center space-y-3">
              <p className="text-sm font-bold text-ink">No matching batch advisor found</p>
              <p className="text-xs text-muted">
                Try another advisor name or batch code (for example SP23-BCS).
              </p>
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                className="rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition cursor-pointer"
              >
                Show All Batches
              </button>
            </div>
          ) : (
            filteredMembers.map((advisor, idx) => {
              const cardTheme = ADVISOR_CARD_THEMES[idx % ADVISOR_CARD_THEMES.length]!;
              return (
                <button
                  key={advisor.id}
                  type="button"
                  onClick={() => setDetailPerson(advisor)}
                  className="w-full rounded-3xl border border-line bg-panel p-4 shadow-2xs hover:shadow-md hover:border-primary/40 transition text-left space-y-3 cursor-pointer group"
                >
                  {/* Top Row: Initials Circle + Name & Pill + Right Chevron */}
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3.5 min-w-0">
                      <span
                        className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-full border font-bold text-sm ${cardTheme.avatarStyle}`}
                      >
                        {advisor.avatarInitials}
                      </span>

                      <div className="min-w-0">
                        <h4 className="font-bold text-base text-ink leading-snug group-hover:text-primary-ink transition">
                          {advisor.name}
                        </h4>
                        <span
                          className={`inline-block mt-1 rounded-md px-2.5 py-0.5 text-[11px] font-semibold ${cardTheme.pillStyle}`}
                        >
                          {advisor.designation}
                        </span>
                      </div>
                    </div>

                    <span
                      className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${cardTheme.arrowStyle} group-hover:translate-x-0.5 transition`}
                      aria-hidden="true"
                    >
                      <ChevronRight size={16} />
                    </span>
                  </div>

                  {/* Divider */}
                  <div className="border-t border-line/60 pt-2.5 flex items-center justify-between gap-2">
                    <span
                      className={`inline-flex items-center gap-1.5 rounded-lg border px-2.5 py-1 text-xs font-semibold ${cardTheme.batchPillStyle}`}
                    >
                      <Users size={13} aria-hidden="true" />
                      <span>{advisor.advisoryBatch ?? advisor.department}</span>
                    </span>

                    {advisor.advisorySeason && (
                      <span className="rounded-lg border border-line bg-surface px-2.5 py-1 text-[11px] font-medium text-muted">
                        {advisor.advisorySeason}
                      </span>
                    )}
                  </div>
                </button>
              );
            })
          )}
        </div>

        {renderDialogs()}
      </div>
    );
  }

  // ================= VIEW 2D: DIRECTOR OFFICE VIEW =================
  const listTitle = activeCategoryMeta.title;
  const listSubtitle = activeCategoryMeta.subtitle;
  const ListIcon = activeCategoryMeta.icon;
  const listCountBadge = activeCategoryMeta.countLabel(categoryMembers.length);
  const backButtonLabel = "Back to Faculty & Teachers";
  const handleBackClick = () => setSelectedCategory(null);

  const showSearch = categoryMembers.length > 1;
  const hasFilters = searchQuery.trim().length > 0 || departmentFilter !== "All";

  return (
    <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
      <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-6 text-hero-fg rounded-b-[2rem] shadow-md space-y-4">
        <div className="pointer-events-none absolute -top-10 -right-10 h-44 w-44 rounded-full bg-hero-fg/10 blur-xl" />
        <div className="pointer-events-none absolute top-4 right-12 h-24 w-24 rounded-full bg-hero-accent/20 blur-md" />

        <div className="relative z-10 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <button
              type="button"
              onClick={handleBackClick}
              aria-label={backButtonLabel}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-hero-fg/15 backdrop-blur-md text-hero-fg hover:bg-hero-fg/25 transition cursor-pointer"
            >
              <ChevronLeft size={20} strokeWidth={2.5} />
            </button>

            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-hero-fg/15 backdrop-blur-md text-hero-fg shadow-xs">
              <ListIcon size={21} />
            </span>

            <div className="min-w-0">
              <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-hero-fg leading-tight">
                {listTitle}
              </h3>
              <p className="text-xs text-hero-muted mt-0.5">{listSubtitle}</p>
            </div>
          </div>

          <span className="shrink-0 rounded-full border border-hero-fg/25 bg-hero-fg/15 px-3.5 py-1.5 text-xs font-semibold text-hero-fg whitespace-nowrap">
            {listCountBadge}
          </span>
        </div>

        {showSearch && (
          <div className="relative z-10 flex items-center gap-2 rounded-2xl bg-panel border border-line p-1.5 shadow-sm">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-subtle text-muted">
              <Search size={16} />
            </span>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              aria-label={`Search ${listTitle}`}
              placeholder="Search by name, department, or room..."
              className="flex-1 min-w-0 bg-transparent px-1 py-1.5 text-sm text-ink placeholder:text-muted focus:outline-hidden"
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                aria-label="Clear search"
                className="mr-1 rounded-full p-1 text-muted hover:text-ink cursor-pointer"
              >
                <X size={14} />
              </button>
            )}
          </div>
        )}
      </div>

      <div className="p-4 sm:p-5 space-y-4">
        {departmentOptions.length > 2 && (
          <div
            className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:flex-wrap sm:overflow-visible"
            role="group"
            aria-label="Filter by department"
          >
            {departmentOptions.map((dept) => {
              const active = departmentFilter === dept;
              return (
                <button
                  key={dept}
                  type="button"
                  aria-pressed={active}
                  onClick={() => setDepartmentFilter(dept)}
                  className={`shrink-0 rounded-xl px-3 py-1.5 text-xs font-bold whitespace-nowrap transition cursor-pointer ${
                    active
                      ? "bg-primary text-on-primary shadow-2xs"
                      : "border border-line bg-panel text-muted hover:text-ink"
                  }`}
                >
                  {dept === "All" ? "All Departments" : dept}
                </button>
              );
            })}
          </div>
        )}

        <div className="flex items-center justify-between px-1">
          <div className="flex items-center gap-2">
            <span className="h-4 w-1 rounded-full bg-primary" />
            <span className="text-xs font-extrabold uppercase tracking-wider text-ink">
              {filteredMembers.length} {filteredMembers.length === 1 ? "PERSON" : "PEOPLE"} FOUND
            </span>
          </div>
          {hasFilters && (
            <button
              type="button"
              onClick={() => {
                setSearchQuery("");
                setDepartmentFilter("All");
              }}
              className="text-xs font-bold text-primary-ink hover:underline cursor-pointer"
            >
              Reset
            </button>
          )}
        </div>

        {filteredMembers.length === 0 ? (
          <div className="rounded-3xl border border-line bg-panel p-8 text-center space-y-3">
            <p className="text-sm font-bold text-ink">No matching offices found</p>
            <p className="text-xs text-muted">
              Try a different name, department, or clear the filters above.
            </p>
            <button
              type="button"
              onClick={() => {
                setSearchQuery("");
                setDepartmentFilter("All");
              }}
              className="rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition cursor-pointer"
            >
              Show All
            </button>
          </div>
        ) : (
          <div className="space-y-3.5">
            {filteredMembers.map((person) => (
              <div
                key={person.id}
                className="rounded-3xl border border-line bg-panel p-4 sm:p-5 shadow-2xs space-y-3.5 hover:border-primary/40 transition"
              >
                <div className="flex flex-col gap-2.5 sm:flex-row sm:items-start sm:justify-between">
                  <div className="flex items-start gap-3 min-w-0">
                    <div className="relative shrink-0">
                      <span className="flex h-11 w-11 sm:h-12 sm:w-12 items-center justify-center rounded-2xl bg-primary text-on-primary font-extrabold text-sm shadow-xs">
                        {person.avatarInitials}
                      </span>
                      <span
                        className={`absolute -bottom-0.5 -right-0.5 h-3.5 w-3.5 rounded-full border-2 border-panel ${
                          person.isAvailableToday ? "bg-success" : "bg-muted"
                        }`}
                        title={person.isAvailableToday ? "In Office Today" : "Not In Office Today"}
                      />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-start justify-between gap-2">
                        <h4 className="font-bold text-base text-ink leading-snug">
                          {person.name}
                        </h4>
                        <span
                          className={`sm:hidden shrink-0 rounded-full px-2 py-0.5 text-[10px] font-bold whitespace-nowrap ${
                            person.isAvailableToday
                              ? "bg-success-soft text-success-ink"
                              : "bg-subtle text-muted"
                          }`}
                        >
                          {person.isAvailableToday ? "In Office" : "By Appt."}
                        </span>
                      </div>
                      <div className="mt-1 flex flex-wrap items-center gap-1.5">
                        <span className="rounded-md bg-primary-soft px-2 py-0.5 text-[11px] font-bold text-primary-ink">
                          {person.designation}
                        </span>
                        {person.advisoryBatch && (
                          <span className="rounded-md bg-secondary-soft px-2 py-0.5 text-[11px] font-bold text-secondary-ink">
                            Batch {person.advisoryBatch}
                          </span>
                        )}
                        <span className="text-xs text-muted">{person.department}</span>
                      </div>
                    </div>
                  </div>

                  <span
                    className={`hidden sm:inline-flex shrink-0 rounded-full px-2.5 py-1 text-[11px] font-bold whitespace-nowrap ${
                      person.isAvailableToday
                        ? "bg-success-soft text-success-ink"
                        : "bg-subtle text-muted"
                    }`}
                  >
                    {person.isAvailableToday ? "Available Today" : "By Appointment"}
                  </span>
                </div>

                <div className="rounded-2xl border border-line/60 bg-surface/65 p-3.5 space-y-2 text-xs">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2 font-semibold text-ink">
                      <MapPin size={14} className="text-primary-ink shrink-0" />
                      <span>
                        {person.block}, {person.floor} · {person.officeRoom}
                      </span>
                    </div>
                    <span className="inline-flex items-center gap-1 font-mono text-[11px] text-muted">
                      <Phone size={11} />
                      {person.phoneExtension}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-muted pt-1 border-t border-line/50">
                    <Clock size={13} className="text-success-ink shrink-0" />
                    <span>
                      Office Hours: <strong className="text-ink">{person.consultationHours}</strong>
                    </span>
                  </div>

                  <div className="flex items-center gap-2 text-muted">
                    <Mail size={13} className="text-primary-ink shrink-0" />
                    <a
                      href={`mailto:${person.email}`}
                      className="font-mono text-[11px] text-primary-ink hover:underline truncate"
                    >
                      {person.email}
                    </a>
                  </div>

                  {person.researchFocus && (
                    <div className="flex items-start gap-2 text-muted pt-1 border-t border-line/50">
                      <GraduationCap size={13} className="text-secondary-ink shrink-0 mt-0.5" />
                      <span>
                        Focus: <strong className="text-ink font-semibold">{person.researchFocus}</strong>
                      </span>
                    </div>
                  )}
                </div>

                <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
                  {onShowOnBlueprint ? (
                    <button
                      type="button"
                      onClick={() =>
                        onShowOnBlueprint(
                          `${person.block} - ${person.floor}`,
                          getBlueprintRoomTarget(person)
                        )
                      }
                      className="rounded-xl border border-line bg-surface px-3.5 py-2 text-xs font-bold text-ink hover:border-primary/50 transition cursor-pointer"
                    >
                      View on Floor Map
                    </button>
                  ) : (
                    <span />
                  )}

                  <button
                    type="button"
                    onClick={() => openMeetingModal(person)}
                    className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition shadow-xs cursor-pointer"
                  >
                    <Calendar size={13} />
                    <span>Request Meeting</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {renderDialogs()}
    </div>
  );
}
