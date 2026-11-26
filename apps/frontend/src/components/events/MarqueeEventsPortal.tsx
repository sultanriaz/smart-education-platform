import { useState, useMemo } from "react";
import {
  Trophy,
  Clock,
  MapPin,
  Search,
  ChevronLeft,
  X
} from "lucide-react";

import {
  SPORTS_WEEK_EVENTS,
  type SportsDayKey,
  type SimpleSportsEvent
} from "../../features/events/marquee-events-data";

const DAY_OPTIONS: Array<{ key: SportsDayKey; label: string }> = [
  { key: "mon", label: "mon" },
  { key: "tue", label: "tue" },
  { key: "wed", label: "wed" },
  { key: "thu", label: "thu" },
  { key: "fri", label: "fri" }
];

const EVENT_CARD_ACCENTS: Record<
  SimpleSportsEvent["accent"],
  { banner: string; clockBadge: string; timeText: string }
> = {
  primary: {
    banner: "bg-primary text-on-primary",
    clockBadge: "bg-primary-soft text-primary-ink",
    timeText: "text-primary-ink"
  },
  success: {
    banner: "bg-success text-success-fg",
    clockBadge: "bg-success-soft text-success-ink",
    timeText: "text-success-ink"
  },
  danger: {
    banner: "bg-danger text-danger-fg",
    clockBadge: "bg-danger-soft text-danger-ink",
    timeText: "text-danger-ink"
  },
  secondary: {
    banner: "bg-secondary text-secondary-fg",
    clockBadge: "bg-secondary-soft text-secondary-ink",
    timeText: "text-secondary-ink"
  }
};

interface Props {
  onBack?: () => void;
  initialMode?: string;
}

/** Displays Sports Week day-by-day events, timings, and venues matching the mobile screenshot. */
export function MarqueeEventsPortal({ onBack }: Props) {
  const [selectedDay, setSelectedDay] = useState<SportsDayKey>("mon");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const filteredEvents = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    return SPORTS_WEEK_EVENTS.filter((ev) => {
      if (ev.day !== selectedDay) return false;
      if (!q) return true;
      return (
        ev.title.toLowerCase().includes(q) ||
        ev.time.toLowerCase().includes(q) ||
        ev.location.toLowerCase().includes(q)
      );
    });
  }, [selectedDay, searchQuery]);

  return (
    <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
      {/* Top Curved Hero Banner */}
      <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-7 text-hero-fg rounded-b-[2rem] shadow-md space-y-4">
        <div className="pointer-events-none absolute -top-10 -right-10 h-44 w-44 rounded-full bg-hero-fg/10 blur-xl" />
        <div className="pointer-events-none absolute top-4 right-12 h-24 w-24 rounded-full bg-hero-accent/20 blur-md" />

        <div className="relative z-10 flex items-center justify-between gap-3">
          {onBack ? (
            <button
              type="button"
              onClick={onBack}
              aria-label="Back to Main Dashboard"
              className="flex h-10 w-10 items-center justify-center rounded-2xl bg-hero-fg/15 backdrop-blur-md text-hero-fg hover:bg-hero-fg/25 transition cursor-pointer"
            >
              <ChevronLeft size={20} strokeWidth={2.5} />
            </button>
          ) : (
            <span />
          )}

          <span className="shrink-0 rounded-full border border-hero-fg/25 bg-hero-fg/15 px-3.5 py-1.5 text-xs font-semibold text-hero-fg whitespace-nowrap">
            Fall 2026
          </span>
        </div>

        <div className="relative z-10 flex items-center gap-3.5">
          <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-hero-fg/15 backdrop-blur-md text-hero-fg shadow-xs">
            <Trophy size={21} />
          </span>
          <div>
            <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-hero-fg leading-tight">
              Sports Week
            </h2>
            <p className="text-xs text-hero-muted mt-0.5">
              Events, timings &amp; venues
            </p>
          </div>
        </div>
      </div>

      {/* Day Tabs + Search + Events Stack */}
      <div className="p-4 sm:p-5 space-y-4">
        {/* Mon - Fri Segmented Day Selector */}
        <div
          className="grid grid-cols-5 gap-1.5 rounded-2xl border border-line bg-panel p-1.5 shadow-2xs"
          role="tablist"
          aria-label="Select Sports Week day"
        >
          {DAY_OPTIONS.map((day) => {
            const active = selectedDay === day.key;
            return (
              <button
                key={day.key}
                type="button"
                role="tab"
                aria-selected={active}
                onClick={() => setSelectedDay(day.key)}
                className={`rounded-xl py-2 text-xs font-bold lowercase transition cursor-pointer ${
                  active
                    ? "bg-primary text-on-primary shadow-2xs"
                    : "text-muted hover:text-ink border border-transparent hover:border-line"
                }`}
              >
                {day.label}
              </button>
            );
          })}
        </div>

        {/* Search Input */}
        <div className="flex items-center gap-2.5 rounded-2xl border border-line bg-panel px-4 py-2.5 shadow-2xs">
          <Search size={16} className="shrink-0 text-primary-ink" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search by location, game, or time"
            placeholder="Search by location, game, or time"
            className="flex-1 min-w-0 bg-transparent py-0.5 text-sm text-ink placeholder:text-muted focus:outline-hidden"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              aria-label="Clear sports search"
              className="rounded-full p-1 text-muted hover:text-ink cursor-pointer"
            >
              <X size={14} />
            </button>
          )}
        </div>

        {/* Event Count */}
        <div className="flex items-center justify-between px-1">
          <span className="text-xs font-medium text-muted">
            {filteredEvents.length} {filteredEvents.length === 1 ? "event found" : "events found"}
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

        {/* Event Cards */}
        {filteredEvents.length === 0 ? (
          <div className="rounded-3xl border border-line bg-panel p-8 text-center space-y-3">
            <p className="text-sm font-bold text-ink">No matching events found</p>
            <p className="text-xs text-muted">
              Try another game name, venue, time, or select a different day above.
            </p>
            <button
              type="button"
              onClick={() => setSearchQuery("")}
              className="rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition cursor-pointer"
            >
              Show All Events
            </button>
          </div>
        ) : (
          <div className="space-y-3.5">
            {filteredEvents.map((ev) => {
              const theme = EVENT_CARD_ACCENTS[ev.accent];
              return (
                <div
                  key={ev.id}
                  className="overflow-hidden rounded-3xl border border-line bg-panel shadow-2xs"
                >
                  {/* Colored Top Header */}
                  <div className={`${theme.banner} px-4 py-3 flex items-center gap-3`}>
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-hero-fg/15">
                      <Trophy size={16} />
                    </span>
                    <h3 className="font-bold text-base leading-snug">{ev.title}</h3>
                  </div>

                  {/* Minimal Body: Time & Venue */}
                  <div className="p-3.5">
                    <div className="rounded-2xl border border-line/60 bg-surface/65 p-3 space-y-2.5">
                      <div className="flex items-center gap-2.5">
                        <span
                          className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg ${theme.clockBadge}`}
                        >
                          <Clock size={14} />
                        </span>
                        <span className={`text-xs sm:text-sm font-bold ${theme.timeText}`}>
                          {ev.time}
                        </span>
                      </div>

                      <div className="flex items-center gap-2.5">
                        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-warning-soft text-warning-ink">
                          <MapPin size={14} />
                        </span>
                        <span className="text-xs sm:text-sm font-medium text-ink">
                          {ev.location}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
