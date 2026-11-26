import { useState, useMemo, useEffect } from "react";
import {
  ChevronLeft,
  ChevronRight,
  ChevronUp,
  ChevronDown,
  DoorClosed,
  Users,
  Search,
  X,
  MapPin,
  Wifi,
  Wind,
  Tv
} from "lucide-react";

import {
  BLOCK_CLASSROOMS,
  type BlockClassroomItem,
  type ClassroomBlockName,
  type ClassroomFloorName
} from "../../features/campushub/campus-hub-data";

const BLOCK_ORDER: ClassroomBlockName[] = ["Block A", "Block B", "Block C"];
const FLOOR_ORDER: ClassroomFloorName[] = ["Ground Floor", "1st Floor", "2nd Floor", "3rd Floor"];

const FLOOR_DISPLAY_LABEL: Record<ClassroomFloorName, string> = {
  "Ground Floor": "G- Floor",
  "1st Floor": "1st- Floor",
  "2nd Floor": "2nd- Floor",
  "3rd Floor": "3rd- Floor"
};

interface FloorTheme {
  headerBg: string;
  borderColor: string;
  badgeBg: string;
  titleColor: string;
  chevronBg: string;
  tileBg: string;
  tileBorder: string;
  tileHoverBg: string;
  codeColor: string;
  capColor: string;
}

const FLOOR_THEMES: Record<ClassroomFloorName, FloorTheme> = {
  "Ground Floor": {
    headerBg: "bg-warning-soft/65",
    borderColor: "border-warning/25",
    badgeBg: "bg-warning text-warning-fg",
    titleColor: "text-warning-ink",
    chevronBg: "bg-warning-soft text-warning-ink border border-warning/25",
    tileBg: "bg-warning-soft/35",
    tileBorder: "border-warning/25",
    tileHoverBg: "hover:bg-warning-soft/75",
    codeColor: "text-warning-ink",
    capColor: "text-warning-ink/85"
  },
  "1st Floor": {
    headerBg: "bg-primary-soft/65",
    borderColor: "border-primary/20",
    badgeBg: "bg-primary text-on-primary",
    titleColor: "text-primary-ink",
    chevronBg: "bg-primary-soft text-primary-ink border border-primary/20",
    tileBg: "bg-primary-soft/35",
    tileBorder: "border-primary/20",
    tileHoverBg: "hover:bg-primary-soft/75",
    codeColor: "text-primary-ink",
    capColor: "text-primary-ink/85"
  },
  "2nd Floor": {
    headerBg: "bg-secondary-soft/65",
    borderColor: "border-secondary/25",
    badgeBg: "bg-secondary text-secondary-fg",
    titleColor: "text-secondary-ink",
    chevronBg: "bg-secondary-soft text-secondary-ink border border-secondary/25",
    tileBg: "bg-secondary-soft/35",
    tileBorder: "border-secondary/25",
    tileHoverBg: "hover:bg-secondary-soft/75",
    codeColor: "text-secondary-ink",
    capColor: "text-secondary-ink/85"
  },
  "3rd Floor": {
    headerBg: "bg-success-soft/65",
    borderColor: "border-success/25",
    badgeBg: "bg-success text-success-fg",
    titleColor: "text-success-ink",
    chevronBg: "bg-success-soft text-success-ink border border-success/25",
    tileBg: "bg-success-soft/35",
    tileBorder: "border-success/25",
    tileHoverBg: "hover:bg-success-soft/75",
    codeColor: "text-success-ink",
    capColor: "text-success-ink/85"
  }
};

const BLOCK_CARD_ACCENTS: Record<ClassroomBlockName, { letter: string; badgeBg: string; ringHover: string }> = {
  "Block A": { letter: "A", badgeBg: "bg-warning text-warning-fg", ringHover: "hover:border-warning/60" },
  "Block B": { letter: "B", badgeBg: "bg-primary text-on-primary", ringHover: "hover:border-primary/60" },
  "Block C": { letter: "C", badgeBg: "bg-secondary text-secondary-fg", ringHover: "hover:border-secondary/60" }
};

function matchesClassroomQuery(room: BlockClassroomItem, query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  const blockAlias = `${room.block.toLowerCase()} ${room.block.toLowerCase().replace("block ", "")} block`;
  const floorAlias = `${room.floor.toLowerCase()} ${FLOOR_DISPLAY_LABEL[room.floor].toLowerCase()}`;
  return (
    room.roomCode.toLowerCase().includes(q) ||
    room.name.toLowerCase().includes(q) ||
    blockAlias.includes(q) ||
    floorAlias.includes(q)
  );
}

/** Displays Block A/B/C selection and floor-wise classroom grids matching the mobile reference UI. */
export function BlockClassroomsBrowser({ onBack }: { onBack?: () => void } = {}) {
  const [selectedBlock, setSelectedBlock] = useState<ClassroomBlockName | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [collapsedFloors, setCollapsedFloors] = useState<Record<string, boolean>>({});
  const [detailRoom, setDetailRoom] = useState<BlockClassroomItem | null>(null);

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

  const blockSummaries = useMemo(() => {
    return BLOCK_ORDER.map((blockName) => {
      const rooms = BLOCK_CLASSROOMS.filter((r) => r.block === blockName);
      const floors = FLOOR_ORDER.filter((flr) => rooms.some((r) => r.floor === flr));
      return {
        blockName,
        totalRooms: rooms.length,
        floorCount: floors.length,
        floorLabels: floors.map((flr) => FLOOR_DISPLAY_LABEL[flr]).join(", ")
      };
    });
  }, []);

  const searchMatches = useMemo(() => {
    if (!searchQuery.trim()) return [];
    return BLOCK_CLASSROOMS.filter((r) => {
      if (selectedBlock && r.block !== selectedBlock) return false;
      return matchesClassroomQuery(r, searchQuery);
    });
  }, [selectedBlock, searchQuery]);

  const activeBlockTotal = useMemo(() => {
    if (!selectedBlock) return 0;
    return BLOCK_CLASSROOMS.filter((r) => r.block === selectedBlock).length;
  }, [selectedBlock]);

  const activeBlockFloors = useMemo(() => {
    if (!selectedBlock) return [];
    const blockRooms = BLOCK_CLASSROOMS.filter(
      (r) => r.block === selectedBlock && matchesClassroomQuery(r, searchQuery)
    );
    return FLOOR_ORDER.map((floorName) => ({
      floorName,
      displayLabel: FLOOR_DISPLAY_LABEL[floorName],
      theme: FLOOR_THEMES[floorName],
      rooms: blockRooms.filter((r) => r.floor === floorName)
    })).filter((grp) => grp.rooms.length > 0);
  }, [selectedBlock, searchQuery]);

  const selectBlock = (blk: ClassroomBlockName) => {
    setSelectedBlock(blk);
    setCollapsedFloors({});
    setSearchQuery("");
  };

  const toggleFloor = (floorKey: string) => {
    setCollapsedFloors((prev) => ({ ...prev, [floorKey]: !prev[floorKey] }));
  };

  return (
    <div className="space-y-5">
      {/* ================= VIEW 1: PICK A BLOCK (OR SEARCH ACROSS ALL BLOCKS) ================= */}
      {!selectedBlock ? (
        <div className="space-y-5">
          {onBack && (
            <div className="flex items-center justify-between gap-3">
              <button
                type="button"
                onClick={onBack}
                className="inline-flex items-center gap-2 rounded-2xl border border-line bg-panel px-3.5 py-2 text-xs font-bold text-ink hover:border-primary transition cursor-pointer shadow-2xs"
              >
                <ChevronLeft size={16} />
                <span>Back to Campus Portal</span>
              </button>
              <span className="text-xs font-bold text-muted">Class Rooms</span>
            </div>
          )}

          {/* Simple Search Bar */}
          <div className="rounded-2xl border border-line bg-panel p-4 shadow-2xs space-y-3">
            <div className="relative">
              <Search
                size={15}
                className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-muted"
              />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                aria-label="Search classrooms"
                placeholder="Search classrooms by room number, block, or floor (e.g. A-1, Block B, 1st Floor)..."
                className="w-full rounded-xl border border-line bg-surface py-2.5 pl-9 pr-8 text-xs text-ink placeholder:text-muted focus:outline-hidden focus:ring-2 focus:ring-primary/40"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  aria-label="Clear classroom search"
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-ink"
                >
                  <X size={14} />
                </button>
              )}
            </div>
          </div>

          {/* Search Matches View OR Block Selector Cards */}
          {searchQuery.trim() ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between px-1">
                <div className="flex items-center gap-2">
                  <span className="h-4 w-1 rounded-full bg-primary" />
                  <span className="text-xs font-extrabold uppercase tracking-wider text-ink">
                    SEARCH RESULTS
                  </span>
                </div>
                <span className="text-xs font-bold text-primary-ink">
                  {searchMatches.length} {searchMatches.length === 1 ? "room" : "rooms"} found
                </span>
              </div>

              {searchMatches.length === 0 ? (
                <div className="rounded-3xl border border-line bg-panel p-8 text-center space-y-3">
                  <p className="text-sm font-bold text-ink">No classrooms found</p>
                  <p className="text-xs text-muted">
                    Try another room number, floor, or select Block A, Block B, or Block C below.
                  </p>
                  <button
                    type="button"
                    onClick={() => setSearchQuery("")}
                    className="rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition"
                  >
                    Clear Search
                  </button>
                </div>
              ) : (
                <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-3">
                  {searchMatches.map((room) => {
                    const theme = FLOOR_THEMES[room.floor];
                    return (
                      <button
                        key={room.id}
                        type="button"
                        onClick={() => setDetailRoom(room)}
                        className={`rounded-2xl border ${theme.tileBorder} ${theme.tileBg} ${theme.tileHoverBg} p-3 text-center transition hover:scale-[1.02] cursor-pointer space-y-1`}
                      >
                        <p className={`text-sm font-bold ${theme.codeColor}`}>{room.roomCode}</p>
                        <p className="text-[11px] font-medium text-muted">
                          {room.block} · {FLOOR_DISPLAY_LABEL[room.floor]}
                        </p>
                        <p className={`flex items-center justify-center gap-1 text-xs font-semibold ${theme.capColor}`}>
                          <Users size={11} />
                          <span>{room.capacity}</span>
                        </p>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center gap-2 px-1">
                <span className="h-4 w-1 rounded-full bg-primary" />
                <h3 className="text-xs font-extrabold uppercase tracking-wider text-ink">
                  SELECT A BLOCK TO VIEW CLASSROOMS
                </h3>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                {blockSummaries.map((blk) => {
                  const accent = BLOCK_CARD_ACCENTS[blk.blockName];
                  return (
                    <button
                      key={blk.blockName}
                      type="button"
                      onClick={() => selectBlock(blk.blockName)}
                      className={`rounded-3xl border border-line bg-panel p-5 text-left shadow-2xs transition flex items-center justify-between gap-4 cursor-pointer group ${accent.ringHover} hover:shadow-sm`}
                    >
                      <div className="flex items-center gap-3.5 min-w-0">
                        <span
                          className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl text-xl font-black shadow-xs ${accent.badgeBg}`}
                        >
                          {accent.letter}
                        </span>
                        <div className="min-w-0">
                          <h4 className="font-bold text-base text-ink">{blk.blockName}</h4>
                          <p className="text-xs font-semibold text-primary-ink mt-0.5">
                            {blk.totalRooms} Classrooms · {blk.floorCount} Floors
                          </p>
                          <p className="text-[11px] text-muted truncate mt-0.5">{blk.floorLabels}</p>
                        </div>
                      </div>

                      <ChevronRight
                        size={18}
                        className="shrink-0 text-muted group-hover:text-ink group-hover:translate-x-0.5 transition"
                      />
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      ) : (
        /* ================= VIEW 2: SELECTED BLOCK FLOOR-WISE CLASSROOMS (MATCHING SCREENSHOT) ================= */
        <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
          {/* Rounded Top Hero Banner */}
          <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-8 text-hero-fg rounded-b-[2rem] shadow-md">
            <div className="pointer-events-none absolute -top-10 -right-10 h-44 w-44 rounded-full bg-hero-fg/10 blur-xl" />
            <div className="pointer-events-none absolute top-4 right-12 h-24 w-24 rounded-full bg-hero-accent/20 blur-md" />

            <div className="relative z-10 flex items-center justify-between gap-3">
              <div className="flex items-center gap-3 min-w-0">
                <button
                  type="button"
                  onClick={() => {
                    setSelectedBlock(null);
                    setSearchQuery("");
                  }}
                  aria-label="Back to blocks"
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-hero-fg/15 backdrop-blur-md text-hero-fg hover:bg-hero-fg/25 transition cursor-pointer"
                >
                  <ChevronLeft size={22} strokeWidth={2.5} />
                </button>

                <div className="min-w-0">
                  <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-hero-fg leading-tight">
                    Class Rooms
                  </h3>
                  <p className="text-xs text-hero-muted mt-0.5">
                    {selectedBlock} · Classrooms &amp; seating capacity
                  </p>
                </div>
              </div>

              <span className="shrink-0 rounded-full border border-hero-fg/25 bg-hero-fg/15 px-3.5 py-1.5 text-xs sm:text-sm font-bold text-hero-fg whitespace-nowrap">
                {activeBlockTotal} Rooms
              </span>
            </div>
          </div>

          {/* Quick Block Switch & Search inside Block */}
          <div className="px-4 pt-4 space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="inline-flex flex-wrap gap-1.5" role="group" aria-label="Switch block">
                {BLOCK_ORDER.map((blk) => {
                  const active = selectedBlock === blk;
                  return (
                    <button
                      key={blk}
                      type="button"
                      aria-pressed={active}
                      onClick={() => selectBlock(blk)}
                      className={`rounded-xl px-3 py-1.5 text-xs font-bold transition cursor-pointer ${
                        active
                          ? "bg-primary text-on-primary shadow-2xs"
                          : "border border-line bg-panel text-muted hover:text-ink"
                      }`}
                    >
                      {blk}
                    </button>
                  );
                })}
              </div>

              <div className="relative w-full sm:w-52">
                <Search
                  size={13}
                  className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-muted"
                />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  aria-label={`Search classrooms in ${selectedBlock}`}
                  placeholder={`Search in ${selectedBlock}...`}
                  className="w-full rounded-xl border border-line bg-panel py-1.5 pl-8 pr-7 text-xs text-ink placeholder:text-muted focus:outline-hidden focus:ring-2 focus:ring-primary/40"
                />
                {searchQuery && (
                  <button
                    type="button"
                    onClick={() => setSearchQuery("")}
                    aria-label="Clear room filter"
                    className="absolute right-2 top-1/2 -translate-y-1/2 text-muted hover:text-ink"
                  >
                    <X size={12} />
                  </button>
                )}
              </div>
            </div>

            {/* AVAILABLE ROOMS header strip matching screenshot */}
            <div className="flex items-center justify-between pt-1">
              <div className="flex items-center gap-2">
                <span className="h-4 w-1 rounded-full bg-primary" />
                <span className="text-xs font-extrabold uppercase tracking-wider text-ink">
                  AVAILABLE ROOMS
                </span>
              </div>
              {searchQuery.trim() && (
                <span className="text-xs font-semibold text-primary-ink">
                  {activeBlockFloors.reduce((acc, f) => acc + f.rooms.length, 0)} matching
                </span>
              )}
            </div>
          </div>

          {/* Floor-by-Floor Collapsible Cards */}
          <div className="p-4 space-y-4">
            {activeBlockFloors.map(({ floorName, displayLabel, theme, rooms }) => {
              const blockLetter = BLOCK_CARD_ACCENTS[selectedBlock].letter;
              const isCollapsed = Boolean(collapsedFloors[floorName]);

              return (
                <div
                  key={floorName}
                  className={`overflow-hidden rounded-3xl border ${theme.borderColor} bg-panel shadow-xs`}
                >
                  {/* Colored Floor Header Band */}
                  <button
                    type="button"
                    aria-expanded={!isCollapsed}
                    onClick={() => toggleFloor(floorName)}
                    className={`w-full flex items-center justify-between p-4 ${theme.headerBg} border-b ${theme.borderColor} text-left cursor-pointer`}
                  >
                    <div className="flex items-center gap-3.5">
                      <span
                        className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl text-xl font-black shadow-xs ${theme.badgeBg}`}
                      >
                        {blockLetter}
                      </span>

                      <div>
                        <h4 className={`text-base font-bold leading-tight ${theme.titleColor}`}>
                          {displayLabel}
                        </h4>
                        <p className="text-xs font-medium text-muted mt-0.5">
                          {rooms.length} {rooms.length === 1 ? "room" : "rooms"}
                        </p>
                      </div>
                    </div>

                    <span
                      className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${theme.chevronBg}`}
                      aria-hidden="true"
                    >
                      {isCollapsed ? <ChevronDown size={18} /> : <ChevronUp size={18} />}
                    </span>
                  </button>

                  {/* Classroom Tiles Grid (ONLY Classrooms) */}
                  {!isCollapsed && (
                    <div className="p-4 space-y-3">
                      <div className={`flex items-center gap-1.5 text-[11px] font-extrabold uppercase tracking-wider ${theme.titleColor}`}>
                        <DoorClosed size={13} />
                        <span>CLASSROOMS</span>
                      </div>

                      <div className="grid grid-cols-3 gap-2.5 sm:gap-3">
                        {rooms.map((room) => (
                          <button
                            key={room.id}
                            type="button"
                            onClick={() => setDetailRoom(room)}
                            className={`rounded-2xl border ${theme.tileBorder} ${theme.tileBg} ${theme.tileHoverBg} py-3.5 px-2 flex flex-col items-center justify-center text-center transition hover:scale-[1.02] active:scale-95 shadow-2xs cursor-pointer`}
                          >
                            <span className={`text-sm font-bold tracking-tight ${theme.codeColor}`}>
                              {room.roomCode}
                            </span>
                            <span
                              className={`mt-1.5 flex items-center justify-center gap-1 text-xs font-medium ${theme.capColor}`}
                            >
                              <Users size={12} className="opacity-80" />
                              <span>{room.capacity}</span>
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}

            {activeBlockFloors.length === 0 && (
              <div className="rounded-3xl border border-line bg-panel p-8 text-center space-y-3">
                <p className="text-sm font-bold text-ink">No classrooms matched in {selectedBlock}</p>
                <button
                  type="button"
                  onClick={() => setSearchQuery("")}
                  className="rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition"
                >
                  Clear Filter
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ================= CLASSROOM DETAIL MODAL ================= */}
      {detailRoom && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="hub-room-modal-title"
          className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-overlay/65 backdrop-blur-xs p-0 sm:p-4"
          onClick={() => setDetailRoom(null)}
        >
          <div
            className="w-full max-w-md rounded-t-3xl sm:rounded-3xl border border-line bg-panel p-6 text-ink shadow-2xl space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mx-auto -mt-2 mb-1 h-1.5 w-12 rounded-full bg-subtle sm:hidden" />

            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 id="hub-room-modal-title" className="text-lg font-bold text-ink">
                  {detailRoom.roomCode}
                </h3>
                <p className="text-xs text-muted mt-0.5">{detailRoom.name}</p>
              </div>

              <button
                type="button"
                onClick={() => setDetailRoom(null)}
                aria-label="Close room info"
                className="flex h-8 w-8 items-center justify-center rounded-full bg-subtle text-muted hover:text-ink transition"
              >
                <X size={16} />
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2.5 text-xs">
              <div className="flex items-center gap-2 rounded-2xl bg-surface border border-line p-3">
                <MapPin size={15} className="text-primary-ink shrink-0" />
                <div>
                  <span className="block text-[10px] uppercase font-bold text-muted">Location</span>
                  <span className="font-semibold text-ink">
                    {detailRoom.block} · {detailRoom.floor}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2 rounded-2xl bg-surface border border-line p-3">
                <Users size={15} className="text-primary-ink shrink-0" />
                <div>
                  <span className="block text-[10px] uppercase font-bold text-muted">Seats</span>
                  <span className="font-semibold text-ink">{detailRoom.capacity} Students</span>
                </div>
              </div>
            </div>

            <div>
              <span className="block text-[11px] font-extrabold uppercase tracking-wider text-muted mb-2">
                Room Features
              </span>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="flex items-center gap-1.5 rounded-xl border border-line bg-surface p-2.5 text-ink">
                  <Wifi size={13} className="text-primary-ink shrink-0" />
                  <span>Wi-Fi</span>
                </div>
                <div className="flex items-center gap-1.5 rounded-xl border border-line bg-surface p-2.5 text-ink">
                  <Wind size={13} className="text-secondary-ink shrink-0" />
                  <span>AC</span>
                </div>
                <div className="flex items-center gap-1.5 rounded-xl border border-line bg-surface p-2.5 text-ink">
                  <Tv size={13} className="text-accent-ink shrink-0" />
                  <span>Projector</span>
                </div>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setDetailRoom(null)}
              className="w-full rounded-2xl bg-primary py-3 text-xs font-bold text-on-primary shadow-xs hover:bg-primary-hover transition"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
