import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Calendar,
  Clock,
  MapPin,
  Users,
  AlertTriangle,
  Download,
  Share2,
  CalendarDays,
  LayoutGrid,
  Map,
  X,
  ExternalLink,
  ChevronRight,
  Sparkles,
  CheckCircle2,
  ArrowRight,
  ArrowUpRight
} from "lucide-react";

import {
  type TimetableSlot,
  STANDARD_PERIODS,
  downloadICSFile
} from "../../features/timetable/timetable-engine";

interface Props {
  schedule: TimetableSlot[];
  mode: "student" | "teacher";
  title?: string;
  description?: string;
}

export function IntelligentTimetableEngine({
  schedule,
  mode,
  title = "Intelligent Timetable & Schedule Engine",
  description = "Adaptive timeline, weekly block matrix, real-time room swap alerts, and 1-click calendar sync."
}: Props) {
  const [viewMode, setViewMode] = useState<"day_timeline" | "weekly_matrix">("day_timeline");
  const [selectedDay, setSelectedDay] = useState<"Monday" | "Tuesday" | "Wednesday" | "Thursday" | "Friday">("Wednesday");
  const [selectedRoomModal, setSelectedRoomModal] = useState<TimetableSlot | null>(null);

  // Current time position indicator (08:00 AM to 05:30 PM = 570 minutes total window)
  const [currentTimeMinutes, setCurrentTimeMinutes] = useState(() => {
    const now = new Date();
    return now.getHours() * 60 + now.getMinutes();
  });

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      setCurrentTimeMinutes(now.getHours() * 60 + now.getMinutes());
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  const daySchedule = schedule.filter((s) => s.day === selectedDay).sort((a, b) => a.slotNumber - b.slotNumber);
  const activeSwaps = schedule.filter((s) => s.swapAlert);

  // Compute position for the red line (Window: 08:30 (510 min) to 17:30 (1050 min))
  const startWindow = 8 * 60 + 30; // 08:30
  const endWindow = 17 * 60 + 30;  // 17:30
  const totalWindow = endWindow - startWindow;
  const clampedCurrent = Math.max(startWindow, Math.min(currentTimeMinutes, endWindow));
  const currentLinePercent = ((clampedCurrent - startWindow) / totalWindow) * 100;
  const isWithinClassHours = currentTimeMinutes >= startWindow && currentTimeMinutes <= endWindow;

  // Next lecture computation
  const nextSlot = daySchedule.find((s) => {
    const [h, m] = s.startTime.split(":").map(Number);
    return (h || 0) * 60 + (m || 0) > currentTimeMinutes;
  }) || daySchedule[0];

  const handleExportGoogle = () => {
    if (!nextSlot) return;
    const titleEnc = encodeURIComponent(`${nextSlot.courseCode}: ${nextSlot.courseTitle} (${nextSlot.section})`);
    const detailsEnc = encodeURIComponent(`Instructor: ${nextSlot.instructorName}\nClassroom: ${nextSlot.room} (${nextSlot.block}, ${nextSlot.floor})`);
    const locEnc = encodeURIComponent(`${nextSlot.room}, ${nextSlot.block}, COMSATS Sahiwal`);
    const url = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${titleEnc}&details=${detailsEnc}&location=${locEnc}`;
    window.open(url, "_blank");
  };

  return (
    <div className="space-y-6">
      {/* ================= 1. TIMETABLE CONTROLS & EXPORT TOOLBAR ================= */}
      <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="rounded-md bg-brand-500/10 px-2 py-0.5 text-xs font-bold text-brand-600">
                {mode === "student" ? "Student Timetable" : "Faculty Timetable"}
              </span>
              <span className="text-xs font-medium text-muted">Spring / Fall 2026</span>
            </div>
            <h2 className="text-xl font-black text-ink tracking-tight mt-1">{title}</h2>
            <p className="text-xs text-muted">{description}</p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {/* View Mode Toggle */}
            <div className="flex rounded-xl border border-line bg-surface p-1 text-xs">
              <button
                type="button"
                onClick={() => setViewMode("day_timeline")}
                className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-bold transition ${
                  viewMode === "day_timeline"
                    ? "bg-brand-600 text-white shadow-2xs"
                    : "text-muted hover:text-ink"
                }`}
              >
                <Clock size={14} />
                <span>Day Timeline</span>
              </button>
              <button
                type="button"
                onClick={() => setViewMode("weekly_matrix")}
                className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 font-bold transition ${
                  viewMode === "weekly_matrix"
                    ? "bg-brand-600 text-white shadow-2xs"
                    : "text-muted hover:text-ink"
                }`}
              >
                <LayoutGrid size={14} />
                <span>Weekly Matrix</span>
              </button>
            </div>

            {/* Calendar Sync Dropdown */}
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => downloadICSFile(schedule, `${mode}_schedule.ics`)}
                className="inline-flex items-center gap-1.5 rounded-xl border border-line bg-panel px-3 py-2 text-xs font-bold text-ink hover:border-brand-500 transition shadow-2xs"
                title="Export .ics file for Apple Calendar & Outlook"
              >
                <Download size={14} className="text-brand-600" />
                <span>Export .ics</span>
              </button>
              <button
                type="button"
                onClick={handleExportGoogle}
                className="inline-flex items-center gap-1.5 rounded-xl bg-brand-600 px-3 py-2 text-xs font-bold text-white shadow-xs hover:bg-brand-700 transition"
                title="Add to Google Calendar"
              >
                <CalendarDays size={14} />
                <span>Google Calendar</span>
              </button>
            </div>
          </div>
        </div>

        {/* Real-Time Swap Alert Notification Bar */}
        {activeSwaps.length > 0 && (
          <div className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-3 text-xs text-amber-900 dark:text-amber-200 flex items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <AlertTriangle size={16} className="text-amber-600 shrink-0" />
              <span>
                <strong>Live Schedule Notice:</strong> {activeSwaps[0]?.swapAlert?.message}
              </span>
            </div>
            <span className="rounded-full bg-amber-600 px-2 py-0.5 text-[10px] font-bold uppercase text-white shrink-0">
              Room Swapped
            </span>
          </div>
        )}

        {/* Day Selector Tabs (for Day Timeline) */}
        {viewMode === "day_timeline" && (
          <div className="flex flex-wrap items-center justify-between gap-2 border-t border-line/60 pt-3">
            <div className="flex flex-wrap gap-1.5">
              {(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"] as const).map((day) => {
                const isSelected = selectedDay === day;
                const count = schedule.filter((s) => s.day === day).length;
                return (
                  <button
                    key={day}
                    onClick={() => setSelectedDay(day)}
                    className={`inline-flex items-center gap-1.5 rounded-xl px-3.5 py-1.5 text-xs font-bold transition ${
                      isSelected
                        ? "bg-brand-600 text-white shadow-xs"
                        : "bg-surface text-muted hover:text-ink hover:bg-panel border border-line"
                    }`}
                  >
                    <span>{day}</span>
                    <span
                      className={`rounded-full px-1.5 py-0.2 text-[10px] font-mono ${
                        isSelected ? "bg-white/20 text-white" : "bg-panel text-muted"
                      }`}
                    >
                      {count}
                    </span>
                  </button>
                );
              })}
            </div>

            {nextSlot && (
              <div className="text-xs text-muted flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
                <span>
                  Next on {selectedDay}: <strong>{nextSlot.courseCode}</strong> in <strong>{nextSlot.room}</strong> ({nextSlot.timeRange.split("–")[0]?.trim()})
                </span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* ================= 2. DAY TIMELINE VIEWPORT ================= */}
      {viewMode === "day_timeline" && (
        <div className="rounded-2xl border border-line bg-panel p-6 shadow-2xs space-y-6 relative">
          <div className="flex items-center justify-between border-b border-line pb-3">
            <div>
              <h3 className="font-bold text-base text-ink">{selectedDay}'s Visual Lecture Timeline</h3>
              <p className="text-xs text-muted">Chronological slots with classroom location, faculty, and room occupancy.</p>
            </div>
            {isWithinClassHours && (
              <div className="inline-flex items-center gap-1.5 rounded-full bg-red-500/10 px-2.5 py-0.5 text-xs font-bold text-danger">
                <span className="h-1.5 w-1.5 rounded-full bg-danger animate-pulse" />
                <span>Live Time Indicator Active</span>
              </div>
            )}
          </div>

          {/* Timeline Container */}
          <div className="relative space-y-4">
            {/* Moving Red Current Time Line */}
            {isWithinClassHours && (
              <div
                className="absolute left-0 right-0 z-20 flex items-center pointer-events-none transition-all duration-1000"
                style={{ top: `${Math.max(4, Math.min(currentLinePercent, 96))}%` }}
              >
                <span className="rounded-r-md bg-danger px-1.5 py-0.5 font-mono text-[10px] font-bold text-white shadow-xs">
                  NOW
                </span>
                <div className="flex-1 h-0.5 bg-danger shadow-xs" />
              </div>
            )}

            {daySchedule.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-line p-10 text-center text-muted text-xs space-y-2">
                <Calendar size={32} className="mx-auto text-muted/60" />
                <p className="font-bold text-ink">No lectures scheduled for {selectedDay}</p>
                <p>Enjoy your study and research day!</p>
              </div>
            ) : (
              daySchedule.map((slot) => {
                const occupancyPct = Math.round((slot.enrolledStudents / slot.capacity) * 100);
                return (
                  <div
                    key={slot.id}
                    className={`rounded-2xl border ${slot.colorScheme.border} ${slot.colorScheme.bg} p-5 space-y-3 transition shadow-2xs hover:shadow-md`}
                  >
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className={`font-mono text-xs font-black px-2 py-0.5 rounded-md ${slot.colorScheme.badge}`}>
                            {slot.courseCode}
                          </span>
                          <span className="text-xs font-bold text-ink bg-panel px-2 py-0.5 rounded-md border border-line">
                            {slot.timeRange} (Slot {slot.slotNumber})
                          </span>
                          <span className="text-xs font-medium text-muted">
                            Section: <strong>{slot.section}</strong>
                          </span>
                          {slot.swapAlert && (
                            <span className="rounded-full bg-amber-500/20 text-amber-700 dark:text-amber-300 px-2 py-0.5 text-[10px] font-bold uppercase">
                              🔄 Swapped
                            </span>
                          )}
                        </div>

                        <h4 className="font-bold text-base text-ink mt-1.5">{slot.courseTitle}</h4>

                        <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-muted">
                          <span>
                            Instructor: <strong>{slot.instructorName}</strong> ({slot.instructorOffice})
                          </span>
                          <span>·</span>
                          <button
                            type="button"
                            onClick={() => setSelectedRoomModal(slot)}
                            className="inline-flex items-center gap-1 font-semibold text-brand-600 hover:underline"
                          >
                            <MapPin size={13} />
                            <span>
                              {slot.room} ({slot.block}, {slot.floor})
                            </span>
                          </button>
                        </div>
                      </div>

                      <div className="flex flex-col sm:flex-row sm:items-center gap-3 self-start md:self-auto">
                        {/* Room Capacity Headcount */}
                        <div className="rounded-xl border border-line bg-panel px-3 py-2 text-xs text-right min-w-[140px]">
                          <div className="flex items-center justify-between gap-2 text-[11px] text-muted">
                            <span>Occupancy</span>
                            <span className="font-bold text-ink font-mono">{occupancyPct}%</span>
                          </div>
                          <div className="h-1.5 w-full bg-surface rounded-full overflow-hidden mt-1">
                            <div
                              className={`h-full rounded-full ${occupancyPct > 90 ? "bg-amber-500" : "bg-emerald-500"}`}
                              style={{ width: `${Math.min(occupancyPct, 100)}%` }}
                            />
                          </div>
                          <p className="text-[10px] text-muted mt-1 font-mono">
                            {slot.enrolledStudents} enrolled / {slot.capacity} max
                          </p>
                        </div>

                        {/* Mode Specific Quick Actions */}
                        {mode === "student" ? (
                          <Link
                            to={`/app/student/courses/${slot.courseCode.toLowerCase().replace(/[^a-z0-9]/g, "")}`}
                            className="inline-flex items-center gap-1 rounded-xl bg-panel px-3 py-2 text-xs font-bold text-brand-600 border border-line hover:border-brand-500 transition shadow-2xs"
                          >
                            <span>Coursework</span>
                            <ArrowRight size={13} />
                          </Link>
                        ) : (
                          <Link
                            to="/app/teacher/attendance"
                            className="inline-flex items-center gap-1 rounded-xl bg-emerald-600 px-3 py-2 text-xs font-bold text-white shadow-xs hover:bg-emerald-700 transition"
                          >
                            <span>Mark Attendance</span>
                            <CheckCircle2 size={13} />
                          </Link>
                        )}
                      </div>
                    </div>

                    {slot.swapAlert && (
                      <div className="rounded-lg bg-surface/80 p-2.5 text-xs text-muted border-l-2 border-amber-500">
                        <strong>Swap Note:</strong> {slot.swapAlert.message}
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}

      {/* ================= 3. WEEKLY MATRIX VIEWPORT ================= */}
      {viewMode === "weekly_matrix" && (
        <div className="rounded-2xl border border-line bg-panel p-6 shadow-2xs space-y-4 overflow-x-auto">
          <div>
            <h3 className="font-bold text-base text-ink">Weekly Master Schedule Matrix</h3>
            <p className="text-xs text-muted">Complete block schedule across all 5 lecture slots and 5 academic days.</p>
          </div>

          <div className="min-w-[760px] rounded-xl border border-line overflow-hidden">
            <table className="w-full text-xs text-left">
              <thead className="bg-surface text-muted font-bold border-b border-line">
                <tr>
                  <th className="p-3 w-32">Slot / Time</th>
                  {["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].map((d) => (
                    <th key={d} className="p-3 font-bold text-ink">
                      {d}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-line/60">
                {STANDARD_PERIODS.map((period) => (
                  <tr key={period.slot} className="hover:bg-surface/20">
                    <td className="p-3 bg-surface/40 border-r border-line/60">
                      <p className="font-bold text-ink">{period.label}</p>
                      <p className="text-[10px] text-muted font-mono">{period.time}</p>
                    </td>

                    {(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"] as const).map((day) => {
                      const match = schedule.find((s) => s.day === day && s.slotNumber === period.slot);
                      if (!match) {
                        return (
                          <td key={day} className="p-3 text-muted/50 italic border-r border-line/40">
                            — Free Slot —
                          </td>
                        );
                      }
                      return (
                        <td key={day} className="p-2 border-r border-line/40">
                          <div
                            onClick={() => setSelectedRoomModal(match)}
                            className={`cursor-pointer rounded-xl border ${match.colorScheme.border} ${match.colorScheme.bg} p-2.5 space-y-1 hover:shadow-md transition`}
                          >
                            <span className={`inline-block font-mono text-[10px] font-bold px-1.5 py-0.2 rounded-md ${match.colorScheme.badge}`}>
                              {match.courseCode}
                            </span>
                            <p className="font-bold text-xs text-ink leading-tight">{match.courseTitle}</p>
                            <p className="text-[11px] text-muted">{match.room} · {match.section}</p>
                            <p className="text-[10px] text-brand-600 font-semibold">{match.instructorName.split(" ")[0]} {match.instructorName.split(" ")[1]}</p>
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ================= 4. CAMPUS MAP & ROOM LOCATOR MODAL ================= */}
      {selectedRoomModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs">
          <div className="w-full max-w-lg rounded-3xl border border-line bg-panel p-6 shadow-2xl space-y-4 animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between border-b border-line pb-3">
              <div>
                <span className="font-mono text-xs font-bold text-brand-600">{selectedRoomModal.courseCode}</span>
                <h3 className="font-bold text-base text-ink">{selectedRoomModal.room} Blueprint Locator</h3>
              </div>
              <button
                type="button"
                onClick={() => setSelectedRoomModal(null)}
                className="text-muted hover:text-ink"
              >
                <X size={18} />
              </button>
            </div>

            {/* Simulated Campus Block Map Visualization */}
            <div className="rounded-2xl border border-brand-500/30 bg-surface/80 p-5 space-y-3">
              <div className="flex items-center justify-between text-xs">
                <div>
                  <p className="font-bold text-sm text-ink">{selectedRoomModal.block}</p>
                  <p className="text-muted">{selectedRoomModal.floor} · {selectedRoomModal.room}</p>
                </div>
                <span className="rounded-md bg-brand-500/10 px-2.5 py-1 text-xs font-bold text-brand-600">
                  Capacity: {selectedRoomModal.capacity} Seats
                </span>
              </div>

              {/* Graphical Floor Blueprint */}
              <div className="rounded-xl border border-line bg-panel p-4 space-y-2">
                <p className="text-[11px] font-bold text-muted uppercase tracking-wider">
                  Floor Layout Blueprint ({selectedRoomModal.floor})
                </p>
                <div className="grid grid-cols-3 gap-2 text-center text-xs">
                  <div className="rounded-lg border border-line/60 bg-surface p-2 text-muted">
                    Wing Stairs & Elevator
                  </div>
                  <div className="rounded-lg border-2 border-brand-600 bg-brand-500/20 p-2 font-bold text-brand-700 dark:text-brand-300 shadow-xs">
                    📍 {selectedRoomModal.room}
                    <div className="text-[10px] font-normal">Active Class</div>
                  </div>
                  <div className="rounded-lg border border-line/60 bg-surface p-2 text-muted">
                    Adjoining Hall
                  </div>
                </div>
              </div>

              <div className="space-y-1 text-xs text-muted">
                <p>
                  <strong>Instructor:</strong> {selectedRoomModal.instructorName} ({selectedRoomModal.instructorOffice})
                </p>
                <p>
                  <strong>Enrolled Students:</strong> {selectedRoomModal.enrolledStudents} students (Section: {selectedRoomModal.section})
                </p>
                <p>
                  <strong>Directions:</strong> Enter via Main Courtyard, take North staircase to {selectedRoomModal.floor}, turn left past the Departmental Notice Board.
                </p>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <Link
                to="/explore"
                className="rounded-xl border border-line bg-surface px-4 py-2 text-xs font-semibold text-text hover:border-brand-500 transition"
              >
                Open Full Campus Directory
              </Link>
              <button
                type="button"
                onClick={() => setSelectedRoomModal(null)}
                className="rounded-xl bg-brand-600 px-4 py-2 text-xs font-bold text-white shadow-xs hover:bg-brand-700 transition"
              >
                Close Map
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
