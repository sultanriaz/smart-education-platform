import { useState, useMemo, useEffect } from "react";
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
  X,
  Search,
  SlidersHorizontal,
  RotateCcw
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
type RoomTypeFilter = "all" | "classroom" | "lab";

const DAYS: ShortDay[] = ["Mon", "Tue", "Wed", "Thu", "Fri"];
const SLOTS = [1, 2, 3, 4, 5];

const DAY_FULL_MAP: Record<ShortDay, string> = {
  Mon: "Monday",
  Tue: "Tuesday",
  Wed: "Wednesday",
  Thu: "Thursday",
  Fri: "Friday"
};

const BLOCK_FILTER_OPTIONS: Array<{ value: string; label: string }> = [
  { value: "All", label: "All Blocks" },
  { value: "Block A", label: "A Block" },
  { value: "Block B", label: "B Block" },
  { value: "Block C", label: "C Block" },
  { value: "Block D", label: "D Block" },
  { value: "Engineering Labs", label: "Engg. Labs" }
];

const SEAT_OPTIONS: Array<{ value: number; label: string }> = [
  { value: 0, label: "Any Size" },
  { value: 40, label: "40+ seats" },
  { value: 55, label: "55+ seats" },
  { value: 65, label: "65+ seats" }
];

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

function isLabRoom(room: CampusRoom): boolean {
  return (
    room.type === "lab" ||
    room.code.toLowerCase().includes("lab") ||
    room.name.toLowerCase().includes("lab") ||
    room.code.toLowerCase().includes("pod")
  );
}

function matchesSearchText(room: CampusRoom, query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;

  const blockLower = room.block.toLowerCase();
  const blockAlias = blockLower.startsWith("block ")
    ? `${blockLower.replace("block ", "")} block`
    : blockLower;

  const amenityWords: string[] = [];
  if (room.equipment.hasWifi) amenityWords.push("wifi", "wi-fi");
  if (room.equipment.hasAC) amenityWords.push("ac", "air conditioned");
  if (room.equipment.hasProjector) amenityWords.push("projector");
  if (room.equipment.hasPowerSockets) amenityWords.push("sockets", "power");

  return (
    room.code.toLowerCase().includes(q) ||
    room.name.toLowerCase().includes(q) ||
    blockLower.includes(q) ||
    blockAlias.includes(q) ||
    room.floor.toLowerCase().includes(q) ||
    (isLabRoom(room) ? "lab" : "classroom").includes(q) ||
    amenityWords.some((word) => word.includes(q))
  );
}

export function FreeSlotsNavigator({ onBack }: Props) {
  const [selectedDay, setSelectedDay] = useState<ShortDay>("Wed");
  const [selectedSlot, setSelectedSlot] = useState<number>(1);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedBlock, setSelectedBlock] = useState<string>("All");
  const [roomType, setRoomType] = useState<RoomTypeFilter>("all");
  const [minSeats, setMinSeats] = useState<number>(0);
  const [needWifi, setNeedWifi] = useState<boolean>(false);
  const [needAC, setNeedAC] = useState<boolean>(false);
  const [needProjector, setNeedProjector] = useState<boolean>(false);
  const [needSockets, setNeedSockets] = useState<boolean>(false);
  const [showOptions, setShowOptions] = useState<boolean>(false);
  const [detailRoom, setDetailRoom] = useState<CampusRoom | null>(null);

  useEffect(() => {
    if (!detailRoom) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setDetailRoom(null);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [detailRoom]);

  const fullDay = DAY_FULL_MAP[selectedDay];
  const slotDef = CAMPUS_SLOTS.find((s) => s.number === selectedSlot) || CAMPUS_SLOTS[0]!;

  const extraOptionsCount =
    (roomType !== "all" ? 1 : 0) +
    (minSeats > 0 ? 1 : 0) +
    (needWifi ? 1 : 0) +
    (needAC ? 1 : 0) +
    (needProjector ? 1 : 0) +
    (needSockets ? 1 : 0);

  const hasActiveFilters =
    searchQuery.trim().length > 0 || selectedBlock !== "All" || extraOptionsCount > 0;

  const resetSearchAndFilters = () => {
    setSearchQuery("");
    setSelectedBlock("All");
    setRoomType("all");
    setMinSeats(0);
    setNeedWifi(false);
    setNeedAC(false);
    setNeedProjector(false);
    setNeedSockets(false);
  };

  // Filter free rooms for active day, slot, and user search options
  const freeRooms = useMemo(() => {
    return CAMPUS_ROOMS.filter((room) => {
      const daySchedule = getRoomDaySchedule(room, fullDay);
      const slot = daySchedule.find((s) => s.slot === selectedSlot);
      if (!(slot ? slot.isFree : true)) return false;

      if (selectedBlock !== "All" && room.block !== selectedBlock) return false;
      if (roomType === "classroom" && isLabRoom(room)) return false;
      if (roomType === "lab" && !isLabRoom(room)) return false;
      if (minSeats > 0 && room.capacity < minSeats) return false;
      if (needWifi && !room.equipment.hasWifi) return false;
      if (needAC && !room.equipment.hasAC) return false;
      if (needProjector && !room.equipment.hasProjector) return false;
      if (needSockets && !room.equipment.hasPowerSockets) return false;
      if (!matchesSearchText(room, searchQuery)) return false;

      return true;
    });
  }, [
    fullDay,
    selectedSlot,
    selectedBlock,
    roomType,
    minSeats,
    needWifi,
    needAC,
    needProjector,
    needSockets,
    searchQuery
  ]);

  // Group free rooms by block
  const blockGroups = useMemo(() => {
    const blocksOrder = ["Block A", "Block B", "Block C", "Block D", "Engineering Labs"];
    return blocksOrder.map((blockName) => {
      const roomsInBlock = freeRooms.filter((r) => r.block === blockName);
      const classrooms = roomsInBlock.filter((r) => !isLabRoom(r));
      const labs = roomsInBlock.filter((r) => isLabRoom(r));

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
          <div className="pointer-events-none absolute -top-12 -right-12 h-52 w-52 rounded-full bg-hero-fg/10 blur-xl" />
          <div className="pointer-events-none absolute top-4 right-10 h-28 w-28 rounded-full bg-hero-accent/20 blur-md" />

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

        {/* ================= FLOATING FILTER & SEARCH CARD ================= */}
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
                    aria-pressed={isSelected}
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

          {/* Row 2: Slot + Slot Clock Time */}
          <div className="space-y-1.5">
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
                      aria-pressed={isSelected}
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
            <p className="pl-12 text-[11px] font-medium text-muted">
              {fullDay} · Slot {selectedSlot}: {slotDef.timeRange}
            </p>
          </div>

          {/* Row 3: Search Input + More Search Options Button */}
          <div className="flex items-center gap-2 pt-1 border-t border-line/70">
            <div className="relative flex-1 min-w-0">
              <Search
                size={14}
                className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted"
              />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                aria-label="Search free rooms"
                placeholder="Search rooms..."
                className="w-full rounded-2xl border border-line bg-surface py-2 pl-8 pr-8 text-xs text-ink placeholder:text-muted focus:outline-hidden focus:ring-2 focus:ring-primary/40"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  aria-label="Clear room search"
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 rounded-full p-0.5 text-muted hover:text-ink"
                >
                  <X size={13} />
                </button>
              )}
            </div>

            <button
              type="button"
              aria-expanded={showOptions}
              onClick={() => setShowOptions((prev) => !prev)}
              className={`inline-flex shrink-0 items-center gap-1.5 rounded-2xl border px-3 py-2 text-xs font-bold transition ${
                showOptions || extraOptionsCount > 0
                  ? "border-primary bg-primary-soft text-primary-ink"
                  : "border-line bg-surface text-ink hover:border-primary/50"
              }`}
            >
              <SlidersHorizontal size={13} />
              <span>Options{extraOptionsCount > 0 ? ` (${extraOptionsCount})` : ""}</span>
            </button>
          </div>

          {/* Row 4: Quick Block Filter Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-0.5" role="group" aria-label="Filter by block">
            {BLOCK_FILTER_OPTIONS.map((opt) => {
              const active = selectedBlock === opt.value;
              return (
                <button
                  key={opt.value}
                  type="button"
                  aria-pressed={active}
                  onClick={() => setSelectedBlock(opt.value)}
                  className={`shrink-0 rounded-xl px-2.5 py-1.5 text-[11px] font-semibold transition cursor-pointer ${
                    active
                      ? "bg-primary text-on-primary shadow-2xs"
                      : "bg-subtle/75 text-muted hover:text-ink"
                  }`}
                >
                  {opt.label}
                </button>
              );
            })}
          </div>

          {/* Expandable More Search Options */}
          {showOptions && (
            <div className="rounded-2xl border border-line bg-surface p-3.5 space-y-3 text-xs">
              {/* Room Type */}
              <div className="space-y-1.5">
                <span className="block text-[11px] font-bold text-muted">Room Type</span>
                <div className="flex flex-wrap gap-1.5" role="group" aria-label="Room type">
                  {[
                    { value: "all", label: "All Rooms" },
                    { value: "classroom", label: "Classrooms" },
                    { value: "lab", label: "Labs" }
                  ].map((item) => {
                    const active = roomType === item.value;
                    return (
                      <button
                        key={item.value}
                        type="button"
                        aria-pressed={active}
                        onClick={() => setRoomType(item.value as RoomTypeFilter)}
                        className={`rounded-xl px-3 py-1.5 font-semibold transition ${
                          active
                            ? "bg-primary text-on-primary"
                            : "border border-line bg-panel text-muted hover:text-ink"
                        }`}
                      >
                        {item.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Minimum Seats */}
              <div className="space-y-1.5">
                <span className="block text-[11px] font-bold text-muted">Seats Needed</span>
                <div className="flex flex-wrap gap-1.5" role="group" aria-label="Minimum seats">
                  {SEAT_OPTIONS.map((opt) => {
                    const active = minSeats === opt.value;
                    return (
                      <button
                        key={opt.value}
                        type="button"
                        aria-pressed={active}
                        onClick={() => setMinSeats(opt.value)}
                        className={`rounded-xl px-3 py-1.5 font-semibold transition ${
                          active
                            ? "bg-primary text-on-primary"
                            : "border border-line bg-panel text-muted hover:text-ink"
                        }`}
                      >
                        {opt.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Room Facilities */}
              <div className="space-y-1.5">
                <span className="block text-[11px] font-bold text-muted">Room Features</span>
                <div className="flex flex-wrap gap-1.5" role="group" aria-label="Room features">
                  {[
                    { key: "wifi", label: "Wi-Fi", active: needWifi, toggle: () => setNeedWifi((v) => !v) },
                    { key: "ac", label: "AC", active: needAC, toggle: () => setNeedAC((v) => !v) },
                    { key: "projector", label: "Projector", active: needProjector, toggle: () => setNeedProjector((v) => !v) },
                    { key: "sockets", label: "Power Sockets", active: needSockets, toggle: () => setNeedSockets((v) => !v) }
                  ].map((feat) => (
                    <button
                      key={feat.key}
                      type="button"
                      aria-pressed={feat.active}
                      onClick={feat.toggle}
                      className={`rounded-xl px-3 py-1.5 font-semibold transition ${
                        feat.active
                          ? "bg-secondary text-secondary-fg"
                          : "border border-line bg-panel text-muted hover:text-ink"
                      }`}
                    >
                      {feat.label}
                    </button>
                  ))}
                </div>
              </div>

              {hasActiveFilters && (
                <div className="pt-1 border-t border-line flex justify-end">
                  <button
                    type="button"
                    onClick={resetSearchAndFilters}
                    className="inline-flex items-center gap-1 text-xs font-bold text-primary-ink hover:underline"
                  >
                    <RotateCcw size={12} />
                    <span>Clear All Filters</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </section>

        {/* ================= SECTION STATUS BAR ================= */}
        <div className="mt-5 mb-3 px-5 flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="h-4 w-1 rounded-full bg-primary" />
            <span className="text-xs font-extrabold uppercase tracking-wider text-ink">
              FREE ROOMS
            </span>
          </div>

          <div className="flex items-center gap-3">
            {hasActiveFilters && (
              <button
                type="button"
                onClick={resetSearchAndFilters}
                className="text-xs font-semibold text-muted hover:text-ink underline"
              >
                Reset
              </button>
            )}
            <span className="text-xs font-bold text-primary-ink">
              {freeRooms.length} {freeRooms.length === 1 ? "room free" : "rooms free"}
            </span>
          </div>
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
            <div className="rounded-3xl border border-line bg-panel p-8 text-center text-muted shadow-xs space-y-3">
              <p className="text-sm font-semibold text-ink">
                {hasActiveFilters
                  ? "No free rooms match your search"
                  : `No free rooms found for ${fullDay} (Slot ${selectedSlot})`}
              </p>
              <p className="text-xs text-muted">
                {hasActiveFilters
                  ? "Try clearing your search text or changing the selected block, size, or room features."
                  : "All campus rooms in this period have scheduled classes. Try choosing another slot or day."}
              </p>
              {hasActiveFilters && (
                <button
                  type="button"
                  onClick={resetSearchAndFilters}
                  className="inline-flex items-center gap-1.5 rounded-2xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition"
                >
                  <RotateCcw size={13} />
                  <span>Clear Search &amp; Filters</span>
                </button>
              )}
            </div>
          )}
        </div>

        {/* ================= DETAIL MODAL / BOTTOM SHEET ================= */}
        {detailRoom && (
          <div
            role="dialog"
            aria-modal="true"
            className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-overlay/65 backdrop-blur-xs p-0 sm:p-4"
            onClick={() => setDetailRoom(null)}
          >
            <div
              className="relative w-full max-w-md rounded-t-3xl sm:rounded-3xl border border-line bg-panel p-6 text-ink shadow-2xl space-y-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="mx-auto -mt-2 mb-2 h-1.5 w-12 rounded-full bg-subtle sm:hidden" />

              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="flex h-2.5 w-2.5 rounded-full bg-success" />
                    <h3 className="text-lg font-bold text-ink">
                      {detailRoom.code}
                    </h3>
                    <span className="rounded-full bg-success-soft border border-success/35 px-2.5 py-0.5 text-2xs font-extrabold text-success-ink">
                      Free in this slot
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
                    <span className="block text-[10px] uppercase font-bold text-muted">Seats</span>
                    <span className="font-semibold text-ink">{detailRoom.capacity} Students</span>
                  </div>
                </div>
              </div>

              <div className="rounded-2xl bg-primary-soft/60 border border-primary/25 p-3.5 space-y-1">
                <div className="flex items-center gap-1.5 text-xs font-bold text-primary-ink">
                  <Clock size={14} className="text-primary-ink" />
                  <span>{fullDay} · Slot {selectedSlot}</span>
                </div>
                <p className="text-xs text-primary-ink">
                  Time: <strong className="font-semibold">{slotDef.timeRange}</strong>
                </p>
                <p className="text-xs text-muted mt-1">
                  Open for self-study and group work during this time.
                </p>
              </div>

              <div>
                <span className="block text-[11px] font-extrabold uppercase tracking-wider text-muted mb-2">
                  Room Features
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
                    <span>Projector</span>
                  </div>
                  <div className={`flex items-center gap-2 rounded-xl p-2.5 border ${detailRoom.equipment.hasPowerSockets ? "bg-surface border-line text-ink" : "bg-surface/50 border-line/60 text-muted/60"}`}>
                    <Zap size={14} className={detailRoom.equipment.hasPowerSockets ? "text-warning-ink" : "text-muted/45"} />
                    <span>Power Sockets</span>
                  </div>
                </div>
              </div>

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
