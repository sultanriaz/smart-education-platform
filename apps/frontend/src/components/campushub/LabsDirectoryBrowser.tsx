import { useState, useMemo, useEffect } from "react";
import {
  FlaskConical,
  Search,
  MapPin,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
  Users,
  Monitor,
  UserCheck,
  Wifi,
  Wind,
  Tv
} from "lucide-react";

import {
  CAMPUS_LABS_DIRECTORY,
  type CampusLabItem,
  type LabBlockLabel
} from "../../features/campushub/campus-hub-data";

const BLOCK_OPTIONS: Array<"All" | LabBlockLabel> = ["All", "A Block", "B Block", "C Block"];

/** Displays the campus Labs Directory matching the clean card-list reference UI. */
export function LabsDirectoryBrowser({ onBack }: { onBack?: () => void } = {}) {
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedBlock, setSelectedBlock] = useState<"All" | LabBlockLabel>("All");
  const [showFilters, setShowFilters] = useState<boolean>(false);
  const [detailLab, setDetailLab] = useState<CampusLabItem | null>(null);

  useEffect(() => {
    if (!detailLab) return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setDetailLab(null);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [detailLab]);

  const filteredLabs = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    return CAMPUS_LABS_DIRECTORY.filter((lab) => {
      if (selectedBlock !== "All" && lab.block !== selectedBlock) return false;
      if (!q) return true;
      const blockAlias = lab.block.toLowerCase();
      const reverseBlock = `block ${blockAlias.replace(" block", "")}`;
      return (
        lab.name.toLowerCase().includes(q) ||
        blockAlias.includes(q) ||
        reverseBlock.includes(q) ||
        lab.floor.toLowerCase().includes(q) ||
        lab.description.toLowerCase().includes(q)
      );
    });
  }, [searchQuery, selectedBlock]);

  const hasFilters = searchQuery.trim().length > 0 || selectedBlock !== "All";

  const clearAll = () => {
    setSearchQuery("");
    setSelectedBlock("All");
  };

  return (
    <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
      {/* ================= TOP ROUNDED HERO HEADER & SEARCH ================= */}
      <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-6 text-hero-fg rounded-b-[2rem] shadow-md space-y-4">
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

            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-hero-fg/15 backdrop-blur-md text-hero-fg shadow-xs">
              <FlaskConical size={22} />
            </span>

            <div className="min-w-0">
              <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-hero-fg leading-tight">
                Labs Directory
              </h3>
              <p className="text-xs text-hero-muted mt-0.5">
                All campus laboratories
              </p>
            </div>
          </div>

          <button
            type="button"
            aria-expanded={showFilters}
            aria-label="Filter labs by block"
            onClick={() => setShowFilters((v) => !v)}
            className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-full backdrop-blur-md transition cursor-pointer ${
              showFilters || selectedBlock !== "All"
                ? "bg-hero-fg text-hero-bg shadow-xs"
                : "bg-hero-fg/15 text-hero-fg hover:bg-hero-fg/25"
            }`}
          >
            <Menu size={20} />
          </button>
        </div>

        {/* Embedded Pill Search Bar */}
        <div className="relative z-10 flex items-center gap-2 rounded-2xl bg-panel border border-line p-1.5 shadow-sm">
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-subtle text-muted">
            <Search size={16} />
          </span>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search labs or location"
            placeholder="Search labs or location..."
            className="flex-1 min-w-0 bg-transparent px-1 py-1.5 text-sm text-ink placeholder:text-muted focus:outline-hidden"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              aria-label="Clear lab search"
              className="mr-1 rounded-full p-1 text-muted hover:text-ink"
            >
              <X size={14} />
            </button>
          )}
        </div>

        {/* Expandable Block Filter Pills */}
        {showFilters && (
          <div className="relative z-10 flex flex-wrap items-center gap-1.5 pt-1" role="group" aria-label="Filter by block">
            {BLOCK_OPTIONS.map((blk) => {
              const active = selectedBlock === blk;
              return (
                <button
                  key={blk}
                  type="button"
                  aria-pressed={active}
                  onClick={() => setSelectedBlock(blk)}
                  className={`rounded-xl px-3 py-1.5 text-xs font-bold transition cursor-pointer ${
                    active
                      ? "bg-hero-fg text-hero-bg shadow-xs"
                      : "bg-hero-fg/15 text-hero-fg hover:bg-hero-fg/25"
                  }`}
                >
                  {blk === "All" ? "All Blocks" : blk}
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* ================= STATUS BAR ================= */}
      <div className="px-5 pt-4 pb-2 flex items-center justify-between gap-2">
        <span className="text-xs font-extrabold uppercase tracking-wider text-muted">
          {filteredLabs.length} {filteredLabs.length === 1 ? "LAB" : "LABS"} FOUND
        </span>

        {hasFilters && (
          <button
            type="button"
            onClick={clearAll}
            className="text-xs font-bold text-primary-ink hover:underline"
          >
            Show all
          </button>
        )}
      </div>

      {/* ================= STACKED LAB CARDS ================= */}
      <div className="px-4 pb-5 space-y-3.5">
        {filteredLabs.map((lab) => (
          <button
            key={lab.id}
            type="button"
            onClick={() => setDetailLab(lab)}
            className="w-full text-left rounded-3xl border border-line bg-panel overflow-hidden shadow-xs hover:shadow-md hover:border-primary/40 transition cursor-pointer group"
          >
            {/* Card Top Banner */}
            <div className="bg-primary px-4 py-3.5 text-on-primary flex items-center gap-3">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-on-primary/15">
                <FlaskConical size={18} />
              </span>
              <span className="font-bold text-base tracking-tight">{lab.name}</span>
            </div>

            {/* Card Bottom Location Row */}
            <div className="px-4 py-3.5 bg-panel flex items-center justify-between gap-3">
              <div className="flex items-center gap-3 min-w-0">
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-warning-soft text-warning-ink">
                  <MapPin size={18} />
                </span>
                <div className="min-w-0">
                  <span className="block text-[10px] font-bold uppercase tracking-wider text-muted">
                    LOCATION
                  </span>
                  <span className="block text-sm font-bold text-ink mt-0.5">
                    {lab.block} &nbsp;({lab.floor})
                  </span>
                </div>
              </div>

              <span
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-subtle text-muted group-hover:text-ink transition"
                aria-hidden="true"
              >
                <ChevronRight size={17} />
              </span>
            </div>
          </button>
        ))}

        {filteredLabs.length === 0 && (
          <div className="rounded-3xl border border-line bg-panel p-8 text-center space-y-3">
            <p className="text-sm font-bold text-ink">No matching labs found</p>
            <p className="text-xs text-muted">
              Try searching by lab name, block, or floor.
            </p>
            <button
              type="button"
              onClick={clearAll}
              className="rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition"
            >
              Show All Labs
            </button>
          </div>
        )}
      </div>

      {/* ================= LAB DETAILS POPUP ================= */}
      {detailLab && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="hub-lab-modal-title"
          className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-overlay/65 backdrop-blur-xs p-0 sm:p-4"
          onClick={() => setDetailLab(null)}
        >
          <div
            className="w-full max-w-md rounded-t-3xl sm:rounded-3xl border border-line bg-panel p-6 text-ink shadow-2xl space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="mx-auto -mt-2 mb-1 h-1.5 w-12 rounded-full bg-subtle sm:hidden" />

            <div className="flex items-start justify-between gap-3">
              <div>
                <h3 id="hub-lab-modal-title" className="text-lg font-bold text-ink">
                  {detailLab.name}
                </h3>
                <p className="text-xs text-muted mt-0.5">{detailLab.description}</p>
              </div>

              <button
                type="button"
                onClick={() => setDetailLab(null)}
                aria-label="Close lab details"
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-subtle text-muted hover:text-ink transition"
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
                    {detailLab.block} ({detailLab.floor})
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2 rounded-2xl bg-surface border border-line p-3">
                {detailLab.computersCount > 0 ? (
                  <Monitor size={15} className="text-primary-ink shrink-0" />
                ) : (
                  <Users size={15} className="text-primary-ink shrink-0" />
                )}
                <div>
                  <span className="block text-[10px] uppercase font-bold text-muted">Capacity</span>
                  <span className="font-semibold text-ink">
                    {detailLab.computersCount > 0
                      ? `${detailLab.computersCount} Computers`
                      : `${detailLab.seats} Seats`}
                  </span>
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-line bg-surface p-3 text-xs flex items-center gap-2 text-ink">
              <UserCheck size={14} className="text-secondary-ink shrink-0" />
              <span>
                <strong>In-Charge:</strong> {detailLab.inCharge}
              </span>
            </div>

            <div>
              <span className="block text-[11px] font-extrabold uppercase tracking-wider text-muted mb-2">
                Room Features
              </span>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className={`flex items-center gap-1.5 rounded-xl border border-line bg-surface p-2.5 ${detailLab.hasWifi ? "text-ink" : "text-muted/55"}`}>
                  <Wifi size={13} className="shrink-0" />
                  <span>Wi-Fi</span>
                </div>
                <div className={`flex items-center gap-1.5 rounded-xl border border-line bg-surface p-2.5 ${detailLab.hasAC ? "text-ink" : "text-muted/55"}`}>
                  <Wind size={13} className="shrink-0" />
                  <span>AC</span>
                </div>
                <div className={`flex items-center gap-1.5 rounded-xl border border-line bg-surface p-2.5 ${detailLab.hasProjector ? "text-ink" : "text-muted/55"}`}>
                  <Tv size={13} className="shrink-0" />
                  <span>Projector</span>
                </div>
              </div>
            </div>

            <button
              type="button"
              onClick={() => setDetailLab(null)}
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
