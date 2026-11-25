import { useState, useMemo } from "react";
import {
  ChevronLeft,
  Users,
  DoorClosed,
  FlaskConical,
  Wifi,
  Tv,
  Wind,
  Zap,
  MapPin,
  Clock,
  X
} from "lucide-react";
import {
  CAMPUS_ROOMS,
  CAMPUS_SLOTS,
  type CampusRoom,
  getRoomDaySchedule
} from "../../features/facilities/space-finder-data";

interface Props {
  onBack?: () => void;
}

type ShortDay = "Mon" | "Tue" | "Wed" | "Thu" | "Fri";
const DAYS: ShortDay[] = ["Mon", "Tue", "Wed", "Thu", "Fri"];
const SLOTS = [1, 2, 3, 4, 5];

const DAY_FULL_MAP: Record<ShortDay, string> = {
  Mon: "Monday",
  Tue: "Tuesday",
  Wed: "Wednesday",
  Thu: "Thursday",
  Fri: "Friday"
};

interface BlockTheme {
  letter: string;
  displayName: string;
  badgeBg: string;
  titleColor: string;
  headerBg: string;
  borderColor: string;
  itemBorder: string;
  itemBg: string;
  itemHoverBg: string;
  roomCodeColor: string;
  capacityColor: string;
  labBorder: string;
  labBg: string;
  labText: string;
  iconBg: string;
  iconColor: string;
}

const BLOCK_THEMES: Record<string, BlockTheme> = {
  "Block A": {
    letter: "A",
    displayName: "A- Block",
    badgeBg: "bg-primary text-on-primary",
    titleColor: "text-primary-ink",
    headerBg: "bg-primary-soft/55",
    borderColor: "border-primary/25",
    itemBorder: "border-primary/30",
    itemBg: "bg-primary-soft/35",
    itemHoverBg: "hover:bg-primary-soft/75",
    roomCodeColor: "text-primary-ink",
    capacityColor: "text-primary-ink/85",
    labBorder: "border-primary/30",
    labBg: "bg-primary-soft/55",
    labText: "text-primary-ink",
    iconBg: "bg-primary-soft",
    iconColor: "text-primary-ink"
  },
  "Block B": {
    letter: "B",
    displayName: "B- Block",
    badgeBg: "bg-secondary text-secondary-fg",
    titleColor: "text-secondary-ink",
    headerBg: "bg-secondary-soft/55",
    borderColor: "border-secondary/25",
    itemBorder: "border-secondary/30",
    itemBg: "bg-secondary-soft/35",
    itemHoverBg: "hover:bg-secondary-soft/75",
    roomCodeColor: "text-secondary-ink",
    capacityColor: "text-secondary-ink/85",
    labBorder: "border-secondary/30",
    labBg: "bg-secondary-soft/55",
    labText: "text-secondary-ink",
    iconBg: "bg-secondary-soft",
    iconColor: "text-secondary-ink"
  },
  "Block C": {
    letter: "C",
    displayName: "C- Block",
    badgeBg: "bg-success text-success-fg",
    titleColor: "text-success-ink",
    headerBg: "bg-success-soft/55",
    borderColor: "border-success/25",
    itemBorder: "border-success/30",
    itemBg: "bg-success-soft/35",
    itemHoverBg: "hover:bg-success-soft/75",
    roomCodeColor: "text-success-ink",
    capacityColor: "text-success-ink/85",
    labBorder: "border-success/30",
    labBg: "bg-success-soft/55",
    labText: "text-success-ink",
    iconBg: "bg-success-soft",
    iconColor: "text-success-ink"
  },
  "Block D": {
    letter: "D",
    displayName: "D- Block",
    badgeBg: "bg-accent text-accent-fg",
    titleColor: "text-accent-ink",
    headerBg: "bg-accent-soft/55",
    borderColor: "border-accent/35",
    itemBorder: "border-accent/35",
    itemBg: "bg-accent-soft/35",
    itemHoverBg: "hover:bg-accent-soft/75",
    roomCodeColor: "text-accent-ink",
    capacityColor: "text-accent-ink/85",
    labBorder: "border-accent/35",
    labBg: "bg-accent-soft/55",
    labText: "text-accent-ink",
    iconBg: "bg-accent-soft",
    iconColor: "text-accent-ink"
  },
  "Engineering Labs": {
    letter: "E",
    displayName: "Engineering Labs",
    badgeBg: "bg-warning text-warning-fg",
    titleColor: "text-warning-ink",
    headerBg: "bg-warning-soft/55",
    borderColor: "border-warning/30",
    itemBorder: "border-warning/30",
    itemBg: "bg-warning-soft/35",
    itemHoverBg: "hover:bg-warning-soft/75",
    roomCodeColor: "text-warning-ink",
    capacityColor: "text-warning-ink/85",
    labBorder: "border-warning/30",
    labBg: "bg-warning-soft/55",
    labText: "text-warning-ink",
    iconBg: "bg-warning-soft",
    iconColor: "text-warning-ink"
  }
};

export function FreeSlotsNavigator({ onBack }: Props) {
  // Defaults to Wednesday & Slot 1
  const [selectedDay, setSelectedDay] = useState<ShortDay>("Wed");
  const [selectedSlot, setSelectedSlot] = useState<number>(1);
  const [detailRoom, setDetailRoom] = useState<CampusRoom | null>(null);

  const fullDay = DAY_FULL_MAP[selectedDay];
  const slotDef = CAMPUS_SLOTS.find((s) => s.number === selectedSlot) || CAMPUS_SLOTS[0]!;

  // Filter free rooms for active day and slot
  const freeRooms = useMemo(() => {
    return CAMPUS_ROOMS.filter((room) => {
      const daySchedule = getRoomDaySchedule(room, fullDay);
      const slot = daySchedule.find((s) => s.slot === selectedSlot);
      return slot ? slot.isFree : true;
    });
  }, [fullDay, selectedSlot]);

  // Group free rooms by block
  const blockGroups = useMemo(() => {
    const blocksOrder = ["Block A", "Block B", "Block C", "Block D", "Engineering Labs"];
    return blocksOrder.map((blockName) => {
      const roomsInBlock = freeRooms.filter((r) => r.block === blockName);
      const classrooms = roomsInBlock.filter(
        (r) =>
          r.type !== "lab" &&
          !r.code.toLowerCase().includes("lab") &&
          !r.name.toLowerCase().includes("lab") &&
          !r.code.toLowerCase().includes("pod")
      );
      const labs = roomsInBlock.filter(
        (r) =>
          r.type === "lab" ||
          r.code.toLowerCase().includes("lab") ||
          r.name.toLowerCase().includes("lab") ||
          r.code.toLowerCase().includes("pod")
      );

      return {
        blockName,
        theme: BLOCK_THEMES[blockName] || BLOCK_THEMES["Block A"]!,
        classrooms,
        labs,
        total: roomsInBlock.length
      };
    });
  }, [freeRooms]);

  return (
    <div className="min-h-screen bg-background text-ink antialiased transition">
      <div className="mx-auto w-full max-w-md sm:max-w-xl md:max-w-2xl min-h-screen pb-24 sm:pb-16 flex flex-col">
        {/* ================= TOP HERO HEADER ================= */}
        <header className="relative overflow-hidden bg-hero-bg px-5 pt-7 pb-16 text-hero-fg rounded-b-[2.5rem] shadow-md">
          {/* Subtle curved background circles for depth */}
          <div className="pointer-events-none absolute -top-12 -right-12 h-52 w-52 rounded-full bg-hero-fg/10 blur-xl" />
          <div className="pointer-events-none absolute top-4 right-10 h-28 w-28 rounded-full bg-hero-accent/20 blur-md" />

          {/* Top row with circular back button and title */}
          <div className="relative z-10 flex items-center gap-3.5">
            <button
              type="button"
              onClick={onBack}
              aria-label="Back to main explorer"
              className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-hero-fg/15 backdrop-blur-md text-hero-fg transition hover:bg-hero-fg/25 active:scale-95 shadow-xs"
            >
              <ChevronLeft size={24} strokeWidth={2.5} />
            </button>

            <div>
              <h1 className="text-2xl font-bold tracking-tight text-hero-fg leading-tight">
                Free Slots
              </h1>
              <p className="text-xs font-normal text-hero-muted mt-0.5">
                Available rooms by day &amp; slot
              </p>
            </div>
          </div>
        </header>

        {/* ================= FLOATING FILTER CARD ================= */}
        <section
          aria-label="Filter schedule"
          className="relative z-20 -mt-9 mx-4 rounded-3xl bg-panel p-4 shadow-panel border border-line space-y-3"
        >
          {/* Row 1: Day */}
          <div className="flex items-center gap-2">
            <span className="w-10 text-xs font-semibold text-muted shrink-0">
              Day
            </span>
            <div className="flex flex-1 items-center justify-between gap-1 sm:gap-2">
              {DAYS.map((day) => {
                const isSelected = selectedDay === day;
                return (
                  <button
                    key={day}
                    type="button"
                    onClick={() => setSelectedDay(day)}
                    className={`flex-1 rounded-2xl py-2 text-xs font-semibold transition active:scale-95 text-center ${
                      isSelected
                        ? "bg-primary text-on-primary shadow-xs font-bold"
                        : "bg-subtle text-muted hover:bg-surface hover:text-ink"
                    }`}
                  >
                    {day}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Row 2: Slot */}
          <div className="flex items-center gap-2">
            <span className="w-10 text-xs font-semibold text-muted shrink-0">
              Slot
            </span>
            <div className="flex flex-1 items-center justify-between gap-1 sm:gap-2">
              {SLOTS.map((slotNum) => {
                const isSelected = selectedSlot === slotNum;
                return (
                  <button
                    key={slotNum}
                    type="button"
                    onClick={() => setSelectedSlot(slotNum)}
                    className={`flex-1 rounded-2xl py-2 text-xs font-semibold transition active:scale-95 text-center ${
                      isSelected
                        ? "bg-primary text-on-primary shadow-xs font-bold"
                        : "bg-subtle text-muted hover:bg-surface hover:text-ink"
                    }`}
                  >
                    {slotNum}
                  </button>
                );
              })}
            </div>
          </div>
        </section>

        {/* ================= SECTION STATUS BAR ================= */}
        <div className="mt-5 mb-3 px-5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="h-4 w-1 rounded-full bg-primary" />
            <span className="text-xs font-extrabold uppercase tracking-wider text-ink">
              FREE ROOMS
            </span>
          </div>

          <span className="text-xs font-bold text-primary-ink">
            {freeRooms.length} rooms free
          </span>
        </div>

        {/* ================= BLOCK CARDS LIST ================= */}
        <div className="space-y-4 px-4 flex-1">
          {blockGroups.map(({ blockName, theme, classrooms, labs, total }) => {
            if (total === 0) return null;

            return (
              <div
                key={blockName}
                className={`overflow-hidden rounded-3xl border ${theme.borderColor} bg-panel shadow-xs transition`}
              >
                {/* Block Header Banner */}
                <div
                  className={`flex items-center justify-between p-4 ${theme.headerBg} border-b ${theme.borderColor}`}
                >
                  <div className="flex items-center gap-3">
                    {/* Big Letter Avatar Badge */}
                    <div
                      className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ${theme.badgeBg} text-xl font-black shadow-xs`}
                    >
                      {theme.letter}
                    </div>

                    <div>
                      <h2 className={`text-base font-bold leading-tight ${theme.titleColor}`}>
                        {theme.displayName}
                      </h2>
                      <p className="text-xs font-medium text-muted mt-0.5">
                        {classrooms.length} {classrooms.length === 1 ? "room" : "rooms"}
                        {labs.length > 0 &&
                          ` · ${labs.length} ${labs.length === 1 ? "lab" : "labs"}`}
                      </p>
                    </div>
                  </div>

                  {/* Right Header Icon Badge */}
                  <div
                    className={`flex h-9 w-9 items-center justify-center rounded-full ${theme.iconBg} ${theme.iconColor}`}
                  >
                    <DoorClosed size={16} />
                  </div>
                </div>

                {/* Card Content Area */}
                <div className="p-4 space-y-4">
                  {/* Subsection 1: Classrooms */}
                  {classrooms.length > 0 && (
                    <div className="space-y-2.5">
                      <div className="flex items-center gap-1.5 text-[11px] font-extrabold uppercase tracking-wider text-muted">
                        <DoorClosed size={13} className="text-muted" />
                        <span>CLASSROOMS</span>
                      </div>

                      {/* 4-Column Grid */}
                      <div className="grid grid-cols-4 gap-2.5 sm:gap-3">
                        {classrooms.map((room) => (
                          <button
                            key={room.id}
                            type="button"
                            onClick={() => setDetailRoom(room)}
                            className={`border ${theme.itemBorder} ${theme.itemBg} ${theme.itemHoverBg} flex flex-col items-center justify-center rounded-2xl p-2 sm:p-2.5 text-center transition-all duration-150 hover:scale-[1.03] active:scale-95 shadow-2xs group cursor-pointer`}
                          >
                            <span
                              className={`text-xs sm:text-sm font-bold tracking-tight ${theme.roomCodeColor}`}
                            >
                              {room.code}
                            </span>
                            <span
                              className={`mt-1 flex items-center justify-center gap-1 text-[11px] font-medium ${theme.capacityColor}`}
                            >
                              <Users size={11} className="opacity-80" />
                              <span>{room.capacity}</span>
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Subsection 2: Labs */}
                  {labs.length > 0 && (
                    <div className="space-y-2 pt-1">
                      <div
                        className={`flex items-center gap-1.5 text-[11px] font-extrabold uppercase tracking-wider ${theme.titleColor}`}
                      >
                        <FlaskConical size={13} />
                        <span>LABS</span>
                      </div>

                      <div className="flex flex-wrap gap-2.5">
                        {labs.map((lab) => (
                          <button
                            key={lab.id}
                            type="button"
                            onClick={() => setDetailRoom(lab)}
                            className={`border ${theme.labBorder} ${theme.labBg} inline-flex items-center gap-2 rounded-2xl px-3.5 py-2 text-xs font-bold ${theme.labText} transition hover:scale-[1.02] active:scale-95 shadow-2xs cursor-pointer`}
                          >
                            <FlaskConical size={13} className="shrink-0" />
                            <span>{lab.code}</span>
                            <span className="ml-1 flex items-center gap-1 text-[11px] font-normal opacity-85">
                              <Users size={10} />
                              <span>{lab.capacity}</span>
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}

          {freeRooms.length === 0 && (
            <div className="rounded-3xl border border-line bg-panel p-8 text-center text-muted shadow-xs">
              <p className="text-sm font-semibold text-ink">
                No free rooms found for {fullDay} (Slot {selectedSlot})
              </p>
              <p className="mt-1 text-xs text-muted">
                All campus rooms in this time period have scheduled classes. Try selecting another slot or day.
              </p>
            </div>
          )}
        </div>

        {/* ================= DETAIL MODAL / BOTTOM SHEET ================= */}
        {detailRoom && (
          <div
            role="dialog"
            aria-modal="true"
            className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-overlay/65 backdrop-blur-xs p-0 sm:p-4 animate-in fade-in duration-200"
            onClick={() => setDetailRoom(null)}
          >
            <div
              className="relative w-full max-w-md rounded-t-3xl sm:rounded-3xl border border-line bg-panel p-6 text-ink shadow-2xl space-y-4 animate-in slide-in-from-bottom duration-200"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Drag indicator for mobile */}
              <div className="mx-auto -mt-2 mb-2 h-1.5 w-12 rounded-full bg-subtle sm:hidden" />

              {/* Modal Top */}
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="flex h-2.5 w-2.5 rounded-full bg-success animate-pulse" />
                    <h3 className="text-lg font-bold text-ink">
                      {detailRoom.code}
                    </h3>
                    <span className="rounded-full bg-success-soft border border-success/35 px-2.5 py-0.5 text-2xs font-extrabold text-success-ink">
                      Available Now
                    </span>
                  </div>
                  <p className="text-xs text-muted mt-0.5">{detailRoom.name}</p>
                </div>

                <button
                  type="button"
                  onClick={() => setDetailRoom(null)}
                  aria-label="Close room details"
                  className="flex h-8 w-8 items-center justify-center rounded-full bg-subtle text-muted hover:bg-surface hover:text-ink transition"
                >
                  <X size={16} />
                </button>
              </div>

              {/* Badges Info */}
              <div className="grid grid-cols-2 gap-2.5 text-xs">
                <div className="flex items-center gap-2 rounded-2xl bg-surface border border-line p-3">
                  <MapPin size={16} className="text-primary-ink shrink-0" />
                  <div>
                    <span className="block text-[10px] uppercase font-bold text-muted">Location</span>
                    <span className="font-semibold text-ink">{detailRoom.block} · {detailRoom.floor}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 rounded-2xl bg-surface border border-line p-3">
                  <Users size={16} className="text-primary-ink shrink-0" />
                  <div>
                    <span className="block text-[10px] uppercase font-bold text-muted">Seating Capacity</span>
                    <span className="font-semibold text-ink">{detailRoom.capacity} Students</span>
                  </div>
                </div>
              </div>

              {/* Active Slot Telemetry */}
              <div className="rounded-2xl bg-primary-soft/60 border border-primary/25 p-3.5 space-y-1">
                <div className="flex items-center gap-1.5 text-xs font-bold text-primary-ink">
                  <Clock size={14} className="text-primary-ink" />
                  <span>{fullDay} · Slot {selectedSlot}</span>
                </div>
                <p className="text-xs text-primary-ink">
                  Time Window: <strong className="font-semibold">{slotDef.timeRange}</strong>
                </p>
                <p className="text-xs text-muted mt-1">
                  Status: <span className="font-semibold text-success-ink">Open for walk-in study and group discussions.</span>
                </p>
              </div>

              {/* Equipment Amenities */}
              <div>
                <span className="block text-[11px] font-extrabold uppercase tracking-wider text-muted mb-2">
                  Room Equipment
                </span>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className={`flex items-center gap-2 rounded-xl p-2.5 border ${detailRoom.equipment.hasWifi ? "bg-surface border-line text-ink" : "bg-surface/50 border-line/60 text-muted/60"}`}>
                    <Wifi size={14} className={detailRoom.equipment.hasWifi ? "text-primary-ink" : "text-muted/45"} />
                    <span>Campus Wi-Fi</span>
                  </div>
                  <div className={`flex items-center gap-2 rounded-xl p-2.5 border ${detailRoom.equipment.hasAC ? "bg-surface border-line text-ink" : "bg-surface/50 border-line/60 text-muted/60"}`}>
                    <Wind size={14} className={detailRoom.equipment.hasAC ? "text-secondary-ink" : "text-muted/45"} />
                    <span>Air Conditioned</span>
                  </div>
                  <div className={`flex items-center gap-2 rounded-xl p-2.5 border ${detailRoom.equipment.hasProjector ? "bg-surface border-line text-ink" : "bg-surface/50 border-line/60 text-muted/60"}`}>
                    <Tv size={14} className={detailRoom.equipment.hasProjector ? "text-accent-ink" : "text-muted/45"} />
                    <span>Smart Projector</span>
                  </div>
                  <div className={`flex items-center gap-2 rounded-xl p-2.5 border ${detailRoom.equipment.hasPowerSockets ? "bg-surface border-line text-ink" : "bg-surface/50 border-line/60 text-muted/60"}`}>
                    <Zap size={14} className={detailRoom.equipment.hasPowerSockets ? "text-warning-ink" : "text-muted/45"} />
                    <span>Power Sockets</span>
                  </div>
                </div>
              </div>

              {/* Dismiss button */}
              <button
                type="button"
                onClick={() => setDetailRoom(null)}
                className="w-full rounded-2xl bg-primary py-3 text-xs font-bold text-on-primary shadow-xs transition hover:bg-primary-hover active:scale-95"
              >
                Close Details
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
