import { useState, useMemo } from "react";
import {
  Search,
  MapPin,
  Users,
  Building,
  BookOpen,
  Sparkles,
  Clock,
  Compass,
  Phone,
  Mail,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Ticket,
  Monitor,
  Tv,
  Wind,
  Wifi,
  X,
  ChevronRight,
  ArrowRight,
  ExternalLink,
  ShieldCheck,
  Mic,
  Activity,
  UserCheck,
  Briefcase,
  BarChart3,
  Cpu
} from "lucide-react";

import {
  FACULTY_DIRECTORY,
  ADMINISTRATIVE_OFFICES,
  CLASSROOMS_LABS,
  LIBRARY_INTELLIGENCE,
  FLOOR_BLUEPRINTS,
  CAMPUS_STATISTICS,
  type FacultyProfile,
  type AdministrativeOffice,
  type ClassroomLab,
  type LibraryBook
} from "../../features/campushub/campus-hub-data";

export type HubTab =
  | "labs"
  | "classrooms"
  | "faculty"
  | "offices"
  | "library"
  | "statistics"
  | "floorplans";

interface Props {
  initialTab?: HubTab;
}

export function CampusHubWayfindingEngine({ initialTab = "faculty" }: Props) {
  const [activeTab, setActiveTab] = useState<HubTab>(initialTab);

  // Search & Filter states
  const [facultyQuery, setFacultyQuery] = useState("");
  const [facultyDeptFilter, setFacultyDeptFilter] = useState("All");

  const [officeQuery, setOfficeQuery] = useState("");

  const [classroomBlockFilter, setClassroomBlockFilter] = useState("All");
  const [classroomQuery, setClassroomQuery] = useState("");

  const [libraryQuery, setLibraryQuery] = useState("");
  const [libraryCategoryFilter, setLibraryCategoryFilter] = useState("All");

  // Floor plan wayfinding states
  const [selectedBlueprintKey, setSelectedBlueprintKey] = useState<string>("Block C - 2nd Floor");
  const [highlightedRoomCode, setHighlightedRoomCode] = useState<string | null>("Room C-204");

  // Modal states
  const [meetingModalFaculty, setMeetingModalFaculty] = useState<FacultyProfile | null>(null);
  const [meetingPurpose, setMeetingPurpose] = useState("");
  const [meetingDate, setMeetingDate] = useState("Wednesday");
  const [meetingTime, setMeetingTime] = useState("11:30 AM");
  const [meetingSubmitted, setMeetingSubmitted] = useState(false);

  // Virtual Queue Ticket states
  const [virtualTicketOffice, setVirtualTicketOffice] = useState<AdministrativeOffice | null>(null);
  const [myTicketNumber, setMyTicketNumber] = useState<number | null>(null);

  // Book Reservation Modal states
  const [reservedBook, setReservedBook] = useState<LibraryBook | null>(null);
  const [bookReservedSuccess, setBookReservedSuccess] = useState(false);

  // Filtered Faculty
  const filteredFaculty = useMemo(() => {
    return FACULTY_DIRECTORY.filter((f) => {
      if (facultyDeptFilter !== "All" && f.department !== facultyDeptFilter) return false;
      if (facultyQuery.trim()) {
        const q = facultyQuery.toLowerCase();
        const matchName = f.name.toLowerCase().includes(q);
        const matchRole = f.designation.toLowerCase().includes(q);
        const matchDept = f.department.toLowerCase().includes(q);
        const matchOffice = f.officeRoom.toLowerCase().includes(q);
        return matchName || matchRole || matchDept || matchOffice;
      }
      return true;
    });
  }, [facultyQuery, facultyDeptFilter]);

  // Filtered Offices (Administrative Offices)
  const filteredOffices = useMemo(() => {
    return ADMINISTRATIVE_OFFICES.filter((off) => {
      if (officeQuery.trim()) {
        const q = officeQuery.toLowerCase();
        const matchName = off.name.toLowerCase().includes(q);
        const matchOfficer = off.headOfficer.toLowerCase().includes(q);
        const matchOffice = off.officeRoom.toLowerCase().includes(q);
        const matchBlockFloor = `${off.block} ${off.floor}`.toLowerCase().includes(q);
        const matchServices = off.servicesOffered.some((s) => s.toLowerCase().includes(q));
        return matchName || matchOfficer || matchOffice || matchBlockFloor || matchServices;
      }
      return true;
    });
  }, [officeQuery]);

  // Filtered Teacher Offices for Office Directory (search by teacher name or office/block/floor)
  const filteredTeacherOffices = useMemo(() => {
    return FACULTY_DIRECTORY.filter((f) => {
      if (officeQuery.trim()) {
        const q = officeQuery.toLowerCase();
        return (
          f.name.toLowerCase().includes(q) ||
          f.designation.toLowerCase().includes(q) ||
          f.department.toLowerCase().includes(q) ||
          f.officeRoom.toLowerCase().includes(q) ||
          `${f.block} ${f.floor}`.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [officeQuery]);

  // Separate Labs vs Classrooms
  const labDirectoryItems = useMemo(() => {
    return CLASSROOMS_LABS.filter(
      (cr) => cr.type === "Computer Lab" || cr.type === "Hardware/Engineering Lab"
    );
  }, []);

  const classroomItems = useMemo(() => {
    return CLASSROOMS_LABS.filter(
      (cr) => cr.type !== "Computer Lab" && cr.type !== "Hardware/Engineering Lab"
    );
  }, []);

  // Filtered Classrooms (supports search by block, floor, room code, or name)
  const filteredClassrooms = useMemo(() => {
    return classroomItems.filter((cr) => {
      if (classroomBlockFilter !== "All" && cr.block !== classroomBlockFilter) return false;
      if (classroomQuery.trim()) {
        const q = classroomQuery.toLowerCase();
        const matchCode = cr.roomCode.toLowerCase().includes(q);
        const matchName = cr.name.toLowerCase().includes(q);
        const matchType = cr.type.toLowerCase().includes(q);
        const matchBlockFloor = `${cr.block} ${cr.floor}`.toLowerCase().includes(q);
        return matchCode || matchName || matchType || matchBlockFloor;
      }
      return true;
    });
  }, [classroomItems, classroomBlockFilter, classroomQuery]);

  // Group all classrooms block-wise and floor-by-floor with identical structure per block
  const classroomsByBlock = useMemo(() => {
    const blocks = ["Block A", "Block B", "Block C", "Block D"] as const;
    const floorOrder = ["Ground Floor", "1st Floor", "2nd Floor", "3rd Floor"] as const;

    return blocks
      .filter((blk) => classroomBlockFilter === "All" || blk === classroomBlockFilter)
      .map((blk) => {
        const blkRooms = filteredClassrooms.filter((r) => r.block === blk);
        const floors = floorOrder
          .map((flr) => ({
            floor: flr,
            rooms: blkRooms.filter((r) => r.floor === flr)
          }))
          .filter((f) => f.rooms.length > 0);
        return {
          block: blk,
          totalRooms: blkRooms.length,
          floors
        };
      })
      .filter((b) => b.totalRooms > 0);
  }, [filteredClassrooms, classroomBlockFilter]);

  // Filtered Library Catalog
  const filteredBooks = useMemo(() => {
    return LIBRARY_INTELLIGENCE.catalog.filter((b) => {
      if (libraryCategoryFilter !== "All" && b.category !== libraryCategoryFilter) return false;
      if (libraryQuery.trim()) {
        const q = libraryQuery.toLowerCase();
        const matchTitle = b.title.toLowerCase().includes(q);
        const matchAuthor = b.authors.toLowerCase().includes(q);
        const matchIsbn = b.isbn.toLowerCase().includes(q);
        return matchTitle || matchAuthor || matchIsbn;
      }
      return true;
    });
  }, [libraryCategoryFilter, libraryQuery]);

  // Helper to jump to floor plan and highlight a room
  const locateOnFloorBlueprint = (blueprintKey: string, roomCode: string) => {
    setSelectedBlueprintKey(blueprintKey);
    setHighlightedRoomCode(roomCode);
    setActiveTab("floorplans");
  };

  const activeBlueprint = FLOOR_BLUEPRINTS[selectedBlueprintKey] || FLOOR_BLUEPRINTS["Block C - 2nd Floor"]!;

  return (
    <div className="space-y-6">
      {/* ================= 6 CAMPUS HUB DIRECTORY CARDS ================= */}
      <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-6">
        {/* Card 1: Lab Directory */}
        <button
          type="button"
          onClick={() => setActiveTab("labs")}
          className={`flex flex-col justify-between rounded-2xl border p-4 text-left transition shadow-2xs group ${
            activeTab === "labs"
              ? "border-cyan-600 bg-panel ring-2 ring-cyan-500/30"
              : "border-line bg-panel hover:border-cyan-500/50"
          }`}
        >
          <div className="flex items-center justify-between">
            <div
              className={`flex h-10 w-10 items-center justify-center rounded-xl transition ${
                activeTab === "labs"
                  ? "bg-cyan-600 text-white"
                  : "bg-cyan-500/10 text-cyan-600 group-hover:scale-105"
              }`}
            >
              <Cpu size={20} />
            </div>
            <span className="text-2xs font-extrabold text-muted">
              {labDirectoryItems.length} Labs
            </span>
          </div>
          <div className="mt-3">
            <h4 className="font-extrabold text-sm text-ink group-hover:text-cyan-600 transition">
              Lab Directory
            </h4>
            <p className="text-[11px] text-muted line-clamp-1 mt-0.5">
              CS, AI, Cisco &amp; CAD Labs
            </p>
          </div>
        </button>

        {/* Card 2: Classrooms */}
        <button
          type="button"
          onClick={() => setActiveTab("classrooms")}
          className={`flex flex-col justify-between rounded-2xl border p-4 text-left transition shadow-2xs group ${
            activeTab === "classrooms"
              ? "border-emerald-600 bg-panel ring-2 ring-emerald-500/30"
              : "border-line bg-panel hover:border-emerald-500/50"
          }`}
        >
          <div className="flex items-center justify-between">
            <div
              className={`flex h-10 w-10 items-center justify-center rounded-xl transition ${
                activeTab === "classrooms"
                  ? "bg-emerald-600 text-white"
                  : "bg-emerald-500/10 text-emerald-600 group-hover:scale-105"
              }`}
            >
              <Building size={20} />
            </div>
            <span className="text-2xs font-extrabold text-muted">
              {classroomItems.length} Rooms
            </span>
          </div>
          <div className="mt-3">
            <h4 className="font-extrabold text-sm text-ink group-hover:text-emerald-600 transition">
              Classrooms
            </h4>
            <p className="text-[11px] text-muted line-clamp-1 mt-0.5">
              Block &amp; Floor Directory
            </p>
          </div>
        </button>

        {/* Card 3: Faculty & Teachers */}
        <button
          type="button"
          onClick={() => setActiveTab("faculty")}
          className={`flex flex-col justify-between rounded-2xl border p-4 text-left transition shadow-2xs group ${
            activeTab === "faculty"
              ? "border-brand-600 bg-panel ring-2 ring-brand-500/30"
              : "border-line bg-panel hover:border-brand-500/50"
          }`}
        >
          <div className="flex items-center justify-between">
            <div
              className={`flex h-10 w-10 items-center justify-center rounded-xl transition ${
                activeTab === "faculty"
                  ? "bg-brand-600 text-white"
                  : "bg-brand-500/10 text-brand-600 group-hover:scale-105"
              }`}
            >
              <Users size={20} />
            </div>
            <span className="text-2xs font-extrabold text-muted">
              {FACULTY_DIRECTORY.length} Staff
            </span>
          </div>
          <div className="mt-3">
            <h4 className="font-extrabold text-sm text-ink group-hover:text-brand-600 transition">
              Faculty &amp; Teachers
            </h4>
            <p className="text-[11px] text-muted line-clamp-1 mt-0.5">
              Director, HODs &amp; Advisors
            </p>
          </div>
        </button>

        {/* Card 4: Office Directory */}
        <button
          type="button"
          onClick={() => setActiveTab("offices")}
          className={`flex flex-col justify-between rounded-2xl border p-4 text-left transition shadow-2xs group ${
            activeTab === "offices"
              ? "border-indigo-600 bg-panel ring-2 ring-indigo-500/30"
              : "border-line bg-panel hover:border-indigo-500/50"
          }`}
        >
          <div className="flex items-center justify-between">
            <div
              className={`flex h-10 w-10 items-center justify-center rounded-xl transition ${
                activeTab === "offices"
                  ? "bg-indigo-600 text-white"
                  : "bg-indigo-500/10 text-indigo-600 group-hover:scale-105"
              }`}
            >
              <Briefcase size={20} />
            </div>
            <span className="text-2xs font-extrabold text-muted">
              Block &amp; Floor
            </span>
          </div>
          <div className="mt-3">
            <h4 className="font-extrabold text-sm text-ink group-hover:text-indigo-600 transition">
              Office Directory
            </h4>
            <p className="text-[11px] text-muted line-clamp-1 mt-0.5">
              Teacher &amp; Admin Offices
            </p>
          </div>
        </button>

        {/* Card 5: Library */}
        <button
          type="button"
          onClick={() => setActiveTab("library")}
          className={`flex flex-col justify-between rounded-2xl border p-4 text-left transition shadow-2xs group ${
            activeTab === "library"
              ? "border-amber-600 bg-panel ring-2 ring-amber-500/30"
              : "border-line bg-panel hover:border-amber-500/50"
          }`}
        >
          <div className="flex items-center justify-between">
            <div
              className={`flex h-10 w-10 items-center justify-center rounded-xl transition ${
                activeTab === "library"
                  ? "bg-amber-600 text-white"
                  : "bg-amber-500/10 text-amber-600 group-hover:scale-105"
              }`}
            >
              <BookOpen size={20} />
            </div>
            <span className="text-2xs font-extrabold text-emerald-600">
              {LIBRARY_INTELLIGENCE.availableSilentSeats} Free
            </span>
          </div>
          <div className="mt-3">
            <h4 className="font-extrabold text-sm text-ink group-hover:text-amber-600 transition">
              Library
            </h4>
            <p className="text-[11px] text-muted line-clamp-1 mt-0.5">
              Seats &amp; Digital Catalog
            </p>
          </div>
        </button>

        {/* Card 6: Statistics */}
        <button
          type="button"
          onClick={() => setActiveTab("statistics")}
          className={`flex flex-col justify-between rounded-2xl border p-4 text-left transition shadow-2xs group ${
            activeTab === "statistics"
              ? "border-purple-600 bg-panel ring-2 ring-purple-500/30"
              : "border-line bg-panel hover:border-purple-500/50"
          }`}
        >
          <div className="flex items-center justify-between">
            <div
              className={`flex h-10 w-10 items-center justify-center rounded-xl transition ${
                activeTab === "statistics"
                  ? "bg-purple-600 text-white"
                  : "bg-purple-500/10 text-purple-600 group-hover:scale-105"
              }`}
            >
              <BarChart3 size={20} />
            </div>
            <span className="text-2xs font-extrabold text-purple-600">
              Campus Data
            </span>
          </div>
          <div className="mt-3">
            <h4 className="font-extrabold text-sm text-ink group-hover:text-purple-600 transition">
              Statistics
            </h4>
            <p className="text-[11px] text-muted line-clamp-1 mt-0.5">
              Enrollment &amp; Facilities
            </p>
          </div>
        </button>
      </div>

      {/* Quick Wayfinding Blueprints Bar */}
      <div className="flex items-center justify-end">
        <button
          type="button"
          onClick={() => setActiveTab("floorplans")}
          className={`inline-flex items-center gap-1.5 rounded-xl border px-3 py-1.5 text-xs font-bold transition ${
            activeTab === "floorplans"
              ? "border-purple-600 bg-purple-600 text-white"
              : "border-line bg-panel text-purple-600 hover:border-purple-500"
          }`}
        >
          <Compass size={14} />
          <span>Interactive Floor Blueprints</span>
        </button>
      </div>

      {/* ================= TAB 1: FACULTY & LEADERSHIP DIRECTORY ================= */}
      {activeTab === "faculty" && (
        <div className="space-y-6 animate-in fade-in duration-200">
          {/* Search & Department Filters */}
          <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs flex flex-wrap items-center gap-4">
            <div className="flex-1 min-w-[260px] relative">
              <input
                type="text"
                placeholder="Search faculty by name, designation, department, or office (e.g. Dr. Munir, HOD, C-301)..."
                value={facultyQuery}
                onChange={(e) => setFacultyQuery(e.target.value)}
                className="w-full rounded-xl border border-line bg-surface px-3 py-2.5 pl-9 text-xs text-ink placeholder:text-muted focus:outline-hidden focus:ring-2 focus:ring-brand-500"
              />
              <Search size={14} className="absolute left-3 top-3 text-muted" />
              {facultyQuery && (
                <button onClick={() => setFacultyQuery("")} className="absolute right-3 top-3 text-muted hover:text-ink">
                  <X size={12} />
                </button>
              )}
            </div>

            <div className="flex items-center gap-2">
              <label className="text-xs font-semibold text-muted">Department:</label>
              <select
                value={facultyDeptFilter}
                onChange={(e) => setFacultyDeptFilter(e.target.value)}
                className="rounded-xl border border-line bg-surface px-3 py-2 text-xs font-semibold text-ink focus:outline-hidden focus:ring-2 focus:ring-brand-500"
              >
                <option value="All">All Departments</option>
                <option value="Computer Science">Computer Science</option>
                <option value="Electrical Engineering">Electrical Engineering</option>
                <option value="Management Sciences">Management Sciences</option>
                <option value="Physics & Engineering">Physics & Engineering</option>
              </select>
            </div>
          </div>

          {/* Faculty Profiles Grid */}
          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {filteredFaculty.map((f) => (
              <div
                key={f.id}
                className="flex flex-col justify-between rounded-3xl border border-line bg-panel p-5 shadow-2xs hover:border-brand-500/60 transition group space-y-4"
              >
                <div className="space-y-3.5">
                  {/* Top Bar: Avatar & Availability */}
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div className="relative">
                        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-600 to-indigo-700 text-white font-extrabold text-sm shadow-xs">
                          {f.avatarInitials}
                        </div>
                        <span
                          className={`absolute -bottom-0.5 -right-0.5 h-3.5 w-3.5 rounded-full border-2 border-panel ${
                            f.isAvailableToday ? "bg-emerald-500" : "bg-zinc-400"
                          }`}
                          title={f.isAvailableToday ? "In Office Today" : "Not In Office Today"}
                        />
                      </div>
                      <div>
                        <h4 className="font-extrabold text-base text-ink group-hover:text-brand-600 transition leading-snug">
                          {f.name}
                        </h4>
                        <span className="inline-block rounded-md bg-brand-500/10 px-2 py-0.5 text-2xs font-bold text-brand-600 mt-0.5">
                          {f.designation}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Office & Spatial Location Link */}
                  <div className="rounded-xl border border-line/60 bg-surface/50 p-3 space-y-1.5 text-xs">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-1.5 text-muted">
                        <MapPin size={13} className="text-brand-500 shrink-0" />
                        <span className="font-semibold text-ink">{f.officeRoom}</span>
                      </div>
                      <button
                        onClick={() =>
                          locateOnFloorBlueprint(
                            `${f.block} - ${f.floor}`,
                            f.officeRoom.includes("C-301")
                              ? "Room C-301"
                              : f.officeRoom.includes("C-205")
                              ? "Room C-205"
                              : f.officeRoom.includes("A-101")
                              ? "Room A-101"
                              : "Room C-204"
                          )
                        }
                        className="text-2xs font-bold text-brand-600 hover:underline shrink-0"
                      >
                        Show on Blueprint →
                      </button>
                    </div>

                    <div className="flex items-center justify-between text-2xs text-muted pt-1 border-t border-line/40">
                      <span>{f.department}</span>
                      <span className="font-mono">{f.phoneExtension}</span>
                    </div>
                  </div>

                  {/* Consultation Hours & Email */}
                  <div className="space-y-1.5 text-xs">
                    <div className="flex items-center gap-1.5 text-muted">
                      <Clock size={12} className="text-emerald-500 shrink-0" />
                      <span className="text-2xs">
                        Consultation: <strong className="text-ink">{f.consultationHours}</strong>
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5 text-muted">
                      <Mail size={12} className="text-brand-500 shrink-0" />
                      <a href={`mailto:${f.email}`} className="text-2xs font-mono text-brand-600 hover:underline truncate">
                        {f.email}
                      </a>
                    </div>
                  </div>

                  {/* Research Focus */}
                  <p className="text-2xs text-muted leading-relaxed line-clamp-2">
                    <strong className="text-ink">Focus:</strong> {f.researchFocus}
                  </p>
                </div>

                {/* Bottom Action Footer */}
                <div className="pt-3 border-t border-line/60">
                  <button
                    onClick={() => {
                      setMeetingModalFaculty(f);
                      setMeetingSubmitted(false);
                      setMeetingPurpose("");
                    }}
                    className="w-full inline-flex items-center justify-center gap-1.5 rounded-xl bg-brand-600 py-2.5 text-xs font-bold text-white hover:bg-brand-700 transition shadow-xs"
                  >
                    <Calendar size={13} />
                    <span>Request Meeting / Consultation</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ================= TAB 2: OFFICE DIRECTORY (TEACHER + ADMIN OFFICES) ================= */}
      {activeTab === "offices" && (
        <div className="space-y-6 animate-in fade-in duration-200">
          {/* Search Bar */}
          <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs">
            <div className="relative">
              <input
                type="text"
                placeholder="Search by teacher name or office name (e.g. Sir Munir, Registrar, Accounts, Block A, 3rd Floor)..."
                value={officeQuery}
                onChange={(e) => setOfficeQuery(e.target.value)}
                className="w-full rounded-xl border border-line bg-surface px-3 py-2.5 pl-9 text-xs text-ink placeholder:text-muted focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
              />
              <Search size={14} className="absolute left-3 top-3 text-muted" />
              {officeQuery && (
                <button onClick={() => setOfficeQuery("")} className="absolute right-3 top-3 text-muted hover:text-ink">
                  <X size={12} />
                </button>
              )}
            </div>
          </div>

          {/* Faculty & Teacher Offices (Block & Floor Locator) */}
          {filteredTeacherOffices.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-extrabold uppercase tracking-wider text-muted">
                Faculty &amp; Teacher Offices ({filteredTeacherOffices.length})
              </h3>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {filteredTeacherOffices.map((f) => (
                  <div
                    key={`off-${f.id}`}
                    className="rounded-2xl border border-line bg-panel p-4 shadow-2xs space-y-2.5 hover:border-indigo-500/60 transition"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <h4 className="font-extrabold text-sm text-ink">{f.name}</h4>
                        <p className="text-2xs font-semibold text-indigo-600">{f.designation}</p>
                        <p className="text-2xs text-muted">{f.department}</p>
                      </div>
                      <span className="rounded-lg bg-indigo-500/10 px-2 py-0.5 text-2xs font-bold text-indigo-600 shrink-0">
                        {f.phoneExtension}
                      </span>
                    </div>

                    <div className="rounded-xl border border-line/60 bg-surface/60 p-3 text-xs space-y-1">
                      <p className="font-bold text-ink flex items-center gap-1.5">
                        <MapPin size={13} className="text-indigo-600 shrink-0" />
                        <span>
                          {f.block}, {f.floor}
                        </span>
                      </p>
                      <p className="text-2xs text-muted pl-5">{f.officeRoom}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Administrative Offices List */}
          <div className="space-y-3">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-muted">
              Administrative Offices &amp; Services ({filteredOffices.length})
            </h3>
            <div className="grid gap-6 lg:grid-cols-2">
              {filteredOffices.map((off) => (
              <div
                key={off.id}
                className="rounded-3xl border border-line bg-panel p-6 shadow-2xs space-y-5 flex flex-col justify-between hover:border-indigo-500/60 transition group"
              >
                <div className="space-y-4">
                  {/* Top Bar: Office Name & Status */}
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <span className="rounded-md bg-indigo-500/10 px-2 py-0.5 text-2xs font-extrabold text-indigo-600">
                        {off.category}
                      </span>
                      <h4 className="font-extrabold text-base text-ink mt-1.5 group-hover:text-indigo-600 transition">
                        {off.name}
                      </h4>
                      <p className="text-xs text-muted mt-0.5">
                        In-charge: <strong className="text-ink">{off.headOfficer}</strong> ({off.headTitle})
                      </p>
                    </div>

                    <span
                      className={`rounded-full px-2.5 py-1 text-2xs font-extrabold ${
                        off.counterStatus === "OPEN"
                          ? "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300"
                          : off.counterStatus === "BUSY"
                          ? "bg-amber-500/15 text-amber-700 dark:text-amber-300"
                          : "bg-rose-500/15 text-rose-700 dark:text-rose-300"
                      }`}
                    >
                      {off.counterStatus === "OPEN" ? "● Counter Active" : "● Busy Traffic"}
                    </span>
                  </div>

                  {/* Live Ticket Queue Telemetry Box */}
                  <div className="rounded-2xl border border-indigo-500/30 bg-indigo-500/5 p-4 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-indigo-700 dark:text-indigo-300 flex items-center gap-1.5">
                        <Ticket size={14} />
                        <span>Live Queue Telemetry</span>
                      </span>
                      <span className="font-mono text-2xs font-semibold text-muted">
                        Avg Wait: ~{off.avgWaitMinutes} mins
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 pt-1 border-t border-indigo-500/20 text-xs">
                      <div className="rounded-xl bg-panel border border-line p-2.5 text-center">
                        <span className="text-2xs text-muted block">Now Serving Token</span>
                        <span className="font-mono font-extrabold text-lg text-indigo-600">
                          #{off.currentTicketServing}
                        </span>
                      </div>
                      <div className="rounded-xl bg-panel border border-line p-2.5 text-center">
                        <span className="text-2xs text-muted block">Students in Line</span>
                        <span className="font-mono font-extrabold text-lg text-amber-600">
                          {off.queueLength} Waiting
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Location & Contact Info */}
                  <div className="space-y-1.5 text-xs text-muted">
                    <div className="flex items-center justify-between">
                      <p className="flex items-center gap-1.5">
                        <MapPin size={13} className="text-brand-500 shrink-0" />
                        <span className="font-semibold text-ink">
                          {off.block}, {off.floor} — {off.officeRoom}
                        </span>
                      </p>
                      <button
                        onClick={() =>
                          locateOnFloorBlueprint(
                            `${off.block} - ${off.floor}`,
                            off.officeRoom.includes("A-101")
                              ? "Room A-101"
                              : off.officeRoom.includes("A-105")
                              ? "Room A-105"
                              : "Room C-204"
                          )
                        }
                        className="text-2xs font-bold text-brand-600 hover:underline"
                      >
                        Locate on Blueprint →
                      </button>
                    </div>

                    <div className="flex items-center justify-between text-2xs pt-1">
                      <span className="flex items-center gap-1">
                        <Clock size={11} className="text-emerald-500" />
                        <span>{off.workingHours}</span>
                      </span>
                      <span className="font-mono">{off.phoneExtension}</span>
                    </div>
                  </div>

                  {/* Services Offered Pills */}
                  <div className="space-y-1.5">
                    <span className="text-2xs font-bold uppercase tracking-wider text-muted">
                      Services Handled:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {off.servicesOffered.map((s, i) => (
                        <span key={i} className="rounded-lg bg-surface border border-line/60 px-2.5 py-1 text-2xs text-ink font-medium">
                          ✓ {s}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Bottom Action Footer */}
                <div className="pt-3 border-t border-line/60">
                  <button
                    onClick={() => {
                      setVirtualTicketOffice(off);
                      setMyTicketNumber(off.currentTicketServing + off.queueLength + 1);
                    }}
                    className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 py-2.5 text-xs font-bold text-white hover:bg-indigo-700 transition shadow-xs"
                  >
                    <Ticket size={14} />
                    <span>Generate Virtual Queue Token</span>
                  </button>
                </div>
              </div>
            ))}
            </div>
          </div>
        </div>
      )}

      {/* ================= TAB: LAB DIRECTORY ================= */}
      {activeTab === "labs" && (
        <div className="space-y-6 animate-in fade-in duration-200">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h3 className="text-base font-extrabold text-ink">Campus Lab Directory</h3>
              <p className="text-xs text-muted">
                Specialized computer, AI/GPU, networking, and CAD engineering laboratories across blocks.
              </p>
            </div>
            <span className="rounded-full bg-cyan-500/10 px-3 py-1 text-xs font-bold text-cyan-600">
              {labDirectoryItems.length} Active Laboratories
            </span>
          </div>

          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {labDirectoryItems.map((lab) => (
              <div
                key={lab.id}
                className="rounded-3xl border border-line bg-panel p-5 shadow-2xs space-y-4 flex flex-col justify-between hover:border-cyan-500/60 transition"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h4 className="font-extrabold text-base text-ink">{lab.roomCode}</h4>
                      <p className="text-xs text-muted mt-0.5">{lab.name}</p>
                    </div>
                    <span className="rounded-full bg-cyan-500/10 px-2.5 py-1 text-2xs font-bold text-cyan-600 shrink-0">
                      {lab.type}
                    </span>
                  </div>

                  <div className="rounded-xl border border-line/60 bg-surface/50 p-3 space-y-1.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-muted">Location</span>
                      <span className="font-bold text-ink">{lab.block}, {lab.floor}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-muted">Capacity / Workstations</span>
                      <span className="font-bold text-ink">{lab.capacity} Seats ({lab.equipment.workstationsCount} PCs)</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-muted">Lab In-Charge</span>
                      <span className="font-semibold text-ink">{lab.inCharge}</span>
                    </div>
                  </div>

                  {lab.equipment.specialGear && (
                    <p className="text-2xs text-amber-700 dark:text-amber-300 font-medium">
                      ⚡ {lab.equipment.specialGear}
                    </p>
                  )}
                </div>

                <button
                  type="button"
                  onClick={() =>
                    locateOnFloorBlueprint(
                      lab.block === "Engineering Labs"
                        ? "Engineering Labs - Ground Floor"
                        : `${lab.block} - ${lab.floor}`,
                      lab.roomCode
                    )
                  }
                  className="w-full inline-flex items-center justify-center gap-1.5 rounded-xl border border-line bg-surface py-2 text-xs font-bold text-cyan-600 hover:border-cyan-500 transition"
                >
                  <Compass size={13} />
                  <span>View on Floor Blueprint</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ================= TAB: CAMPUS STATISTICS ================= */}
      {activeTab === "statistics" && (
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

      {/* ================= TAB 3: CLASSROOMS (SEARCH + BLOCK-WISE FLOOR CARDS) ================= */}
      {activeTab === "classrooms" && (
        <div className="space-y-6 animate-in fade-in duration-200">
          {/* Block Selector Chips & Search Bar */}
          <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs space-y-4">
            <div className="relative">
              <input
                type="text"
                placeholder="Search classrooms by block, floor, room code, or name (e.g. Block A, 2nd Floor, C-204)..."
                value={classroomQuery}
                onChange={(e) => setClassroomQuery(e.target.value)}
                className="w-full rounded-xl border border-line bg-surface px-3 py-2 pl-9 text-xs text-ink placeholder:text-muted focus:outline-hidden focus:ring-2 focus:ring-emerald-500"
              />
              <Search size={14} className="absolute left-3 top-2.5 text-muted" />
              {classroomQuery && (
                <button onClick={() => setClassroomQuery("")} className="absolute right-3 top-2.5 text-muted hover:text-ink">
                  <X size={12} />
                </button>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-line/60">
              <span className="text-2xs font-bold uppercase tracking-wider text-muted mr-1">
                Filter by Block:
              </span>
              {["All", "Block A", "Block B", "Block C", "Block D"].map((blk) => (
                <button
                  key={blk}
                  onClick={() => setClassroomBlockFilter(blk)}
                  className={`rounded-xl px-3 py-1.5 text-xs font-semibold transition border ${
                    classroomBlockFilter === blk
                      ? "border-emerald-600 bg-emerald-600 text-white font-bold shadow-xs"
                      : "border-line bg-surface text-muted hover:text-ink"
                  }`}
                >
                  {blk}
                </button>
              ))}
            </div>
          </div>

          {/* Block-Wise Classrooms Directory (One Card per Block, Grouped by Floor) */}
          <div className="space-y-3">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-muted">
              All Classrooms Block-Wise (Floor-by-Floor Structure)
            </h3>
            <div className="grid gap-5 md:grid-cols-2">
              {classroomsByBlock.map((blkGroup) => (
                <div
                  key={blkGroup.block}
                  className="rounded-3xl border border-line bg-panel p-5 shadow-2xs space-y-4"
                >
                  <div className="flex items-center justify-between border-b border-line pb-3">
                    <div className="flex items-center gap-2.5">
                      <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-600">
                        <Building size={18} />
                      </span>
                      <div>
                        <h4 className="font-extrabold text-base text-ink">{blkGroup.block}</h4>
                        <p className="text-2xs text-muted">
                          {blkGroup.floors.length} {blkGroup.floors.length === 1 ? "Floor" : "Floors"} · {blkGroup.totalRooms} Classrooms
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    {blkGroup.floors.map((flr) => (
                      <div key={flr.floor} className="space-y-1.5">
                        <p className="text-xs font-bold text-emerald-700 dark:text-emerald-300">
                          {flr.floor}
                        </p>
                        <div className="space-y-1.5">
                          {flr.rooms.map((rm) => (
                            <div
                              key={rm.id}
                              className="flex items-center justify-between gap-2 rounded-xl border border-line/60 bg-surface/60 px-3 py-2 text-xs"
                            >
                              <div className="min-w-0">
                                <span className="font-mono font-bold text-ink">{rm.roomCode}</span>
                                <span className="text-muted ml-2 truncate">{rm.name}</span>
                              </div>
                              <span className="text-2xs font-semibold text-muted shrink-0">
                                {rm.capacity} seats
                              </span>
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

          {/* Detailed Classroom Cards (with explicit Block & Floor badges) */}
          <div className="space-y-3">
            <h3 className="text-xs font-extrabold uppercase tracking-wider text-muted">
              Classroom Search Results &amp; Equipment Details ({filteredClassrooms.length})
            </h3>
            <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
              {filteredClassrooms.map((cr) => (
                <div
                  key={cr.id}
                  className="rounded-3xl border border-line bg-panel p-5 shadow-2xs space-y-4 flex flex-col justify-between hover:border-emerald-500/60 transition group"
                >
                  <div className="space-y-3.5">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="flex flex-wrap items-center gap-1.5">
                          <h4 className="font-extrabold text-base text-ink group-hover:text-emerald-600 transition">
                            {cr.roomCode}
                          </h4>
                          <span className="rounded-md bg-emerald-500/10 px-2 py-0.5 text-2xs font-bold text-emerald-700 dark:text-emerald-300">
                            {cr.block} · {cr.floor}
                          </span>
                        </div>
                        <p className="text-xs text-muted mt-0.5 line-clamp-1">{cr.name}</p>
                      </div>

                      <span className="rounded-full bg-surface border border-line px-2 py-0.5 text-[10px] font-bold text-muted shrink-0">
                        {cr.type}
                      </span>
                    </div>

                  {/* Telemetry Box */}
                  <div className="rounded-xl border border-line/60 bg-surface/50 p-3 space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-muted">Student Seating</span>
                      <span className="font-bold text-ink">{cr.capacity} Desks</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-muted">Current Activity</span>
                      <span className="font-bold text-emerald-600 line-clamp-1">{cr.currentActivity}</span>
                    </div>
                  </div>

                  {/* Equipment Inventory */}
                  <div className="space-y-1.5">
                    <span className="text-2xs font-bold uppercase tracking-wider text-muted">
                      Equipment Inventory:
                    </span>
                    <div className="flex flex-wrap gap-1.5 text-2xs">
                      {cr.equipment.workstationsCount > 0 && (
                        <span className="inline-flex items-center gap-1 rounded-md bg-surface border border-line/60 px-2 py-0.5 text-ink font-semibold">
                          <Monitor size={10} className="text-brand-500" />
                          <span>{cr.equipment.workstationsCount} PCs</span>
                        </span>
                      )}
                      {cr.equipment.projectorsCount > 0 && (
                        <span className="inline-flex items-center gap-1 rounded-md bg-surface border border-line/60 px-2 py-0.5 text-ink font-semibold">
                          <Tv size={10} className="text-indigo-500" />
                          <span>{cr.equipment.projectorsCount} Laser Projector{cr.equipment.projectorsCount > 1 ? "s" : ""}</span>
                        </span>
                      )}
                      {cr.equipment.hasAC && (
                        <span className="inline-flex items-center gap-1 rounded-md bg-surface border border-line/60 px-2 py-0.5 text-sky-600 font-semibold">
                          <Wind size={10} />
                          <span>AC</span>
                        </span>
                      )}
                      {cr.equipment.hasWifi && (
                        <span className="inline-flex items-center gap-1 rounded-md bg-surface border border-line/60 px-2 py-0.5 text-emerald-600 font-semibold">
                          <Wifi size={10} />
                          <span>Wi-Fi</span>
                        </span>
                      )}
                      {cr.equipment.hasSmartPodium && (
                        <span className="inline-flex items-center gap-1 rounded-md bg-surface border border-line/60 px-2 py-0.5 text-purple-600 font-semibold">
                          <Mic size={10} />
                          <span>Smart Podium</span>
                        </span>
                      )}
                    </div>

                    {cr.equipment.specialGear && (
                      <p className="text-2xs text-amber-700 dark:text-amber-300 font-medium pt-1">
                        ⚡ {cr.equipment.specialGear}
                      </p>
                    )}
                  </div>
                </div>

                {/* Bottom Action Footer */}
                <div className="pt-3 border-t border-line/60">
                  <button
                    onClick={() =>
                      locateOnFloorBlueprint(
                        cr.block === "Engineering Labs"
                          ? "Engineering Labs - Ground Floor"
                          : `${cr.block} - ${cr.floor}`,
                        cr.roomCode
                      )
                    }
                    className="w-full inline-flex items-center justify-center gap-1.5 rounded-xl border border-line bg-surface py-2 text-xs font-bold text-brand-600 hover:border-brand-500 transition"
                  >
                    <Compass size={13} />
                    <span>View on Vector Blueprint</span>
                  </button>
                </div>
              </div>
            ))}
            </div>
          </div>
        </div>
      )}

      {/* ================= TAB 4: LIBRARY INTELLIGENCE ================= */}
      {activeTab === "library" && (
        <div className="space-y-6 animate-in fade-in duration-200">
          {/* Real-Time Silent Study Seat Telemetry Banner */}
          <div className="rounded-3xl border border-amber-500/40 bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent p-6 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-6">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
                  <h3 className="text-base font-extrabold text-ink">
                    Central University Library Live Intelligence
                  </h3>
                  <span className="rounded-full bg-emerald-500/15 px-2.5 py-0.5 text-2xs font-extrabold text-emerald-600">
                    Live Optical Counters
                  </span>
                </div>
                <p className="text-xs text-muted">
                  Silent Study Wing Portico · Hours: <strong className="text-ink">{LIBRARY_INTELLIGENCE.openingHours}</strong> · Librarian: {LIBRARY_INTELLIGENCE.librarianOnDuty}
                </p>
              </div>

              {/* Live Gauges */}
              <div className="flex items-center gap-4">
                <div className="rounded-2xl border border-line bg-panel p-3.5 text-center min-w-[130px] shadow-xs">
                  <span className="text-2xs text-muted block uppercase font-bold tracking-wider">
                    Silent Desks
                  </span>
                  <span className="font-mono font-extrabold text-xl text-emerald-600">
                    {LIBRARY_INTELLIGENCE.availableSilentSeats} / {LIBRARY_INTELLIGENCE.totalSilentSeats}
                  </span>
                  <span className="text-[10px] text-muted block mt-0.5">Seats Free Right Now</span>
                </div>

                <div className="rounded-2xl border border-line bg-panel p-3.5 text-center min-w-[130px] shadow-xs">
                  <span className="text-2xs text-muted block uppercase font-bold tracking-wider">
                    Study Pods
                  </span>
                  <span className="font-mono font-extrabold text-xl text-brand-600">
                    {LIBRARY_INTELLIGENCE.collaborativePodsAvailable} / {LIBRARY_INTELLIGENCE.collaborativePodsTotal}
                  </span>
                  <span className="text-[10px] text-muted block mt-0.5">Rooms Available</span>
                </div>
              </div>
            </div>
          </div>

          {/* Digital Catalog Search */}
          <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs space-y-4">
            <div className="relative">
              <input
                type="text"
                placeholder="Search digital book catalog by title, author, or ISBN (e.g. Compilers Dragon Book, Operating Systems, CLRS, Deep Learning)..."
                value={libraryQuery}
                onChange={(e) => setLibraryQuery(e.target.value)}
                className="w-full rounded-xl border border-line bg-surface px-3 py-2.5 pl-9 text-xs text-ink placeholder:text-muted focus:outline-hidden focus:ring-2 focus:ring-amber-500"
              />
              <Search size={14} className="absolute left-3 top-3 text-muted" />
              {libraryQuery && (
                <button onClick={() => setLibraryQuery("")} className="absolute right-3 top-3 text-muted hover:text-ink">
                  <X size={12} />
                </button>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-line/60">
              <span className="text-2xs font-bold uppercase tracking-wider text-muted mr-1">
                Category:
              </span>
              {["All", "Computer Science", "Mathematics", "Electrical Eng", "Management Sciences"].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setLibraryCategoryFilter(cat)}
                  className={`rounded-xl px-3 py-1.5 text-xs font-semibold transition border ${
                    libraryCategoryFilter === cat
                      ? "border-amber-600 bg-amber-600 text-white font-bold shadow-xs"
                      : "border-line bg-surface text-muted hover:text-ink"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>

          {/* Book Catalog Grid */}
          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {filteredBooks.map((book) => (
              <div
                key={book.id}
                className="rounded-3xl border border-line bg-panel p-5 shadow-2xs space-y-4 flex flex-col justify-between hover:border-amber-500/60 transition group"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <span className="rounded-md bg-amber-500/10 px-2 py-0.5 text-2xs font-bold text-amber-700 dark:text-amber-300">
                      {book.category}
                    </span>
                    <span
                      className={`rounded-full px-2 py-0.5 text-2xs font-bold ${
                        book.isAvailable
                          ? "bg-emerald-500/15 text-emerald-600"
                          : "bg-rose-500/15 text-rose-600"
                      }`}
                    >
                      {book.isAvailable ? `${book.availableCopies} Available` : "All Checked Out"}
                    </span>
                  </div>

                  <div>
                    <h4 className="font-extrabold text-sm text-ink group-hover:text-amber-600 transition leading-snug">
                      {book.title}
                    </h4>
                    <p className="text-xs text-muted mt-0.5">{book.authors}</p>
                    <p className="text-2xs text-muted italic mt-0.5">{book.edition}</p>
                  </div>

                  {/* Shelf Location Box */}
                  <div className="rounded-xl border border-line/60 bg-surface/50 p-2.5 space-y-1 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-muted flex items-center gap-1">
                        <MapPin size={11} className="text-amber-500" />
                        <span>Shelf Location:</span>
                      </span>
                      <span className="font-mono font-bold text-ink">{book.shelfLocation}</span>
                    </div>
                    <div className="flex items-center justify-between text-2xs text-muted">
                      <span>ISBN: {book.isbn}</span>
                      <span>Total Copies: {book.totalCopies}</span>
                    </div>
                  </div>
                </div>

                {/* Bottom Action Footer */}
                <div className="pt-3 border-t border-line/60 flex items-center gap-2">
                  <button
                    onClick={() => {
                      setReservedBook(book);
                      setBookReservedSuccess(false);
                    }}
                    disabled={!book.isAvailable}
                    className="flex-1 rounded-xl bg-amber-600 py-2 text-xs font-bold text-white hover:bg-amber-700 transition disabled:opacity-50 shadow-xs"
                  >
                    Reserve Copy
                  </button>
                  {book.digitalPdfAvailable && (
                    <button
                      onClick={() => alert(`Opening digital IEEE / Springer academic e-book link for "${book.title}"...`)}
                      className="rounded-xl border border-line bg-surface p-2 text-muted hover:text-ink hover:border-brand-500 transition"
                      title="Open Digital PDF / IEEE e-book"
                    >
                      <ExternalLink size={14} />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ================= TAB 5: INTERACTIVE FLOOR PLANS & SPATIAL BLUEPRINTS ================= */}
      {activeTab === "floorplans" && (
        <div className="space-y-6 animate-in fade-in duration-200">
          {/* Blueprint Selector Bar */}
          <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs flex flex-wrap items-center justify-between gap-4">
            <div>
              <label className="block text-xs font-bold text-ink mb-1.5 flex items-center gap-1.5">
                <Compass size={14} className="text-purple-600" />
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
                        ? "border-purple-600 bg-purple-600 text-white shadow-xs"
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
                <span className="rounded-md bg-purple-500/10 px-2.5 py-1 text-2xs font-bold text-purple-600">
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
                            ? "border-purple-600 bg-purple-600/15 ring-2 ring-purple-500/60 shadow-md scale-[1.02]"
                            : room.type === "classroom"
                            ? "border-line bg-panel hover:border-purple-500/60 hover:bg-surface"
                            : room.type === "office"
                            ? "border-indigo-500/30 bg-indigo-500/5 hover:border-indigo-500"
                            : room.type === "lab"
                            ? "border-emerald-500/30 bg-emerald-500/5 hover:border-emerald-500"
                            : "border-line/60 bg-surface/80 opacity-75"
                        }`}
                      >
                        {isSelected && (
                          <span className="inline-flex items-center gap-1 text-[10px] font-extrabold text-purple-600 animate-pulse">
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
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-500/10 text-purple-600">
                    <Compass size={20} />
                  </div>
                  <div>
                    <h4 className="font-extrabold text-sm text-ink">Turn-by-Turn Walking Directions</h4>
                    <p className="text-2xs text-muted">From Campus Main Entrance Gate 1</p>
                  </div>
                </div>

                {highlightedRoomCode ? (
                  <div className="space-y-4">
                    <div className="rounded-2xl border border-purple-500/40 bg-purple-500/10 p-4 space-y-1">
                      <span className="text-2xs font-extrabold text-purple-600 uppercase tracking-wider">
                        Destination Target
                      </span>
                      <h4 className="font-extrabold text-base text-ink">{highlightedRoomCode}</h4>
                      <p className="text-xs text-muted">
                        {activeBlueprint.block} · {activeBlueprint.floor}
                      </p>
                    </div>

                    <div className="space-y-3 relative pl-5 border-l-2 border-purple-500/40 text-xs">
                      <div className="relative">
                        <span className="absolute -left-[25px] top-1 h-3 w-3 rounded-full bg-purple-600 ring-4 ring-panel" />
                        <strong className="text-ink block">Step 1: Arrive at Sector Arch</strong>
                        <p className="text-2xs text-muted mt-0.5">
                          Walk past the Central Fountain towards {activeBlueprint.block} Portico entrance.
                        </p>
                      </div>

                      <div className="relative">
                        <span className="absolute -left-[25px] top-1 h-3 w-3 rounded-full bg-purple-600 ring-4 ring-panel" />
                        <strong className="text-ink block">Step 2: Ascend to {activeBlueprint.floor}</strong>
                        <p className="text-2xs text-muted mt-0.5">
                          Take the West Wing Elevator or Central Fire Staircase to {activeBlueprint.floor}.
                        </p>
                      </div>

                      <div className="relative">
                        <span className="absolute -left-[25px] top-1 h-3 w-3 rounded-full bg-emerald-500 ring-4 ring-panel" />
                        <strong className="text-emerald-700 dark:text-emerald-300 block">
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
                <span className="text-emerald-600 font-bold">100% Barrier-Free Access</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ================= MEETING REQUEST MODAL ================= */}
      {meetingModalFaculty && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
          <div className="w-full max-w-md rounded-3xl border border-line bg-panel p-6 shadow-2xl space-y-5 animate-in zoom-in-95 duration-200">
            <div className="flex items-start justify-between">
              <div>
                <span className="rounded-full bg-brand-500/10 px-2.5 py-0.5 text-2xs font-extrabold text-brand-600 uppercase">
                  Faculty Consultation Request
                </span>
                <h3 className="font-extrabold text-base text-ink mt-1">
                  Meet with {meetingModalFaculty.name}
                </h3>
                <p className="text-xs text-muted">
                  {meetingModalFaculty.designation} · {meetingModalFaculty.officeRoom}
                </p>
              </div>
              <button onClick={() => setMeetingModalFaculty(null)} className="rounded-xl p-1.5 text-muted hover:text-ink">
                <X size={16} />
              </button>
            </div>

            {meetingSubmitted ? (
              <div className="rounded-2xl border border-emerald-500/40 bg-emerald-500/10 p-5 text-center space-y-2">
                <div className="inline-flex items-center gap-1.5 text-xs font-extrabold text-emerald-600">
                  <CheckCircle2 size={18} />
                  <span>Consultation Request Dispatched!</span>
                </div>
                <p className="text-2xs text-emerald-700 dark:text-emerald-300">
                  Confirmation sent to {meetingModalFaculty.email}. An invite will appear on your Student Timetable once accepted.
                </p>
                <button
                  onClick={() => setMeetingModalFaculty(null)}
                  className="rounded-xl bg-emerald-600 px-4 py-2 text-xs font-bold text-white hover:bg-emerald-700 mt-2"
                >
                  Done
                </button>
              </div>
            ) : (
              <div className="space-y-4 text-xs">
                <div>
                  <label className="block font-bold text-ink mb-1">Consultation Window</label>
                  <div className="rounded-xl border border-line bg-surface p-2.5 font-semibold text-ink flex items-center justify-between text-2xs">
                    <span>{meetingModalFaculty.consultationHours}</span>
                    <span className="text-brand-600 font-bold">Standard Slots</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block font-bold text-ink mb-1">Preferred Day</label>
                    <select
                      value={meetingDate}
                      onChange={(e) => setMeetingDate(e.target.value)}
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
                    <label className="block font-bold text-ink mb-1">Preferred Time</label>
                    <select
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
                  <label className="block font-bold text-ink mb-1">Discussion Topic / Purpose</label>
                  <textarea
                    rows={3}
                    placeholder="Describe discussion topic (e.g. FYP Proposal Guidance, Midterm Exam Rechecking, Course Advising)..."
                    value={meetingPurpose}
                    onChange={(e) => setMeetingPurpose(e.target.value)}
                    className="w-full rounded-xl border border-line bg-surface p-2.5 text-xs text-ink placeholder:text-muted focus:outline-hidden focus:ring-2 focus:ring-brand-500"
                  />
                </div>

                <div className="flex items-center justify-end gap-2 pt-2 border-t border-line/60">
                  <button
                    onClick={() => setMeetingModalFaculty(null)}
                    className="rounded-xl border border-line bg-surface px-4 py-2 text-xs font-bold text-muted hover:text-ink"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => setMeetingSubmitted(true)}
                    disabled={!meetingPurpose.trim()}
                    className="rounded-xl bg-brand-600 px-5 py-2 text-xs font-bold text-white hover:bg-brand-700 disabled:opacity-50"
                  >
                    Submit Request
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ================= VIRTUAL QUEUE TICKET MODAL ================= */}
      {virtualTicketOffice && myTicketNumber && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
          <div className="w-full max-w-sm rounded-3xl border border-line bg-panel p-6 shadow-2xl text-center space-y-5 animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between text-left">
              <div>
                <h4 className="font-extrabold text-sm text-ink">{virtualTicketOffice.name}</h4>
                <p className="text-2xs text-muted">{virtualTicketOffice.officeRoom}</p>
              </div>
              <button onClick={() => setVirtualTicketOffice(null)} className="rounded-xl p-1 text-muted hover:text-ink">
                <X size={16} />
              </button>
            </div>

            <div className="rounded-2xl border-2 border-dashed border-indigo-500/40 bg-surface/80 p-6 space-y-3">
              <span className="text-2xs font-extrabold text-muted uppercase tracking-wider">
                Your Priority Ticket
              </span>
              <div className="font-mono font-black text-4xl text-indigo-600">
                #{myTicketNumber}
              </div>
              <p className="text-2xs text-muted">
                Currently Serving: <strong className="text-ink">#{virtualTicketOffice.currentTicketServing}</strong>
              </p>
              <div className="rounded-xl bg-panel border border-line p-2 text-2xs text-indigo-700 dark:text-indigo-300 font-semibold">
                Est. Waiting Time: ~{virtualTicketOffice.avgWaitMinutes + 4} minutes
              </div>
            </div>

            <p className="text-2xs text-muted">
              We'll notify your student portal when token #{myTicketNumber} is called at the counter.
            </p>

            <button
              onClick={() => setVirtualTicketOffice(null)}
              className="w-full rounded-xl bg-indigo-600 py-2.5 text-xs font-bold text-white hover:bg-indigo-700 transition"
            >
              Keep Ticket in Wallet
            </button>
          </div>
        </div>
      )}

      {/* ================= BOOK RESERVATION MODAL ================= */}
      {reservedBook && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
          <div className="w-full max-w-md rounded-3xl border border-line bg-panel p-6 shadow-2xl space-y-5 animate-in zoom-in-95 duration-200">
            <div className="flex items-start justify-between">
              <div>
                <span className="rounded-full bg-amber-500/10 px-2.5 py-0.5 text-2xs font-extrabold text-amber-700 dark:text-amber-300 uppercase">
                  Library Circulation Desk
                </span>
                <h3 className="font-extrabold text-base text-ink mt-1">Reserve Book Copy</h3>
              </div>
              <button onClick={() => setReservedBook(null)} className="rounded-xl p-1 text-muted hover:text-ink">
                <X size={16} />
              </button>
            </div>

            {bookReservedSuccess ? (
              <div className="rounded-2xl border border-emerald-500/40 bg-emerald-500/10 p-5 text-center space-y-2">
                <CheckCircle2 size={22} className="mx-auto text-emerald-600" />
                <h4 className="font-bold text-sm text-ink">Copy Held at Circulation Desk!</h4>
                <p className="text-2xs text-muted">
                  A physical copy of "{reservedBook.title}" will be held under your Reg No at {reservedBook.shelfLocation} for 24 hours.
                </p>
                <button
                  onClick={() => setReservedBook(null)}
                  className="rounded-xl bg-emerald-600 px-5 py-2 text-xs font-bold text-white hover:bg-emerald-700 mt-2"
                >
                  Close
                </button>
              </div>
            ) : (
              <div className="space-y-4 text-xs">
                <div className="rounded-2xl border border-line bg-surface p-3.5 space-y-1">
                  <h4 className="font-bold text-ink">{reservedBook.title}</h4>
                  <p className="text-2xs text-muted">{reservedBook.authors} · {reservedBook.edition}</p>
                  <p className="text-2xs font-mono text-amber-600 pt-1">Location: {reservedBook.shelfLocation}</p>
                </div>

                <div className="rounded-xl border border-line/60 bg-panel p-3 text-2xs text-muted space-y-1">
                  <p className="font-bold text-ink">Circulation Policy:</p>
                  <p>• Standard borrowing period: 14 days with 1-click renewal online.</p>
                  <p>• Overdue fine: PKR 10/day after grace period.</p>
                </div>

                <div className="flex items-center justify-end gap-2 pt-2 border-t border-line/60">
                  <button
                    onClick={() => setReservedBook(null)}
                    className="rounded-xl border border-line bg-surface px-4 py-2 text-xs font-bold text-muted hover:text-ink"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => setBookReservedSuccess(true)}
                    className="rounded-xl bg-amber-600 px-5 py-2 text-xs font-bold text-white hover:bg-amber-700"
                  >
                    Confirm 24h Desk Hold
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
