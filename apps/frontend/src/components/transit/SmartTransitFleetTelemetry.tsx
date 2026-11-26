import { useState, useMemo } from "react";
import {
  Map,
  Bus,
  ChevronLeft,
  ChevronRight,
  Building2,
  ChevronDown,
  Search,
  MapPin,
  Clock,
  BookOpen,
  Moon,
  Trophy,
  ArrowRight,
  X
} from "lucide-react";

import {
  PLANNED_CITY_BUSES,
  SHUTTLE_SCHEDULE_SETS,
  type PlannedCityBus,
  type ShuttleScheduleKey,
  type ShuttleDirectionKey
} from "../../features/transit/transit-data";

type TransportView = "home" | "planned" | "shuttle";

const SHUTTLE_CARD_ICONS: Record<ShuttleScheduleKey, { icon: typeof Bus; iconStyle: string; linkStyle: string }> = {
  regular: { icon: Bus, iconStyle: "bg-secondary-soft text-secondary-ink", linkStyle: "text-secondary-ink" },
  exams: { icon: BookOpen, iconStyle: "bg-subtle text-ink", linkStyle: "text-ink" },
  ramzan: { icon: Moon, iconStyle: "bg-primary-soft text-primary-ink", linkStyle: "text-primary-ink" },
  sports: { icon: Trophy, iconStyle: "bg-success-soft text-success-ink", linkStyle: "text-success-ink" }
};

interface Props {
  onBack?: () => void;
  initialCategory?: string;
}

/** Renders clean Transport module matching Planned Routes & Shuttle Schedule screenshots. */
export function SmartTransitFleetTelemetry({ onBack }: Props) {
  const [view, setView] = useState<TransportView>("home");
  const [selectedShuttleMode, setSelectedShuttleMode] = useState<ShuttleScheduleKey | null>(null);
  const [selectedDirection, setSelectedDirection] = useState<ShuttleDirectionKey | null>(null);
  const [selectedCity, setSelectedCity] = useState<string>("Sahiwal");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const availableCities = useMemo(() => {
    const cities = Array.from(new Set(PLANNED_CITY_BUSES.map((b) => b.city)));
    return [...cities, "All"];
  }, []);

  const filteredPlannedBuses = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    return PLANNED_CITY_BUSES.filter((bus) => {
      if (selectedCity !== "All" && bus.city !== selectedCity) return false;
      if (!q) return true;
      return (
        bus.busName.toLowerCase().includes(q) ||
        bus.routeTitle.toLowerCase().includes(q) ||
        bus.city.toLowerCase().includes(q) ||
        bus.stops.some((s) => s.name.toLowerCase().includes(q) || s.time.toLowerCase().includes(q))
      );
    });
  }, [selectedCity, searchQuery]);

  const activeShuttleSet = useMemo(
    () => SHUTTLE_SCHEDULE_SETS.find((s) => s.key === selectedShuttleMode) ?? null,
    [selectedShuttleMode]
  );

  const filteredShuttleBuses = useMemo(() => {
    if (!activeShuttleSet || !selectedDirection) return [];
    const list = activeShuttleSet.directions[selectedDirection];
    const q = searchQuery.trim().toLowerCase();
    return list.filter((bus) => {
      if (selectedCity !== "All" && bus.city !== selectedCity) return false;
      if (!q) return true;
      return (
        bus.busName.toLowerCase().includes(q) ||
        bus.routeTitle.toLowerCase().includes(q) ||
        bus.stops.some((s) => s.name.toLowerCase().includes(q) || s.time.toLowerCase().includes(q))
      );
    });
  }, [activeShuttleSet, selectedDirection, selectedCity, searchQuery]);

  const renderBusScheduleBlock = (buses: PlannedCityBus[]) => (
    <div className="space-y-4">
      {/* City Dropdown */}
      <div className="relative flex items-center rounded-2xl border border-line bg-panel px-4 py-2.5 shadow-2xs">
        <Building2 size={16} className="shrink-0 text-primary-ink mr-2.5" />
        <select
          value={selectedCity}
          onChange={(e) => setSelectedCity(e.target.value)}
          aria-label="Select city"
          className="flex-1 appearance-none bg-transparent pr-6 text-sm font-semibold text-ink focus:outline-hidden cursor-pointer"
        >
          {availableCities.map((city) => (
            <option key={city} value={city}>
              {city === "All" ? "All Cities" : city}
            </option>
          ))}
        </select>
        <ChevronDown size={16} className="pointer-events-none text-muted shrink-0" />
      </div>

      {/* Search Bar */}
      <div className="flex items-center gap-2.5 rounded-2xl border border-line bg-panel px-4 py-2.5 shadow-2xs">
        <Search size={16} className="shrink-0 text-primary-ink" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          aria-label="Search by route or bus number"
          placeholder="Search by route or bus number"
          className="flex-1 min-w-0 bg-transparent py-0.5 text-sm text-ink placeholder:text-muted focus:outline-hidden"
        />
        {searchQuery && (
          <button
            type="button"
            onClick={() => setSearchQuery("")}
            aria-label="Clear bus search"
            className="rounded-full p-1 text-muted hover:text-ink cursor-pointer"
          >
            <X size={14} />
          </button>
        )}
      </div>

      {/* Count Line */}
      <div className="flex items-center justify-between px-1">
        <span className="text-xs font-medium text-muted">
          {buses.length} {buses.length === 1 ? "bus found" : "buses found"}
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

      {/* Bus Cards */}
      {buses.length === 0 ? (
        <div className="rounded-3xl border border-line bg-panel p-8 text-center space-y-3">
          <p className="text-sm font-bold text-ink">No matching buses found</p>
          <p className="text-xs text-muted">Try another stop name, bus number, or switch city.</p>
          <button
            type="button"
            onClick={() => {
              setSearchQuery("");
              setSelectedCity("Sahiwal");
            }}
            className="rounded-xl bg-primary px-4 py-2 text-xs font-bold text-on-primary hover:bg-primary-hover transition cursor-pointer"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {buses.map((bus) => (
            <div
              key={bus.id}
              className="overflow-hidden rounded-3xl border border-line bg-panel shadow-xs"
            >
              {/* Blue Header Bar matching screenshot */}
              <div className="bg-hero-bg px-4 py-3 text-hero-fg flex items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-hero-fg/15 text-hero-fg">
                    <Bus size={18} />
                  </span>
                  <h4 className="font-bold text-base text-hero-fg">{bus.busName}</h4>
                </div>
                <span className="text-[11px] font-medium text-hero-muted truncate">
                  {bus.routeTitle}
                </span>
              </div>

              {/* Stop Tiles Grid: Location Pin + Name, Clock Icon + Time directly below */}
              <div className="p-4 grid grid-cols-2 sm:grid-cols-3 gap-2.5 sm:gap-3">
                {bus.stops.map((stop) => (
                  <div
                    key={stop.id}
                    className="rounded-2xl border border-line/70 bg-surface/65 p-3 space-y-1.5"
                  >
                    <div className="flex items-start gap-1.5">
                      <MapPin size={13} className="shrink-0 text-primary-ink mt-0.5" />
                      <span className="text-xs font-semibold text-ink leading-snug">
                        {stop.name}
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5 text-muted">
                      <Clock size={12} className="shrink-0 text-secondary-ink" />
                      <span className="text-[11px] font-medium font-mono">{stop.time}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  // ================= VIEW 1: TRANSPORT LANDING (PLANNED ROUTES & SHUTTLE SCHEDULE ONLY) =================
  if (view === "home") {
    return (
      <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
        <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-9 text-hero-fg rounded-b-[2rem] shadow-md">
          <div className="pointer-events-none absolute -top-10 -right-10 h-44 w-44 rounded-full bg-hero-fg/10 blur-xl" />
          <div className="pointer-events-none absolute top-4 right-12 h-24 w-24 rounded-full bg-hero-accent/20 blur-md" />

          <div className="relative z-10 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 min-w-0">
              {onBack && (
                <button
                  type="button"
                  onClick={onBack}
                  aria-label="Back to Main Dashboard"
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-hero-fg/15 backdrop-blur-md text-hero-fg hover:bg-hero-fg/25 transition cursor-pointer"
                >
                  <ChevronLeft size={20} strokeWidth={2.5} />
                </button>
              )}

              <div className="min-w-0">
                <h2 className="text-xl sm:text-2xl font-bold tracking-tight text-hero-fg leading-tight">
                  Transport
                </h2>
                <p className="text-xs text-hero-muted mt-0.5">
                  Campus transport services
                </p>
              </div>
            </div>

            <span className="shrink-0 rounded-full border border-hero-fg/25 bg-hero-fg/15 px-3.5 py-1.5 text-xs font-semibold text-hero-fg whitespace-nowrap">
              2 Options
            </span>
          </div>
        </div>

        <div className="p-4 sm:p-5 space-y-4">
          <div className="flex items-center gap-2 px-1">
            <span className="h-4 w-1 rounded-full bg-primary" />
            <span className="text-xs font-extrabold uppercase tracking-wider text-muted">
              QUICK ACCESS
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3.5 sm:gap-4">
            {/* Planned Routes */}
            <button
              type="button"
              onClick={() => {
                setView("planned");
                setSearchQuery("");
                setSelectedCity("Sahiwal");
              }}
              aria-label="Planned Routes"
              className="rounded-3xl border border-line bg-panel p-4 sm:p-5 text-left shadow-sm hover:shadow-md hover:border-primary/40 transition flex flex-col justify-between min-h-[144px] cursor-pointer group"
            >
              <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-secondary-soft text-secondary-ink group-hover:scale-105 transition">
                <Map size={21} />
              </span>

              <div className="mt-4 space-y-1">
                <span className="block font-bold text-sm sm:text-base text-ink leading-snug">
                  Planned Routes
                </span>
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs text-muted leading-snug">View all bus routes</span>
                  <ChevronRight
                    size={15}
                    className="shrink-0 text-muted group-hover:text-ink group-hover:translate-x-0.5 transition"
                    aria-hidden="true"
                  />
                </div>
              </div>
            </button>

            {/* Shuttle Schedule */}
            <button
              type="button"
              onClick={() => {
                setView("shuttle");
                setSelectedShuttleMode(null);
                setSelectedDirection(null);
                setSearchQuery("");
              }}
              aria-label="Shuttle Schedule"
              className="rounded-3xl border border-line bg-panel p-4 sm:p-5 text-left shadow-sm hover:shadow-md hover:border-primary/40 transition flex flex-col justify-between min-h-[144px] cursor-pointer group"
            >
              <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary-soft text-primary-ink group-hover:scale-105 transition">
                <Bus size={21} />
              </span>

              <div className="mt-4 space-y-1">
                <span className="block font-bold text-sm sm:text-base text-ink leading-snug">
                  Shuttle Schedule
                </span>
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs text-muted leading-snug">Check timings &amp; stops</span>
                  <ChevronRight
                    size={15}
                    className="shrink-0 text-muted group-hover:text-ink group-hover:translate-x-0.5 transition"
                    aria-hidden="true"
                  />
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ================= VIEW 2A: PLANNED ROUTES -> TRANSPORT SCHEDULE =================
  if (view === "planned") {
    const cityBusCount = PLANNED_CITY_BUSES.filter(
      (b) => selectedCity === "All" || b.city === selectedCity
    ).length;

    return (
      <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
        <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-8 text-hero-fg rounded-b-[2rem] shadow-md space-y-4">
          <div className="pointer-events-none absolute -top-10 -right-10 h-44 w-44 rounded-full bg-hero-fg/10 blur-xl" />
          <div className="pointer-events-none absolute top-4 right-12 h-24 w-24 rounded-full bg-hero-accent/20 blur-md" />

          <div className="relative z-10 flex items-center justify-between gap-3">
            <button
              type="button"
              onClick={() => setView("home")}
              aria-label="Back to Transport"
              className="flex h-10 w-10 items-center justify-center rounded-2xl bg-hero-fg/15 backdrop-blur-md text-hero-fg hover:bg-hero-fg/25 transition cursor-pointer"
            >
              <ChevronLeft size={20} strokeWidth={2.5} />
            </button>

            <span className="shrink-0 rounded-full border border-hero-fg/25 bg-hero-fg/15 px-3.5 py-1.5 text-xs font-semibold text-hero-fg whitespace-nowrap">
              {cityBusCount} {cityBusCount === 1 ? "Bus" : "Buses"}
            </span>
          </div>

          <div className="relative z-10 flex items-center gap-3.5">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-hero-fg/15 backdrop-blur-md text-hero-fg shadow-xs">
              <Bus size={21} />
            </span>
            <div>
              <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-hero-fg leading-tight">
                Transport Schedule
              </h3>
              <p className="text-xs text-hero-muted mt-0.5">
                City bus routes &amp; timings
              </p>
            </div>
          </div>
        </div>

        <div className="p-4 sm:p-5">{renderBusScheduleBlock(filteredPlannedBuses)}</div>
      </div>
    );
  }

  // ================= VIEW 2B: SHUTTLE SCHEDULE OVERVIEW (4 MODES) =================
  if (!activeShuttleSet) {
    return (
      <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
        <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-9 text-hero-fg rounded-b-[2rem] shadow-md">
          <div className="pointer-events-none absolute -top-10 -right-10 h-44 w-44 rounded-full bg-hero-fg/10 blur-xl" />
          <div className="pointer-events-none absolute top-4 right-12 h-24 w-24 rounded-full bg-hero-accent/20 blur-md" />

          <div className="relative z-10 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 min-w-0">
              <button
                type="button"
                onClick={() => setView("home")}
                aria-label="Back to Transport"
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-hero-fg/15 backdrop-blur-md text-hero-fg hover:bg-hero-fg/25 transition cursor-pointer"
              >
                <ChevronLeft size={20} strokeWidth={2.5} />
              </button>

              <div className="min-w-0">
                <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-hero-fg leading-tight">
                  Shuttle Schedule
                </h3>
                <p className="text-xs text-hero-muted mt-0.5">
                  Campus transport timings
                </p>
              </div>
            </div>

            <span className="shrink-0 rounded-full border border-hero-fg/25 bg-hero-fg/15 px-3.5 py-1.5 text-xs font-semibold text-hero-fg whitespace-nowrap">
              {SHUTTLE_SCHEDULE_SETS.length} Routes
            </span>
          </div>
        </div>

        <div className="p-4 sm:p-5 space-y-4">
          <div className="flex items-center gap-2 px-1">
            <span className="h-4 w-1 rounded-full bg-primary" />
            <span className="text-xs font-extrabold uppercase tracking-wider text-muted">
              QUICK ACCESS
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3.5 sm:gap-4">
            {SHUTTLE_SCHEDULE_SETS.map((item) => {
              const meta = SHUTTLE_CARD_ICONS[item.key];
              const Icon = meta.icon;
              return (
                <button
                  key={item.key}
                  type="button"
                  onClick={() => {
                    setSelectedShuttleMode(item.key);
                    setSelectedDirection(null);
                    setSearchQuery("");
                  }}
                  aria-label={item.label}
                  className="rounded-3xl border border-line bg-panel p-4 sm:p-5 text-left shadow-sm hover:shadow-md hover:border-primary/40 transition flex flex-col justify-between min-h-[144px] cursor-pointer group"
                >
                  <span
                    className={`flex h-11 w-11 items-center justify-center rounded-2xl ${meta.iconStyle} group-hover:scale-105 transition`}
                  >
                    <Icon size={21} />
                  </span>

                  <div className="mt-4 space-y-1">
                    <span className="block font-bold text-sm sm:text-base text-ink leading-snug">
                      {item.label}
                    </span>
                    <div className="flex items-center justify-between gap-2">
                      <span className={`text-xs font-semibold ${meta.linkStyle}`}>
                        View schedule
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
      </div>
    );
  }

  // ================= VIEW 3: SHUTTLE DIRECTION + INLINE BUS SCHEDULE BELOW =================
  return (
    <div className="mx-auto max-w-2xl rounded-3xl border border-line bg-background overflow-hidden shadow-sm">
      <div className="relative overflow-hidden bg-hero-bg px-5 pt-6 pb-9 text-hero-fg rounded-b-[2rem] shadow-md">
        <div className="pointer-events-none absolute -top-10 -right-10 h-44 w-44 rounded-full bg-hero-fg/10 blur-xl" />
        <div className="pointer-events-none absolute top-4 right-12 h-24 w-24 rounded-full bg-hero-accent/20 blur-md" />

        <div className="relative z-10 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3 min-w-0">
            <button
              type="button"
              onClick={() => {
                setSelectedShuttleMode(null);
                setSelectedDirection(null);
                setSearchQuery("");
              }}
              aria-label="Back to Shuttle Schedule"
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-hero-fg/15 backdrop-blur-md text-hero-fg hover:bg-hero-fg/25 transition cursor-pointer"
            >
              <ChevronLeft size={20} strokeWidth={2.5} />
            </button>

            <div className="min-w-0">
              <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-hero-fg leading-tight">
                Shuttle
              </h3>
              <p className="text-xs text-hero-muted mt-0.5">
                {activeShuttleSet.subtitle}
              </p>
            </div>
          </div>

          <span className="inline-flex items-center gap-1.5 shrink-0 rounded-full border border-hero-fg/25 bg-hero-fg/15 px-3.5 py-1.5 text-xs font-semibold text-hero-fg whitespace-nowrap">
            <Bus size={13} />
            <span>2 Routes</span>
          </span>
        </div>
      </div>

      <div className="p-4 sm:p-5 space-y-5">
        <div className="space-y-3.5">
          <div className="flex items-center gap-2 px-1">
            <span className="h-4 w-1 rounded-full bg-primary" />
            <span className="text-xs font-extrabold uppercase tracking-wider text-muted">
              SELECT DIRECTION
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3.5 sm:gap-4">
            {/* From University */}
            <button
              type="button"
              aria-pressed={selectedDirection === "from_university"}
              onClick={() => {
                setSelectedDirection("from_university");
                setSearchQuery("");
              }}
              className={`rounded-3xl border bg-panel p-4 sm:p-5 text-left transition flex flex-col justify-between min-h-[144px] cursor-pointer group ${
                selectedDirection === "from_university"
                  ? "border-secondary ring-2 ring-secondary/25 shadow-md"
                  : "border-line shadow-sm hover:shadow-md hover:border-secondary/45"
              }`}
            >
              <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-secondary-soft text-secondary-ink group-hover:scale-105 transition">
                <Bus size={21} />
              </span>

              <div className="mt-4 space-y-2">
                <span className="inline-flex items-center gap-1 rounded-full bg-secondary px-2.5 py-0.5 text-[10px] font-bold text-secondary-fg">
                  <ArrowRight size={10} />
                  <span>University → Stop</span>
                </span>
                <div className="flex items-center justify-between gap-2">
                  <span className="font-bold text-sm text-ink">From University</span>
                  <ChevronRight size={15} className="shrink-0 text-muted" aria-hidden="true" />
                </div>
              </div>
            </button>

            {/* To University */}
            <button
              type="button"
              aria-pressed={selectedDirection === "to_university"}
              onClick={() => {
                setSelectedDirection("to_university");
                setSearchQuery("");
              }}
              className={`rounded-3xl border bg-panel p-4 sm:p-5 text-left transition flex flex-col justify-between min-h-[144px] cursor-pointer group ${
                selectedDirection === "to_university"
                  ? "border-primary ring-2 ring-primary/25 shadow-md"
                  : "border-line shadow-sm hover:shadow-md hover:border-primary/45"
              }`}
            >
              <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-primary-soft text-primary-ink group-hover:scale-105 transition">
                <Bus size={21} />
              </span>

              <div className="mt-4 space-y-2">
                <span className="inline-flex items-center gap-1 rounded-full bg-primary px-2.5 py-0.5 text-[10px] font-bold text-on-primary">
                  <ArrowRight size={10} />
                  <span>Stop → University</span>
                </span>
                <div className="flex items-center justify-between gap-2">
                  <span className="font-bold text-sm text-ink">To University</span>
                  <ChevronRight size={15} className="shrink-0 text-muted" aria-hidden="true" />
                </div>
              </div>
            </button>
          </div>
        </div>

        {/* Route Details Rendered Inline Below when a direction is clicked (Planned Route UI) */}
        {selectedDirection && (
          <div className="pt-4 border-t border-line/60 animate-in fade-in duration-200">
            {renderBusScheduleBlock(filteredShuttleBuses)}
          </div>
        )}
      </div>
    </div>
  );
}
