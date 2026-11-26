import { useState, useEffect, useMemo } from "react";
import {
  GraduationCap,
  BookOpen,
  Calendar,
  Clock,
  MapPin,
  Users,
  UserCheck,
  Download,
  LayoutGrid,
  List,
  Search,
  X,
  AlertTriangle,
  Check,
  ChevronRight
} from "lucide-react";

import {
  STUDENT_TIMETABLES_BY_SECTION,
  TEACHER_TIMETABLES_BY_NAME,
  downloadICSFile,
  type TimetableSlot
} from "../../features/timetable/timetable-engine";
import { TimetableTableView, TimetableSlotModal } from "./IntelligentTimetableEngine";

type Weekday = TimetableSlot["day"];

const WEEKDAYS: Weekday[] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
const SHORT_DAY: Record<Weekday, string> = {
  Monday: "Mon",
  Tuesday: "Tue",
  Wednesday: "Wed",
  Thursday: "Thu",
  Friday: "Fri"
};

function getTodayWeekday(now: Date): Weekday | null {
  const map: Record<number, Weekday> = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday"
  };
  return map[now.getDay()] ?? null;
}

function parseMinutes(hhmm: string): number {
  const [h, m] = hhmm.split(":").map(Number);
  return (h || 0) * 60 + (m || 0);
}

interface TimetableHubProps {
  initialRole?: "student" | "teacher";
  signedInRole?: "student" | "teacher" | null;
}

export function TimetableHub({
  initialRole = "student",
  signedInRole = null
}: TimetableHubProps) {
  const [selectedRole, setSelectedRole] = useState<"student" | "teacher">(initialRole);
  const [selectedSection, setSelectedSection] = useState<string>("BCS-7C");
  const [selectedTeacher, setSelectedTeacher] = useState<string>("Sir Munir (Dr. Munir Ahmad)");
  const [viewStyle, setViewStyle] = useState<"list" | "table">("list");
  const [selectedDay, setSelectedDay] = useState<"All Days" | Weekday>("All Days");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [activeModalSlot, setActiveModalSlot] = useState<TimetableSlot | null>(null);

  const [now, setNow] = useState<Date>(() => new Date());
  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  const sectionNames = Object.keys(STUDENT_TIMETABLES_BY_SECTION);
  const teacherNames = Object.keys(TEACHER_TIMETABLES_BY_NAME);

  const activeSchedule: TimetableSlot[] = useMemo(() => {
    return selectedRole === "student"
      ? STUDENT_TIMETABLES_BY_SECTION[selectedSection] ?? []
      : TEACHER_TIMETABLES_BY_NAME[selectedTeacher] ?? [];
  }, [selectedRole, selectedSection, selectedTeacher]);

  const filteredSchedule = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return activeSchedule;
    return activeSchedule.filter((slot) => {
      return (
        slot.courseTitle.toLowerCase().includes(q) ||
        slot.courseCode.toLowerCase().includes(q) ||
        slot.instructorName.toLowerCase().includes(q) ||
        slot.room.toLowerCase().includes(q) ||
        slot.block.toLowerCase().includes(q) ||
        slot.section.toLowerCase().includes(q)
      );
    });
  }, [activeSchedule, searchQuery]);

  const todayWeekday = getTodayWeekday(now);
  const nowMinutes = now.getHours() * 60 + now.getMinutes();

  const { liveSlot, nextTodaySlot } = useMemo(() => {
    if (!todayWeekday) return { liveSlot: null, nextTodaySlot: null };
    const todaySlots = activeSchedule
      .filter((s) => s.day === todayWeekday)
      .sort((a, b) => a.slotNumber - b.slotNumber);

    const running =
      todaySlots.find(
        (s) => nowMinutes >= parseMinutes(s.startTime) && nowMinutes <= parseMinutes(s.endTime)
      ) ?? null;

    const upcoming =
      todaySlots.find((s) => parseMinutes(s.startTime) > nowMinutes) ?? null;

    return { liveSlot: running, nextTodaySlot: upcoming };
  }, [activeSchedule, todayWeekday, nowMinutes]);

  const visibleDays: Weekday[] =
    viewStyle === "list" && selectedDay !== "All Days" ? [selectedDay] : WEEKDAYS;

  const swapAlerts = useMemo(() => {
    const pool =
      viewStyle === "list" && selectedDay !== "All Days"
        ? filteredSchedule.filter((s) => s.day === selectedDay)
        : filteredSchedule;
    return pool.filter((s) => Boolean(s.swapAlert));
  }, [filteredSchedule, viewStyle, selectedDay]);

  const totalWeeklyLectures = activeSchedule.length;

  const handleRoleSwitch = (nextRole: "student" | "teacher") => {
    setSelectedRole(nextRole);
    setSearchQuery("");
  };

  const handleSaveCalendar = () => {
    const fileLabel =
      selectedRole === "student"
        ? `${selectedSection}_Timetable.ics`
        : `${selectedTeacher.replace(/[^a-zA-Z0-9]+/g, "_")}_Timetable.ics`;
    downloadICSFile(activeSchedule, fileLabel);
  };

  return (
    <div className="space-y-4">
      {/* ================= 1. STUDENT OR TEACHER PICKER ================= */}
      <div className="grid grid-cols-2 gap-3 sm:gap-4" role="group" aria-label="Choose schedule view">
        <button
          type="button"
          aria-pressed={selectedRole === "student"}
          onClick={() => handleRoleSwitch("student")}
          className={`flex items-center justify-between gap-2.5 rounded-2xl border p-3.5 sm:p-4 text-left transition shadow-2xs cursor-pointer ${
            selectedRole === "student"
              ? "border-primary bg-panel ring-2 ring-primary/25 shadow-sm"
              : "border-line bg-panel hover:border-primary/50"
          }`}
        >
          <div className="flex items-center gap-3 min-w-0">
            <span
              className={`flex h-10 w-10 sm:h-11 sm:w-11 shrink-0 items-center justify-center rounded-xl transition ${
                selectedRole === "student"
                  ? "bg-primary text-on-primary"
                  : "bg-primary-soft text-primary-ink"
              }`}
            >
              <GraduationCap size={22} />
            </span>
            <div className="min-w-0">
              <h3 className="font-bold text-sm sm:text-base text-ink leading-tight">Student</h3>
              <p className="hidden sm:block text-xs text-muted mt-0.5 truncate">
                Classes by section (teachers, rooms &amp; seats)
              </p>
            </div>
          </div>

          <span
            className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border transition ${
              selectedRole === "student"
                ? "border-primary bg-primary text-on-primary"
                : "border-line bg-surface text-transparent"
            }`}
            aria-hidden="true"
          >
            <Check size={13} strokeWidth={3} />
          </span>
        </button>

        <button
          type="button"
          aria-pressed={selectedRole === "teacher"}
          onClick={() => handleRoleSwitch("teacher")}
          className={`flex items-center justify-between gap-2.5 rounded-2xl border p-3.5 sm:p-4 text-left transition shadow-2xs cursor-pointer ${
            selectedRole === "teacher"
              ? "border-secondary bg-panel ring-2 ring-secondary/25 shadow-sm"
              : "border-line bg-panel hover:border-secondary/50"
          }`}
        >
          <div className="flex items-center gap-3 min-w-0">
            <span
              className={`flex h-10 w-10 sm:h-11 sm:w-11 shrink-0 items-center justify-center rounded-xl transition ${
                selectedRole === "teacher"
                  ? "bg-secondary text-secondary-fg"
                  : "bg-secondary-soft text-secondary-ink"
              }`}
            >
              <BookOpen size={22} />
            </span>
            <div className="min-w-0">
              <h3 className="font-bold text-sm sm:text-base text-ink leading-tight">Teacher</h3>
              <p className="hidden sm:block text-xs text-muted mt-0.5 truncate">
                Schedule by teacher (classes, rooms &amp; sections)
              </p>
            </div>
          </div>

          <span
            className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border transition ${
              selectedRole === "teacher"
                ? "border-secondary bg-secondary text-secondary-fg"
                : "border-line bg-surface text-transparent"
            }`}
            aria-hidden="true"
          >
            <Check size={13} strokeWidth={3} />
          </span>
        </button>
      </div>

      {/* ================= 2. UNIFIED CONTROLS BAR ================= */}
      <div className="rounded-2xl border border-line bg-panel p-3.5 sm:p-4 shadow-2xs space-y-3">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
          {/* Left: Section Pills or Teacher Selector + Class Count */}
          <div className="flex flex-wrap items-center gap-2.5">
            {selectedRole === "student" ? (
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-bold text-muted">Class / Section:</span>
                <div className="inline-flex flex-wrap gap-1.5" role="group" aria-label="Select class or section">
                  {sectionNames.map((sec) => {
                    const active = selectedSection === sec;
                    return (
                      <button
                        key={sec}
                        type="button"
                        aria-pressed={active}
                        onClick={() => setSelectedSection(sec)}
                        className={`rounded-xl px-3 py-1.5 text-xs font-bold transition cursor-pointer ${
                          active
                            ? "bg-primary text-on-primary shadow-2xs"
                            : "border border-line bg-surface text-ink hover:border-primary/50"
                        }`}
                      >
                        {sec}
                      </button>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto">
                <label htmlFor="tt-teacher-select" className="text-xs font-bold text-muted">
                  Teacher:
                </label>
                <select
                  id="tt-teacher-select"
                  value={selectedTeacher}
                  onChange={(e) => setSelectedTeacher(e.target.value)}
                  className="flex-1 sm:flex-none min-w-[210px] rounded-xl border border-line bg-surface px-3 py-2 text-xs font-bold text-ink focus:outline-hidden focus:ring-2 focus:ring-secondary"
                >
                  {teacherNames.map((tName) => (
                    <option key={tName} value={tName}>
                      {tName}
                    </option>
                  ))}
                </select>
              </div>
            )}

            <span className="rounded-xl border border-line bg-subtle/60 px-3 py-1.5 text-xs font-semibold text-ink">
              {totalWeeklyLectures} {totalWeeklyLectures === 1 ? "lecture" : "lectures"} a week
            </span>
          </div>

          {/* Right: Search + View Mode Switch + Save Calendar */}
          <div className="flex flex-wrap items-center justify-between sm:justify-end gap-2">
            <div className="relative w-full sm:w-56">
              <Search
                size={14}
                className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted"
              />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                aria-label="Search classes by subject, teacher, or room"
                placeholder="Search classes..."
                className="w-full rounded-xl border border-line bg-surface py-1.5 pl-8 pr-7 text-xs text-ink placeholder:text-muted focus:outline-hidden focus:ring-2 focus:ring-primary/40"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  aria-label="Clear search"
                  className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full p-0.5 text-muted hover:text-ink"
                >
                  <X size={13} />
                </button>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-2 w-full sm:w-auto justify-between sm:justify-start">
              <div className="inline-flex rounded-xl border border-line bg-surface p-1 text-xs" role="group" aria-label="Layout view">
                <button
                  type="button"
                  aria-pressed={viewStyle === "list"}
                  onClick={() => setViewStyle("list")}
                  className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 font-semibold transition cursor-pointer ${
                    viewStyle === "list"
                      ? "bg-primary text-on-primary shadow-2xs"
                      : "text-muted hover:text-ink"
                  }`}
                >
                  <List size={13} />
                  <span>List View</span>
                </button>
                <button
                  type="button"
                  aria-pressed={viewStyle === "table"}
                  onClick={() => setViewStyle("table")}
                  className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 font-semibold transition cursor-pointer ${
                    viewStyle === "table"
                      ? "bg-primary text-on-primary shadow-2xs"
                      : "text-muted hover:text-ink"
                  }`}
                >
                  <LayoutGrid size={13} />
                  <span>Table View</span>
                </button>
              </div>

              <button
                type="button"
                onClick={handleSaveCalendar}
                title="Download calendar file for Google, Apple, or Outlook Calendar"
                className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-surface px-3 py-2 text-xs font-bold text-ink hover:border-primary transition cursor-pointer"
              >
                <Download size={13} className="text-primary-ink" />
                <span>Save Calendar</span>
              </button>
            </div>
          </div>
        </div>

        {/* Day Quick Filter Pills (for fast day jumping in List View) */}
        {viewStyle === "list" && (
          <div className="flex items-center gap-1.5 overflow-x-auto pt-2 border-t border-line/70">
            <button
              type="button"
              aria-pressed={selectedDay === "All Days"}
              onClick={() => setSelectedDay("All Days")}
              className={`shrink-0 rounded-xl px-3 py-1.5 text-xs font-semibold transition cursor-pointer ${
                selectedDay === "All Days"
                  ? "bg-primary text-on-primary"
                  : "bg-subtle/60 text-muted hover:text-ink"
              }`}
            >
              All Days ({activeSchedule.length})
            </button>

            {WEEKDAYS.map((day) => {
              const count = activeSchedule.filter((s) => s.day === day).length;
              const isSelected = selectedDay === day;
              const isToday = todayWeekday === day;
              return (
                <button
                  key={day}
                  type="button"
                  aria-pressed={isSelected}
                  onClick={() => setSelectedDay(day)}
                  className={`inline-flex shrink-0 items-center gap-1.5 rounded-xl px-3 py-1.5 text-xs font-semibold transition cursor-pointer ${
                    isSelected
                      ? "bg-primary text-on-primary"
                      : "bg-subtle/60 text-muted hover:text-ink"
                  }`}
                >
                  <span className="sm:hidden">{SHORT_DAY[day]}</span>
                  <span className="hidden sm:inline">{day}</span>
                  {isToday && (
                    <span
                      className={`h-1.5 w-1.5 rounded-full ${
                        isSelected ? "bg-on-primary" : "bg-success"
                      }`}
                      title="Today"
                    />
                  )}
                  <span
                    className={`rounded-full px-1.5 py-0.2 text-[10px] font-bold ${
                      isSelected ? "bg-on-primary/20 text-on-primary" : "bg-panel text-muted"
                    }`}
                  >
                    {count}
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* ================= 3. ACCURATE TODAY & ROOM CHANGE NOTICES ================= */}
      {(liveSlot || nextTodaySlot) && (selectedDay === "All Days" || selectedDay === todayWeekday) && (
        <button
          type="button"
          onClick={() => setActiveModalSlot(liveSlot ?? nextTodaySlot)}
          className="w-full text-left rounded-2xl border border-success/35 bg-success-soft px-4 py-2.5 text-xs text-success-ink flex flex-wrap items-center justify-between gap-2 hover:opacity-95 transition cursor-pointer"
        >
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-success shrink-0" />
            {liveSlot ? (
              <span>
                <strong>Happening Now:</strong> {liveSlot.courseTitle} ({liveSlot.courseCode}) in{" "}
                <strong>{liveSlot.room}</strong> until {liveSlot.timeRange.split("–")[1]?.trim()}
              </span>
            ) : (
              <span>
                <strong>Next Class Today:</strong> {nextTodaySlot!.courseTitle} ({nextTodaySlot!.courseCode}) at{" "}
                <strong>{nextTodaySlot!.timeRange.split("–")[0]?.trim()}</strong> in{" "}
                <strong>{nextTodaySlot!.room}</strong>
              </span>
            )}
          </div>
          <span className="font-bold underline-offset-2 hover:underline">See room details →</span>
        </button>
      )}

      {swapAlerts.map((alertSlot) => (
        <button
          key={`notice-${alertSlot.id}`}
          type="button"
          onClick={() => setActiveModalSlot(alertSlot)}
          className="w-full text-left rounded-2xl border border-warning/35 bg-warning-soft px-4 py-2.5 text-xs text-warning-ink flex items-center justify-between gap-3 hover:opacity-95 transition cursor-pointer"
        >
          <div className="flex flex-1 min-w-0 items-start sm:items-center gap-2">
            <AlertTriangle size={15} className="shrink-0 mt-0.5 sm:mt-0" />
            <span className="leading-snug">
              <strong>
                Room Change Notice ({alertSlot.day}, {alertSlot.timeRange}):
              </strong>{" "}
              {alertSlot.courseTitle} — {alertSlot.swapAlert!.message}
            </span>
          </div>
          <span className="hidden sm:inline-flex rounded-full bg-warning px-2.5 py-0.5 text-[10px] font-bold uppercase text-warning-fg shrink-0">
            Room Changed
          </span>
        </button>
      ))}

      {/* ================= 4. MAIN TIMETABLE CONTENT ================= */}
      {searchQuery.trim() && filteredSchedule.length === 0 ? (
        <div className="rounded-2xl border border-line bg-panel p-8 text-center space-y-3">
          <p className="text-sm font-bold text-ink">
            No classes matched &ldquo;{searchQuery.trim()}&rdquo;
          </p>
          <p className="text-xs text-muted">
            Try searching by subject name, course code, teacher name, or room number.
          </p>
          <button
            type="button"
            onClick={() => setSearchQuery("")}
            className="inline-flex items-center gap-1.5 rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition"
          >
            Clear Search
          </button>
        </div>
      ) : viewStyle === "table" ? (
        <TimetableTableView
          schedule={filteredSchedule}
          mode={selectedRole}
          onSelectSlot={(slot) => setActiveModalSlot(slot)}
        />
      ) : (
        <div className="space-y-4">
          {visibleDays.map((day) => {
            const daySlots = filteredSchedule
              .filter((s) => s.day === day)
              .sort((a, b) => a.slotNumber - b.slotNumber);
            const isToday = todayWeekday === day;

            return (
              <section
                key={day}
                aria-label={`${day} classes`}
                className="rounded-2xl border border-line bg-panel p-4 sm:p-5 shadow-2xs space-y-3"
              >
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-line pb-2.5">
                  <div className="flex items-center gap-2">
                    <Calendar size={16} className="text-primary-ink" />
                    <h3 className="font-bold text-base text-ink">{day}</h3>
                    {isToday && (
                      <span className="rounded-full bg-success-soft px-2 py-0.5 text-2xs font-bold text-success-ink">
                        Today
                      </span>
                    )}
                  </div>
                  <span
                    className={`rounded-full px-3 py-0.5 text-xs font-bold ${
                      daySlots.length > 0
                        ? "bg-primary-soft text-primary-ink"
                        : "bg-surface text-muted border border-line"
                    }`}
                  >
                    {daySlots.length} {daySlots.length === 1 ? "Lecture" : "Lectures"}
                  </span>
                </div>

                {daySlots.length === 0 ? (
                  <div className="flex flex-wrap items-center justify-between gap-2 py-1 text-xs text-muted">
                    <span className="italic">No classes scheduled on {day}.</span>
                    {selectedDay !== "All Days" && (
                      <button
                        type="button"
                        onClick={() => setSelectedDay("All Days")}
                        className="font-bold text-primary-ink hover:underline"
                      >
                        Show all days
                      </button>
                    )}
                  </div>
                ) : (
                  <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                    {daySlots.map((slot) => {
                      const isLive = liveSlot?.id === slot.id;
                      const isNext = !isLive && nextTodaySlot?.id === slot.id;

                      return (
                        <button
                          key={slot.id}
                          type="button"
                          onClick={() => setActiveModalSlot(slot)}
                          className={`w-full text-left cursor-pointer rounded-2xl border p-4 space-y-2.5 transition hover:shadow-sm group ${slot.colorScheme.border} ${slot.colorScheme.bg}`}
                        >
                          <div className="flex flex-wrap items-center justify-between gap-1.5">
                            <div className="flex items-center gap-1.5">
                              <span
                                className={`rounded-md px-2 py-0.5 text-xs font-bold ${slot.colorScheme.badge}`}
                              >
                                Slot {slot.slotNumber}
                              </span>
                              {isLive && (
                                <span className="rounded-full bg-success px-2 py-0.5 text-[10px] font-bold text-success-fg">
                                  Now
                                </span>
                              )}
                              {isNext && (
                                <span className="rounded-full bg-primary px-2 py-0.5 text-[10px] font-bold text-on-primary">
                                  Next
                                </span>
                              )}
                              {slot.swapAlert && (
                                <span className="rounded-full bg-warning-soft border border-warning/35 px-2 py-0.5 text-[10px] font-bold text-warning-ink">
                                  Room Changed
                                </span>
                              )}
                            </div>

                            <span className="text-xs font-semibold text-muted flex items-center gap-1">
                              <Clock size={12} />
                              <span>{slot.timeRange}</span>
                            </span>
                          </div>

                          <div>
                            <p className="text-2xs font-bold text-muted">{slot.courseCode}</p>
                            <h4 className="font-bold text-sm sm:text-base text-ink mt-0.5 leading-snug">
                              {slot.courseTitle}
                            </h4>
                          </div>

                          <div className="space-y-1.5 pt-2 border-t border-line/60 text-xs text-muted">
                            {selectedRole === "student" ? (
                              <p className="flex items-center gap-1.5">
                                <UserCheck size={13} className="text-primary-ink shrink-0" />
                                <span>
                                  Teacher: <strong className="text-ink">{slot.instructorName}</strong>
                                </span>
                              </p>
                            ) : (
                              <p className="flex items-center gap-1.5">
                                <GraduationCap size={13} className="text-secondary-ink shrink-0" />
                                <span>
                                  Section: <strong className="text-ink">{slot.section}</strong>
                                </span>
                              </p>
                            )}

                            <p className="flex items-center gap-1.5">
                              <MapPin size={13} className="text-primary-ink shrink-0" />
                              <span>
                                Classroom: <strong className="text-ink">{slot.room}</strong> ({slot.block}, {slot.floor})
                              </span>
                            </p>

                            <p className="flex items-center gap-1.5">
                              <Users size={13} className="text-success-ink shrink-0" />
                              <span>
                                Class Capacity: <strong className="text-ink">{slot.capacity} students</strong>{" "}
                                <span className="text-2xs">({slot.enrolledStudents} in class)</span>
                              </span>
                            </p>
                          </div>

                          {slot.swapAlert && (
                            <p className="rounded-lg bg-warning-soft/90 border border-warning/30 px-2.5 py-1.5 text-2xs font-medium text-warning-ink">
                              Room changed: {slot.swapAlert.message}
                            </p>
                          )}

                          <div className="flex items-center justify-end gap-1 text-2xs font-bold text-primary-ink opacity-80 group-hover:opacity-100">
                            <span>Class &amp; room details</span>
                            <ChevronRight size={12} />
                          </div>
                        </button>
                      );
                    })}
                  </div>
                )}
              </section>
            );
          })}
        </div>
      )}

      {/* ================= 5. CLASS & ROOM DETAILS MODAL ================= */}
      <TimetableSlotModal
        slot={activeModalSlot}
        mode={selectedRole}
        signedInRole={signedInRole}
        onClose={() => setActiveModalSlot(null)}
      />
    </div>
  );
}
