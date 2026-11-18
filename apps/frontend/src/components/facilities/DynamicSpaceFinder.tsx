import { useState, useEffect, useMemo } from "react";
import { Link } from "react-router-dom";
import {
  Search,
  Clock,
  Calendar,
  MapPin,
  Users,
  CheckCircle2,
  AlertTriangle,
  Wifi,
  Tv,
  Wind,
  Zap,
  Monitor,
  Mic,
  QrCode,
  Sparkles,
  X,
  Filter,
  Layers,
  Lock,
  Unlock,
  ArrowRight,
  ShieldCheck,
  Building,
  RotateCcw
} from "lucide-react";

import {
  CAMPUS_ROOMS,
  CAMPUS_DAYS,
  CAMPUS_SLOTS,
  CAMPUS_BLOCKS,
  type CampusRoom,
  type CampusDay,
  type CampusBlockFilter,
  type StudyGroupReservation,
  INITIAL_STUDY_RESERVATIONS,
  getRoomDaySchedule,
  getCurrentSlotTelemetry
} from "../../features/facilities/space-finder-data";

interface Props {
  mode?: "student" | "teacher" | "public";
  initialBlock?: CampusBlockFilter;
  onBookingSuccess?: (reservation: StudyGroupReservation) => void;
}

export function DynamicSpaceFinder({
  mode = "student",
  initialBlock = "All Blocks",
  onBookingSuccess
}: Props) {
  // Current slot telemetry
  const telemetry = useMemo(() => getCurrentSlotTelemetry(), []);

  // Filter states
  const [selectedDay, setSelectedDay] = useState<CampusDay>(telemetry.day);
  const [selectedSlotNumber, setSelectedSlotNumber] = useState<number>(telemetry.slotNumber);
  const [selectedBlock, setSelectedBlock] = useState<CampusBlockFilter>(initialBlock);
  const [isRightNowActive, setIsRightNowActive] = useState<boolean>(false);
  const [showOccupied, setShowOccupied] = useState<boolean>(false);
  const [showWeeklyOverview, setShowWeeklyOverview] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [minCapacity, setMinCapacity] = useState<number>(0);
  const [filterAC, setFilterAC] = useState<boolean>(false);
  const [filterProjector, setFilterProjector] = useState<boolean>(false);
  const [filterWorkstations, setFilterWorkstations] = useState<boolean>(false);

  // Active reservations state (in localStorage or initial state)
  const [reservations, setReservations] = useState<StudyGroupReservation[]>(() => {
    try {
      const saved = localStorage.getItem("smart_edu_study_reservations");
      if (saved) return JSON.parse(saved);
    } catch {
      // ignore
    }
    return INITIAL_STUDY_RESERVATIONS;
  });

  // Modal reservation states
  const [reserveModalRoom, setReserveModalRoom] = useState<CampusRoom | null>(null);
  const [reserveDuration, setReserveDuration] = useState<number>(90);
  const [reserveGroupSize, setReserveGroupSize] = useState<number>(4);
  const [reservePurpose, setReservePurpose] = useState<string>("");
  const [reserveAgreed, setReserveAgreed] = useState<boolean>(true);

  // QR Modal inspection state
  const [activeQrModal, setActiveQrModal] = useState<StudyGroupReservation | null>(null);

  // Countdown timer for pending reservations
  useEffect(() => {
    const timer = setInterval(() => {
      setReservations((prev) =>
        prev.map((res) => {
          if (res.status === "AWAITING_CHECK_IN" && res.expiresInSeconds > 0) {
            return { ...res, expiresInSeconds: res.expiresInSeconds - 1 };
          }
          if (res.status === "AWAITING_CHECK_IN" && res.expiresInSeconds <= 0) {
            return { ...res, status: "EXPIRED" };
          }
          return res;
        })
      );
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Save reservations to localStorage
  useEffect(() => {
    try {
      localStorage.setItem("smart_edu_study_reservations", JSON.stringify(reservations));
    } catch {
      // ignore
    }
  }, [reservations]);

  // Handle "Available Right Now" toggle
  const toggleAvailableRightNow = () => {
    if (!isRightNowActive) {
      const current = getCurrentSlotTelemetry();
      setSelectedDay(current.day);
      setSelectedSlotNumber(current.slotNumber);
      setIsRightNowActive(true);
    } else {
      setIsRightNowActive(false);
    }
  };

  // Filtered rooms calculation
  const filteredRooms = useMemo(() => {
    return CAMPUS_ROOMS.filter((room) => {
      // Block filter
      if (selectedBlock !== "All Blocks" && room.block !== selectedBlock) {
        return false;
      }

      // Search query
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const matchesCode = room.code.toLowerCase().includes(query);
        const matchesName = room.name.toLowerCase().includes(query);
        const matchesFloor = room.floor.toLowerCase().includes(query);
        const matchesBlock = room.block.toLowerCase().includes(query);
        if (!matchesCode && !matchesName && !matchesFloor && !matchesBlock) {
          return false;
        }
      }

      // Min capacity
      if (minCapacity > 0 && room.capacity < minCapacity) {
        return false;
      }

      // Equipment filters
      if (filterAC && !room.equipment.hasAC) return false;
      if (filterProjector && !room.equipment.hasProjector) return false;
      if (filterWorkstations && !room.equipment.hasWorkstations) return false;

      // Slot availability filter — default to showing only available rooms in the selected slot
      const daySchedule = getRoomDaySchedule(room, selectedDay);
      const slot = daySchedule.find((s) => s.slot === selectedSlotNumber);

      if (isRightNowActive || !showOccupied) {
        return slot ? slot.isFree : true;
      }

      return true;
    });
  }, [
    selectedBlock,
    searchQuery,
    minCapacity,
    filterAC,
    filterProjector,
    filterWorkstations,
    selectedDay,
    selectedSlotNumber,
    isRightNowActive,
    showOccupied
  ]);

  // Group rooms by block for structured view
  const roomsByBlock = useMemo(() => {
    const map: Record<string, CampusRoom[]> = {};
    for (const room of filteredRooms) {
      if (!map[room.block]) map[room.block] = [];
      map[room.block]!.push(room);
    }
    return map;
  }, [filteredRooms]);

  // Active slot definition
  const currentSlotDef = CAMPUS_SLOTS.find((s) => s.number === selectedSlotNumber) || CAMPUS_SLOTS[0]!;

  // Handle creating study group reservation
  const handleConfirmReservation = () => {
    if (!reserveModalRoom) return;

    const qrToken = `QR-${reserveModalRoom.code.replace(/[^A-Za-z0-9]/g, "")}-${Math.floor(1000 + Math.random() * 9000)}`;
    const now = new Date();
    const expiryDate = new Date(now.getTime() + 15 * 60 * 1000); // 15 mins check-in window

    const newRes: StudyGroupReservation = {
      id: `res-${Date.now()}`,
      roomCode: reserveModalRoom.code,
      roomName: reserveModalRoom.name,
      block: reserveModalRoom.block,
      floor: reserveModalRoom.floor,
      day: selectedDay,
      slotNumber: selectedSlotNumber,
      slotTime: currentSlotDef.timeRange,
      durationMinutes: reserveDuration,
      purpose: reservePurpose.trim() || "Collaborative Group Study & Problem Solving",
      groupSize: reserveGroupSize,
      reservedAt: now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      expiresAt: expiryDate.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      expiresInSeconds: 15 * 60,
      isCheckedIn: false,
      qrToken,
      status: "AWAITING_CHECK_IN"
    };

    setReservations((prev) => [newRes, ...prev]);
    if (onBookingSuccess) onBookingSuccess(newRes);

    setReserveModalRoom(null);
    setReservePurpose("");
    setActiveQrModal(newRes);
  };

  // Simulate Door QR Scan check-in
  const handleSimulateCheckIn = (resId: string) => {
    setReservations((prev) =>
      prev.map((r) =>
        r.id === resId
          ? {
              ...r,
              isCheckedIn: true,
              status: "CONFIRMED_ACTIVE"
            }
          : r
      )
    );
    if (activeQrModal && activeQrModal.id === resId) {
      setActiveQrModal((prev) => (prev ? { ...prev, isCheckedIn: true, status: "CONFIRMED_ACTIVE" } : null));
    }
  };

  // Cancel reservation
  const handleCancelReservation = (resId: string) => {
    setReservations((prev) => prev.filter((r) => r.id !== resId));
    if (activeQrModal && activeQrModal.id === resId) {
      setActiveQrModal(null);
    }
  };

  // Format seconds into mm:ss
  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const activeReservationsCount = reservations.filter((r) => r.status === "AWAITING_CHECK_IN" || r.status === "CONFIRMED_ACTIVE").length;

  return (
    <div className="space-y-6">
      {/* ================= ACTIVE RESERVATIONS DRAWER / NOTIFICATION ================= */}
      {activeReservationsCount > 0 && (
        <div className="rounded-2xl border border-brand-500/40 bg-gradient-to-r from-brand-500/10 via-indigo-500/5 to-transparent p-5 shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-brand-600 text-white shadow-xs">
                <QrCode size={22} />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-bold text-sm text-ink">Active Room Reservations</h4>
                  <span className="rounded-full bg-brand-500/20 px-2 py-0.5 text-2xs font-extrabold text-brand-600 dark:text-brand-300">
                    {activeReservationsCount} Active
                  </span>
                </div>
                <p className="text-xs text-muted mt-0.5">
                  Check in at the door terminal within 15 minutes to prevent auto-release.
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              {reservations
                .filter((r) => r.status === "AWAITING_CHECK_IN" || r.status === "CONFIRMED_ACTIVE")
                .map((res) => (
                  <button
                    key={res.id}
                    onClick={() => setActiveQrModal(res)}
                    className={`inline-flex items-center gap-2 rounded-xl px-3 py-1.5 text-xs font-semibold transition border ${
                      res.status === "CONFIRMED_ACTIVE"
                        ? "border-emerald-500/40 bg-emerald-50 text-emerald-800 dark:bg-emerald-950/40 dark:text-emerald-300"
                        : "border-amber-500/40 bg-amber-50 text-amber-900 dark:bg-amber-950/40 dark:text-amber-300"
                    }`}
                  >
                    <span className="flex h-2 w-2 rounded-full bg-current animate-pulse" />
                    <span>{res.roomCode}</span>
                    <span className="text-2xs opacity-80">
                      {res.status === "CONFIRMED_ACTIVE" ? "✓ Checked In" : `Door Timer: ${formatTimer(res.expiresInSeconds)}`}
                    </span>
                    <QrCode size={13} className="ml-0.5 opacity-70" />
                  </button>
                ))}
            </div>
          </div>
        </div>
      )}

      {/* ================= HEADER CONTROLS BAR ================= */}
      <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <h3 className="text-base font-bold text-ink">Dynamic Space Finder & Free Slot Navigator</h3>
              <span className="rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-2xs font-semibold text-emerald-600">
                Live Sensor Sync
              </span>
            </div>
            <p className="text-xs text-muted mt-1">
              Select day and slot or toggle <strong className="text-ink">Available Right Now</strong> to find empty lecture rooms, labs, and study pods.
            </p>
          </div>

          {/* Quick Available Right Now Button */}
          <button
            onClick={toggleAvailableRightNow}
            className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-bold transition shadow-xs ${
              isRightNowActive
                ? "bg-emerald-600 text-white ring-2 ring-emerald-500/50"
                : "border border-line bg-surface text-ink hover:border-emerald-500 hover:text-emerald-600"
            }`}
          >
            <Sparkles size={15} className={isRightNowActive ? "animate-spin" : ""} />
            <span>⚡ Available Right Now</span>
            {isRightNowActive && (
              <span className="rounded-md bg-white/20 px-1.5 py-0.5 text-2xs font-mono">
                {telemetry.timeString}
              </span>
            )}
          </button>
        </div>

        {/* ================= PRIMARY TIME SLOT SELECTOR ================= */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 pt-2 border-t border-line/60">
          {/* Day Selector */}
          <div>
            <label className="block text-xs font-semibold text-muted mb-1.5 flex items-center gap-1.5">
              <Calendar size={13} className="text-brand-500" />
              <span>Select Day</span>
            </label>
            <select
              value={selectedDay}
              onChange={(e) => {
                setSelectedDay(e.target.value as CampusDay);
                setIsRightNowActive(false);
              }}
              className="w-full rounded-xl border border-line bg-surface px-3 py-2 text-xs font-semibold text-ink focus:outline-hidden focus:ring-2 focus:ring-brand-500"
            >
              {CAMPUS_DAYS.map((day) => (
                <option key={day} value={day}>
                  {day}
                </option>
              ))}
            </select>
          </div>

          {/* Slot Selector */}
          <div>
            <label className="block text-xs font-semibold text-muted mb-1.5 flex items-center gap-1.5">
              <Clock size={13} className="text-brand-500" />
              <span>Lecture Slot</span>
            </label>
            <select
              value={selectedSlotNumber}
              onChange={(e) => {
                setSelectedSlotNumber(Number(e.target.value));
                setIsRightNowActive(false);
              }}
              className="w-full rounded-xl border border-line bg-surface px-3 py-2 text-xs font-semibold text-ink focus:outline-hidden focus:ring-2 focus:ring-brand-500"
            >
              {CAMPUS_SLOTS.map((slot) => (
                <option key={slot.number} value={slot.number}>
                  {slot.label}
                </option>
              ))}
            </select>
          </div>

          {/* Search Query */}
          <div>
            <label className="block text-xs font-semibold text-muted mb-1.5 flex items-center gap-1.5">
              <Search size={13} className="text-brand-500" />
              <span>Filter Rooms</span>
            </label>
            <div className="relative">
              <input
                type="text"
                placeholder="Search C-204, Software Lab, 2nd floor..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-xl border border-line bg-surface px-3 py-2 pl-8 text-xs text-ink placeholder:text-muted focus:outline-hidden focus:ring-2 focus:ring-brand-500"
              />
              <Search size={13} className="absolute left-2.5 top-2.5 text-muted" />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute right-2.5 top-2.5 text-muted hover:text-ink"
                >
                  <X size={12} />
                </button>
              )}
            </div>
          </div>

          {/* Capacity Filter */}
          <div>
            <label className="block text-xs font-semibold text-muted mb-1.5 flex items-center gap-1.5">
              <Users size={13} className="text-brand-500" />
              <span>Min Capacity</span>
            </label>
            <select
              value={minCapacity}
              onChange={(e) => setMinCapacity(Number(e.target.value))}
              className="w-full rounded-xl border border-line bg-surface px-3 py-2 text-xs font-semibold text-ink focus:outline-hidden focus:ring-2 focus:ring-brand-500"
            >
              <option value={0}>Any Capacity</option>
              <option value={15}>15+ Seats (Pod / Small)</option>
              <option value={40}>40+ Seats (Medium Class)</option>
              <option value={60}>60+ Seats (Large Hall)</option>
            </select>
          </div>
        </div>

        {/* Equipment Filter Pills */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-line/60">
          <span className="text-2xs font-bold uppercase tracking-wider text-muted mr-1">
            Amenities:
          </span>

          <button
            onClick={() => setFilterAC((prev) => !prev)}
            className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-2xs font-semibold transition border ${
              filterAC
                ? "border-sky-500/50 bg-sky-500/10 text-sky-600 dark:text-sky-300 font-bold"
                : "border-line bg-surface text-muted hover:text-ink"
            }`}
          >
            <Wind size={12} />
            <span>Air Conditioned</span>
          </button>

          <button
            onClick={() => setFilterProjector((prev) => !prev)}
            className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-2xs font-semibold transition border ${
              filterProjector
                ? "border-indigo-500/50 bg-indigo-500/10 text-indigo-600 dark:text-indigo-300 font-bold"
                : "border-line bg-surface text-muted hover:text-ink"
            }`}
          >
            <Tv size={12} />
            <span>Overhead Projector</span>
          </button>

          <button
            onClick={() => setFilterWorkstations((prev) => !prev)}
            className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-2xs font-semibold transition border ${
              filterWorkstations
                ? "border-violet-500/50 bg-violet-500/10 text-violet-600 dark:text-violet-300 font-bold"
                : "border-line bg-surface text-muted hover:text-ink"
            }`}
          >
            <Monitor size={12} />
            <span>Workstations / PCs</span>
          </button>

          <button
            onClick={() => setShowOccupied((prev) => !prev)}
            className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-2xs font-semibold transition border ${
              showOccupied
                ? "border-amber-500/50 bg-amber-500/10 text-amber-700 dark:text-amber-300 font-bold"
                : "border-line bg-surface text-muted hover:text-ink"
            }`}
          >
            <Lock size={11} />
            <span>{showOccupied ? "Showing Occupied Too" : "Available Only"}</span>
          </button>

          <button
            onClick={() => setShowWeeklyOverview((prev) => !prev)}
            className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-surface px-2.5 py-1 text-2xs font-semibold text-brand-600 hover:border-brand-500 transition"
          >
            <Calendar size={11} />
            <span>{showWeeklyOverview ? "Hide Full Week Grid" : "Show Full Week Grid"}</span>
          </button>

          {(filterAC || filterProjector || filterWorkstations || searchQuery || minCapacity > 0) && (
            <button
              onClick={() => {
                setFilterAC(false);
                setFilterProjector(false);
                setFilterWorkstations(false);
                setSearchQuery("");
                setMinCapacity(0);
              }}
              className="ml-auto inline-flex items-center gap-1 text-2xs font-semibold text-muted hover:text-red-500 transition"
            >
              <RotateCcw size={11} />
              <span>Reset Filters</span>
            </button>
          )}
        </div>
      </div>

      {/* ================= FULL WEEK FREE SLOTS OVERVIEW ================= */}
      {showWeeklyOverview && (
        <div className="rounded-2xl border border-line bg-panel p-4 shadow-2xs space-y-3 overflow-x-auto">
          <div className="flex items-center justify-between gap-2">
            <div>
              <h4 className="font-bold text-xs text-ink">Full Week Free Slots Matrix (Monday – Saturday)</h4>
              <p className="text-2xs text-muted">Click any slot cell to view block-wise available rooms for that day and period.</p>
            </div>
          </div>

          <table className="w-full min-w-[600px] border-collapse text-xs">
            <thead>
              <tr className="border-b border-line text-left text-2xs uppercase tracking-wider text-muted">
                <th className="py-2 pr-3 font-bold">Day</th>
                {CAMPUS_SLOTS.map((slot) => (
                  <th key={slot.number} className="px-2 py-2 text-center font-bold">
                    Slot {slot.number}
                    <span className="block font-mono font-normal text-[10px]">{slot.timeRange.replace(" AM", "").replace(" PM", "")}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-line/50">
              {CAMPUS_DAYS.map((day) => (
                <tr key={day}>
                  <td className="py-2 pr-3 font-bold text-ink">{day}</td>
                  {CAMPUS_SLOTS.map((slot) => {
                    const freeCount = CAMPUS_ROOMS.filter((room) => {
                      const s = getRoomDaySchedule(room, day).find((x) => x.slot === slot.number);
                      return s ? s.isFree : true;
                    }).length;
                    const isSelectedCell = selectedDay === day && selectedSlotNumber === slot.number;
                    return (
                      <td key={slot.number} className="p-1.5 text-center">
                        <button
                          type="button"
                          onClick={() => {
                            setSelectedDay(day);
                            setSelectedSlotNumber(slot.number);
                            setIsRightNowActive(false);
                          }}
                          className={`w-full rounded-lg px-2 py-1.5 text-2xs font-bold transition border ${
                            isSelectedCell
                              ? "border-brand-600 bg-brand-600 text-white shadow-xs"
                              : "border-emerald-500/30 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 hover:border-brand-500"
                          }`}
                        >
                          {freeCount} Free
                        </button>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ================= MULTI-BLOCK NAVIGATION TABS ================= */}
      <div className="flex flex-wrap items-center gap-2 border-b border-line pb-3">
        {CAMPUS_BLOCKS.map((block) => {
          const count =
            block === "All Blocks"
              ? filteredRooms.length
              : filteredRooms.filter((r) => r.block === block).length;

          const isSelected = selectedBlock === block;

          return (
            <button
              key={block}
              onClick={() => setSelectedBlock(block)}
              className={`inline-flex items-center gap-2 rounded-xl px-3.5 py-2 text-xs font-semibold transition ${
                isSelected
                  ? "bg-brand-600 text-white shadow-xs font-bold"
                  : "bg-panel text-muted border border-line hover:border-brand-500/50 hover:text-ink"
              }`}
            >
              <Building size={13} className={isSelected ? "text-white" : "text-muted"} />
              <span>{block}</span>
              <span
                className={`rounded-full px-2 py-0.5 text-2xs font-bold ${
                  isSelected
                    ? "bg-white/20 text-white"
                    : "bg-surface text-muted"
                }`}
              >
                {count}
              </span>
            </button>
          );
        })}
      </div>

      {/* ================= TELEMETRY SUMMARY BANNER ================= */}
      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-muted px-1">
        <div>
          Showing availability for <strong className="text-ink">{selectedDay}</strong> ·{" "}
          <strong className="text-brand-600">{currentSlotDef.label}</strong> ({currentSlotDef.timeRange})
        </div>
        <div>
          Found <strong className="text-ink">{filteredRooms.length}</strong> matching rooms across campus
        </div>
      </div>

      {/* ================= ROOMS GRID / BLOCK-WISE ACCORDIONS ================= */}
      {filteredRooms.length === 0 ? (
        <div className="rounded-2xl border border-line bg-panel p-12 text-center space-y-3">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-surface text-muted">
            <Search size={22} />
          </div>
          <h4 className="font-bold text-sm text-ink">No Free Rooms Found</h4>
          <p className="text-xs text-muted max-w-md mx-auto">
            No rooms match your active filter criteria for {selectedDay} ({currentSlotDef.label}). Try selecting another lecture slot or clearing equipment filters.
          </p>
          <button
            onClick={() => {
              setFilterAC(false);
              setFilterProjector(false);
              setFilterWorkstations(false);
              setMinCapacity(0);
              setSearchQuery("");
              setSelectedBlock("All Blocks");
            }}
            className="rounded-xl border border-line bg-surface px-4 py-2 text-xs font-bold text-brand-600 hover:border-brand-500"
          >
            Clear All Filters
          </button>
        </div>
      ) : (
        <div className="space-y-8">
          {Object.entries(roomsByBlock).map(([blockName, blockRooms]) => (
            <div key={blockName} className="space-y-4">
              {/* Block Header */}
              <div className="flex items-center justify-between border-b border-line pb-2">
                <div className="flex items-center gap-2">
                  <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-500/10 text-brand-600">
                    <Building size={15} />
                  </div>
                  <div>
                    <h3 className="font-bold text-sm text-ink">{blockName}</h3>
                    <p className="text-2xs text-muted">
                      {blockRooms.length} rooms listed in this sector
                    </p>
                  </div>
                </div>

                <span className="rounded-full bg-emerald-500/10 px-2.5 py-0.5 text-2xs font-bold text-emerald-600">
                  {blockRooms.filter((r) => {
                    const slot = getRoomDaySchedule(r, selectedDay).find((s) => s.slot === selectedSlotNumber);
                    return slot?.isFree ?? true;
                  }).length}{" "}
                  Available Now
                </span>
              </div>

              {/* Rooms Grid */}
              <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                {blockRooms.map((room) => {
                  const daySchedule = getRoomDaySchedule(room, selectedDay);
                  const currentSlot = daySchedule.find((s) => s.slot === selectedSlotNumber);
                  const isSlotFree = currentSlot ? currentSlot.isFree : true;

                  // Check if room has an active study reservation right now
                  const activeRes = reservations.find(
                    (r) =>
                      r.roomCode === room.code &&
                      r.day === selectedDay &&
                      r.slotNumber === selectedSlotNumber &&
                      (r.status === "AWAITING_CHECK_IN" || r.status === "CONFIRMED_ACTIVE")
                  );

                  return (
                    <div
                      key={room.id}
                      className={`flex flex-col justify-between rounded-2xl border p-5 shadow-2xs transition group hover:shadow-md ${
                        activeRes
                          ? "border-amber-500/60 bg-amber-500/5 dark:bg-amber-950/10"
                          : isSlotFree
                          ? "border-line bg-panel hover:border-brand-500/60"
                          : "border-line/60 bg-panel/60 opacity-85"
                      }`}
                    >
                      <div className="space-y-3.5">
                        {/* Card Top: Code & Floor & Status */}
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <div className="flex items-center gap-2">
                              <h4 className="font-extrabold text-base text-ink group-hover:text-brand-600 transition">
                                {room.code}
                              </h4>
                              <span className="rounded-md bg-surface border border-line px-2 py-0.5 text-2xs font-semibold text-muted">
                                {room.floor}
                              </span>
                            </div>
                            <p className="text-xs text-muted mt-0.5 line-clamp-1">{room.name}</p>
                          </div>

                          {/* Status Badge */}
                          {activeRes ? (
                            <span className="inline-flex items-center gap-1 rounded-full bg-amber-500/15 px-2.5 py-1 text-2xs font-extrabold text-amber-700 dark:text-amber-300">
                              <Lock size={10} />
                              <span>Reserved</span>
                            </span>
                          ) : isSlotFree ? (
                            <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/15 px-2.5 py-1 text-2xs font-extrabold text-emerald-600">
                              <Unlock size={10} />
                              <span>Available</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 rounded-full bg-rose-500/10 px-2.5 py-1 text-2xs font-semibold text-rose-600">
                              <Lock size={10} />
                              <span>In Class</span>
                            </span>
                          )}
                        </div>

                        {/* Room Telemetry: Capacity & Next Class */}
                        <div className="rounded-xl border border-line/60 bg-surface/50 p-3 space-y-2">
                          <div className="flex items-center justify-between text-xs">
                            <span className="flex items-center gap-1 text-muted">
                              <Users size={12} className="text-brand-500" />
                              <span>Capacity</span>
                            </span>
                            <span className="font-bold text-ink">{room.capacity} Student Desks</span>
                          </div>

                          <div className="flex items-center justify-between text-xs">
                            <span className="flex items-center gap-1 text-muted">
                              <Clock size={12} className="text-emerald-500" />
                              <span>Free Until</span>
                            </span>
                            <span className="font-bold text-emerald-600">
                              {currentSlot?.freeUntil || "05:15 PM"}
                            </span>
                          </div>

                          {!isSlotFree && currentSlot?.bookedBy && (
                            <div className="pt-1 border-t border-line/40 text-2xs text-rose-600 flex items-center gap-1">
                              <AlertTriangle size={11} />
                              <span className="truncate">Booked: {currentSlot.bookedBy}</span>
                            </div>
                          )}
                        </div>

                        {/* Equipment Pills */}
                        <div className="space-y-1.5">
                          <span className="text-2xs font-semibold text-muted uppercase tracking-wider">
                            Room Equipment
                          </span>
                          <div className="flex flex-wrap gap-1.5">
                            {room.equipment.hasProjector && (
                              <span className="inline-flex items-center gap-1 rounded-md bg-surface border border-line/60 px-2 py-0.5 text-2xs text-ink">
                                <Tv size={10} className="text-brand-500" />
                                <span>Projector</span>
                              </span>
                            )}
                            {room.equipment.hasAC && (
                              <span className="inline-flex items-center gap-1 rounded-md bg-surface border border-line/60 px-2 py-0.5 text-2xs text-ink">
                                <Wind size={10} className="text-sky-500" />
                                <span>AC</span>
                              </span>
                            )}
                            {room.equipment.hasWifi && (
                              <span className="inline-flex items-center gap-1 rounded-md bg-surface border border-line/60 px-2 py-0.5 text-2xs text-ink">
                                <Wifi size={10} className="text-emerald-500" />
                                <span>High-Density Wi-Fi</span>
                              </span>
                            )}
                            {room.equipment.hasPowerSockets && (
                              <span className="inline-flex items-center gap-1 rounded-md bg-surface border border-line/60 px-2 py-0.5 text-2xs text-ink">
                                <Zap size={10} className="text-amber-500" />
                                <span>Desk Outlets</span>
                              </span>
                            )}
                            {room.equipment.hasSmartPodium && (
                              <span className="inline-flex items-center gap-1 rounded-md bg-surface border border-line/60 px-2 py-0.5 text-2xs text-ink">
                                <Mic size={10} className="text-purple-500" />
                                <span>Smart Podium</span>
                              </span>
                            )}
                            {room.equipment.hasWorkstations && (
                              <span className="inline-flex items-center gap-1 rounded-md bg-surface border border-line/60 px-2 py-0.5 text-2xs text-ink">
                                <Monitor size={10} className="text-violet-500" />
                                <span>PCs / Labs</span>
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Daily Mini Slot Matrix Bar (Slots 1 to 5) */}
                        <div className="space-y-1.5 pt-1">
                          <span className="text-2xs font-semibold text-muted uppercase tracking-wider flex items-center justify-between">
                            <span>Today's Slots</span>
                            <span className="text-2xs lowercase font-normal">{selectedDay}</span>
                          </span>
                          <div className="grid grid-cols-5 gap-1">
                            {daySchedule.map((slot) => {
                              const isActiveSelectedSlot = slot.slot === selectedSlotNumber;
                              return (
                                <button
                                  key={slot.slot}
                                  onClick={() => setSelectedSlotNumber(slot.slot)}
                                  title={`Slot ${slot.slot}: ${slot.isFree ? "Free" : "Occupied"}`}
                                  className={`rounded-md py-1 text-center text-2xs font-bold transition ${
                                    isActiveSelectedSlot
                                      ? "ring-2 ring-brand-500 font-extrabold"
                                      : ""
                                  } ${
                                    slot.isFree
                                      ? "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 hover:bg-emerald-500/25"
                                      : "bg-surface text-muted/60 line-through"
                                  }`}
                                >
                                  S{slot.slot}
                                </button>
                              );
                            })}
                          </div>
                        </div>
                      </div>

                      {/* Card Action Footer */}
                      <div className="mt-5 pt-4 border-t border-line/60">
                        {activeRes ? (
                          <button
                            onClick={() => setActiveQrModal(activeRes)}
                            className="w-full inline-flex items-center justify-center gap-1.5 rounded-xl border border-amber-500/40 bg-amber-500/10 py-2.5 text-xs font-bold text-amber-700 dark:text-amber-300 hover:bg-amber-500/20 transition"
                          >
                            <QrCode size={14} />
                            <span>View QR Door Pass</span>
                          </button>
                        ) : isSlotFree ? (
                          mode === "public" ? (
                            <Link
                              to="/login"
                              className="w-full inline-flex items-center justify-center gap-1.5 rounded-xl bg-brand-600 py-2.5 text-xs font-bold text-white hover:bg-brand-700 transition shadow-xs"
                            >
                              <span>Sign In to Reserve</span>
                              <ArrowRight size={14} />
                            </Link>
                          ) : (
                            <button
                              onClick={() => {
                                setReserveModalRoom(room);
                                setReservePurpose("");
                              }}
                              className="w-full inline-flex items-center justify-center gap-1.5 rounded-xl bg-brand-600 py-2.5 text-xs font-bold text-white hover:bg-brand-700 transition shadow-xs"
                            >
                              <Calendar size={14} />
                              <span>
                                {mode === "student"
                                  ? "Reserve for Study Group"
                                  : "Book for Makeup Lecture"}
                              </span>
                            </button>
                          )
                        ) : (
                          <button
                            disabled
                            className="w-full rounded-xl bg-surface/80 py-2 text-xs font-semibold text-muted cursor-not-allowed border border-line/60"
                          >
                            Occupied During This Slot
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ================= STUDY GROUP RESERVATION MODAL ================= */}
      {reserveModalRoom && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
          <div className="w-full max-w-lg rounded-3xl border border-line bg-panel p-6 shadow-2xl space-y-5 animate-in zoom-in-95 duration-200">
            {/* Modal Header */}
            <div className="flex items-start justify-between">
              <div>
                <span className="rounded-full bg-brand-500/10 px-2.5 py-0.5 text-2xs font-extrabold text-brand-600 uppercase tracking-wider">
                  Campus Space Governance
                </span>
                <h3 className="font-extrabold text-lg text-ink mt-1">
                  Reserve {reserveModalRoom.code}
                </h3>
                <p className="text-xs text-muted">
                  {reserveModalRoom.name} · {reserveModalRoom.floor} ({reserveModalRoom.block})
                </p>
              </div>

              <button
                onClick={() => setReserveModalRoom(null)}
                className="rounded-xl p-1.5 text-muted hover:bg-surface hover:text-ink transition"
              >
                <X size={18} />
              </button>
            </div>

            {/* Governance Policy Warning */}
            <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 p-3.5 flex items-start gap-3 text-xs text-amber-900 dark:text-amber-200">
              <ShieldCheck size={18} className="shrink-0 text-amber-600 mt-0.5" />
              <div>
                <strong className="font-bold">University Reservation Policy:</strong> Max 90 minutes.
                You must scan the room entrance QR code within 15 minutes of reservation start time, or the room will be automatically released back to the campus pool.
              </div>
            </div>

            {/* Form Fields */}
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-ink mb-1.5">
                  Slot Time Window ({selectedDay})
                </label>
                <div className="rounded-xl border border-line bg-surface p-2.5 text-xs font-semibold text-ink flex items-center justify-between">
                  <span>{currentSlotDef.label}</span>
                  <span className="text-brand-600 font-bold">{currentSlotDef.timeRange}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-ink mb-1.5">
                    Duration (Max 90m)
                  </label>
                  <select
                    value={reserveDuration}
                    onChange={(e) => setReserveDuration(Number(e.target.value))}
                    className="w-full rounded-xl border border-line bg-surface px-3 py-2 text-xs font-semibold text-ink focus:outline-hidden focus:ring-2 focus:ring-brand-500"
                  >
                    <option value={30}>30 Minutes</option>
                    <option value={45}>45 Minutes</option>
                    <option value={60}>60 Minutes</option>
                    <option value={90}>90 Minutes (Maximum)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-ink mb-1.5">Group Size</label>
                  <input
                    type="number"
                    min={2}
                    max={15}
                    value={reserveGroupSize}
                    onChange={(e) => setReserveGroupSize(Number(e.target.value))}
                    className="w-full rounded-xl border border-line bg-surface px-3 py-2 text-xs font-semibold text-ink focus:outline-hidden focus:ring-2 focus:ring-brand-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-ink mb-1.5">
                  Study Purpose / Course Discussion
                </label>
                <input
                  type="text"
                  placeholder="e.g. Compiler Construction Parser Sprint, Midterm Review..."
                  value={reservePurpose}
                  onChange={(e) => setReservePurpose(e.target.value)}
                  className="w-full rounded-xl border border-line bg-surface px-3 py-2.5 text-xs text-ink placeholder:text-muted focus:outline-hidden focus:ring-2 focus:ring-brand-500"
                />
              </div>

              <label className="flex items-center gap-2.5 text-xs text-muted cursor-pointer pt-1">
                <input
                  type="checkbox"
                  checked={reserveAgreed}
                  onChange={(e) => setReserveAgreed(e.target.checked)}
                  className="rounded-md border-line text-brand-600 focus:ring-brand-500"
                />
                <span>We agree to follow room decorum, turn off lights, and vacate on time.</span>
              </label>
            </div>

            {/* Modal Actions */}
            <div className="flex items-center justify-end gap-3 pt-3 border-t border-line/60">
              <button
                type="button"
                onClick={() => setReserveModalRoom(null)}
                className="rounded-xl border border-line bg-surface px-4 py-2.5 text-xs font-bold text-muted hover:text-ink transition"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleConfirmReservation}
                disabled={!reserveAgreed}
                className="inline-flex items-center gap-1.5 rounded-xl bg-brand-600 px-5 py-2.5 text-xs font-bold text-white hover:bg-brand-700 transition disabled:opacity-50 shadow-xs"
              >
                <CheckCircle2 size={15} />
                <span>Confirm & Generate QR Pass</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ================= DIGITAL QR PASS & CHECK-IN MODAL ================= */}
      {activeQrModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
          <div className="w-full max-w-md rounded-3xl border border-line bg-panel p-6 shadow-2xl space-y-6 text-center animate-in zoom-in-95 duration-200">
            {/* Modal Close */}
            <div className="flex items-center justify-between text-left">
              <div className="flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-500/10 text-brand-600">
                  <QrCode size={18} />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-ink">Room Access QR Pass</h4>
                  <p className="text-2xs text-muted">{activeQrModal.roomCode}</p>
                </div>
              </div>
              <button
                onClick={() => setActiveQrModal(null)}
                className="rounded-xl p-1.5 text-muted hover:bg-surface hover:text-ink transition"
              >
                <X size={18} />
              </button>
            </div>

            {/* QR Visual Card */}
            <div className="rounded-2xl border-2 border-dashed border-brand-500/40 bg-surface/60 p-6 space-y-4">
              <div className="mx-auto flex h-48 w-48 items-center justify-center rounded-2xl bg-white p-3 shadow-inner">
                {/* SVG QR Code Simulation */}
                <svg
                  viewBox="0 0 100 100"
                  className="h-full w-full text-zinc-900 fill-current"
                >
                  <rect x="0" y="0" width="30" height="30" rx="4" />
                  <rect x="5" y="5" width="20" height="20" fill="white" rx="2" />
                  <rect x="10" y="10" width="10" height="10" />

                  <rect x="70" y="0" width="30" height="30" rx="4" />
                  <rect x="75" y="5" width="20" height="20" fill="white" rx="2" />
                  <rect x="80" y="10" width="10" height="10" />

                  <rect x="0" y="70" width="30" height="30" rx="4" />
                  <rect x="5" y="75" width="20" height="20" fill="white" rx="2" />
                  <rect x="10" y="80" width="10" height="10" />

                  {/* Matrix patterns */}
                  <rect x="36" y="8" width="8" height="8" />
                  <rect x="48" y="12" width="6" height="14" />
                  <rect x="14" y="38" width="12" height="6" />
                  <rect x="34" y="36" width="14" height="14" />
                  <rect x="54" y="40" width="8" height="8" />
                  <rect x="70" y="38" width="12" height="14" />
                  <rect x="40" y="58" width="10" height="10" />
                  <rect x="58" y="60" width="12" height="8" />
                  <rect x="36" y="78" width="8" height="12" />
                  <rect x="78" y="70" width="14" height="14" />
                </svg>
              </div>

              <div>
                <p className="font-mono text-xs font-bold text-ink tracking-wider">
                  {activeQrModal.qrToken}
                </p>
                <p className="text-2xs text-muted mt-1">
                  Hold screen against the room door tablet or optical scanner
                </p>
              </div>
            </div>

            {/* Check-in Status & Countdown */}
            {activeQrModal.status === "CONFIRMED_ACTIVE" ? (
              <div className="rounded-2xl border border-emerald-500/40 bg-emerald-500/10 p-4 text-center space-y-1">
                <div className="inline-flex items-center gap-1.5 text-xs font-extrabold text-emerald-600">
                  <CheckCircle2 size={16} />
                  <span>Door Check-in Confirmed!</span>
                </div>
                <p className="text-2xs text-emerald-700 dark:text-emerald-300">
                  Room access granted for {activeQrModal.durationMinutes} minutes. Enjoy your session!
                </p>
              </div>
            ) : (
              <div className="rounded-2xl border border-amber-500/40 bg-amber-500/10 p-4 text-center space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-amber-800 dark:text-amber-300 flex items-center gap-1">
                    <Clock size={13} />
                    <span>Auto-Release Countdown</span>
                  </span>
                  <span className="font-mono font-extrabold text-amber-900 dark:text-amber-200">
                    {formatTimer(activeQrModal.expiresInSeconds)}
                  </span>
                </div>
                <p className="text-2xs text-muted text-left">
                  Scan before the timer hits 00:00 to lock in your booking.
                </p>

                {/* Simulate Door Check-in Button */}
                <button
                  onClick={() => handleSimulateCheckIn(activeQrModal.id)}
                  className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 py-2.5 text-xs font-bold text-white hover:bg-emerald-700 transition shadow-xs mt-2"
                >
                  <CheckCircle2 size={15} />
                  <span>Simulate Door QR Check-in</span>
                </button>
              </div>
            )}

            {/* Modal Footer */}
            <div className="flex items-center justify-between pt-2 border-t border-line/60">
              <button
                onClick={() => handleCancelReservation(activeQrModal.id)}
                className="text-xs font-bold text-rose-600 hover:underline"
              >
                Release Room
              </button>
              <button
                onClick={() => setActiveQrModal(null)}
                className="rounded-xl border border-line bg-surface px-4 py-2 text-xs font-bold text-ink hover:border-brand-500 transition"
              >
                Close Pass
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
