import { useState, useMemo } from "react";
import {
  Bus,
  Clock,
  MapPin,
  Users,
  Phone,
  AlertTriangle,
  CheckCircle2,
  Navigation,
  RefreshCw,
  Search,
  Wifi,
  Wind,
  Sparkles,
  ShieldAlert,
  Info,
  ChevronDown,
  ChevronUp,
  Bell,
  ArrowRight,
  ArrowUpDown,
  Activity,
  Layers,
  X
} from "lucide-react";

import {
  TRANSIT_ROUTES,
  TRANSIT_ALERTS,
  type TransitRoute,
  type RouteCategory,
  type TransitStop
} from "../../features/transit/transit-data";

interface Props {
  initialCategory?: RouteCategory;
  showExplorerLink?: boolean;
}

export function SmartTransitFleetTelemetry({
  initialCategory = "CITY_ROUTE",
  showExplorerLink = false
}: Props) {
  const [selectedCategory, setSelectedCategory] = useState<RouteCategory>(initialCategory);
  const [stopSearchQuery, setStopSearchQuery] = useState<string>("");
  const [expandedRouteId, setExpandedRouteId] = useState<string | null>(null);
  const [isAlertsDismissed, setIsAlertsDismissed] = useState<boolean>(false);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [lastRefreshedAt, setLastRefreshedAt] = useState<string>("Just now");
  const [subscribedStops, setSubscribedStops] = useState<Record<string, boolean>>({});

  // Trigger manual GPS telemetry refresh
  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
      setLastRefreshedAt(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }));
    }, 600);
  };

  // Toggle stop arrival notification simulation
  const toggleStopAlert = (stopId: string, stopName: string) => {
    setSubscribedStops((prev) => {
      const next = !prev[stopId];
      return { ...prev, [stopId]: next };
    });
  };

  // Filter routes by category and optional stop query
  const filteredRoutes = useMemo(() => {
    return TRANSIT_ROUTES.filter((route) => {
      // Category filter
      if (route.category !== selectedCategory) return false;

      // Stop search query
      if (stopSearchQuery.trim()) {
        const query = stopSearchQuery.toLowerCase();
        const matchesRouteName = route.name.toLowerCase().includes(query);
        const matchesBusNumber = route.bus.busNumber.toLowerCase().includes(query);
        const matchesStop = route.stops.some(
          (s) => s.name.toLowerCase().includes(query) || s.landmark.toLowerCase().includes(query)
        );
        return matchesRouteName || matchesBusNumber || matchesStop;
      }

      return true;
    });
  }, [selectedCategory, stopSearchQuery]);

  // Count active routes per category
  const cityCount = TRANSIT_ROUTES.filter((r) => r.category === "CITY_ROUTE").length;
  const shuttleCount = TRANSIT_ROUTES.filter((r) => r.category === "CAMPUS_SHUTTLE").length;

  // Find stop matches when searching
  const searchedStopMatches = useMemo(() => {
    if (!stopSearchQuery.trim()) return [];
    const query = stopSearchQuery.toLowerCase();
    const results: { route: TransitRoute; stop: TransitStop }[] = [];

    TRANSIT_ROUTES.forEach((route) => {
      route.stops.forEach((stop) => {
        if (stop.name.toLowerCase().includes(query) || stop.landmark.toLowerCase().includes(query)) {
          results.push({ route, stop });
        }
      });
    });

    return results;
  }, [stopSearchQuery]);

  return (
    <div className="space-y-6">
      {/* ================= SERVICE DISRUPTION NOTICES FEED ================= */}
      {!isAlertsDismissed && TRANSIT_ALERTS.length > 0 && (
        <div className="rounded-2xl border border-amber-500/40 bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent p-4 sm:p-5 shadow-xs space-y-3">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-2.5">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-500 text-white shadow-xs shrink-0">
                <AlertTriangle size={18} />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-extrabold text-sm text-ink">Active Fleet & Route Disruption Notices</h4>
                  <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-2xs font-extrabold text-amber-800 dark:text-amber-300">
                    {TRANSIT_ALERTS.length} Active Bulletins
                  </span>
                </div>
                <p className="text-xs text-muted">
                  Municipal road repairs, weather advisories, and maintenance swaps impacting scheduled ETAs.
                </p>
              </div>
            </div>

            <button
              onClick={() => setIsAlertsDismissed(true)}
              className="text-xs text-muted hover:text-ink transition p-1"
              title="Dismiss notices for this session"
            >
              <X size={16} />
            </button>
          </div>

          <div className="grid gap-3 pt-1 sm:grid-cols-2 lg:grid-cols-3">
            {TRANSIT_ALERTS.map((alert) => (
              <div
                key={alert.id}
                className="rounded-xl border border-amber-500/30 bg-panel/80 p-3.5 space-y-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-amber-700 dark:text-amber-300 flex items-center gap-1.5">
                    <ShieldAlert size={13} />
                    <span>{alert.affectedRoutes.join(", ")}</span>
                  </span>
                  <span className="text-2xs text-muted">{alert.timestamp}</span>
                </div>
                <p className="font-bold text-ink leading-snug">{alert.title}</p>
                <p className="text-muted text-2xs leading-relaxed">{alert.message}</p>
                <div className="rounded-lg bg-surface border border-line/60 p-2 text-2xs text-ink flex items-start gap-1.5">
                  <Info size={12} className="text-brand-500 shrink-0 mt-0.5" />
                  <span>{alert.actionRecommendation}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ================= TWO CORE NAVIGATION PATHS ================= */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* CARD 1: CITY ROUTE NETWORKS */}
        <div
          onClick={() => setSelectedCategory("CITY_ROUTE")}
          className={`cursor-pointer rounded-3xl border p-6 transition shadow-2xs group flex flex-col justify-between ${
            selectedCategory === "CITY_ROUTE"
              ? "border-brand-600 bg-panel ring-2 ring-brand-500/30 shadow-md"
              : "border-line bg-panel hover:border-brand-500/60"
          }`}
        >
          <div>
            <div className="flex items-center justify-between mb-4">
              <div
                className={`flex h-12 w-12 items-center justify-center rounded-2xl transition ${
                  selectedCategory === "CITY_ROUTE"
                    ? "bg-brand-600 text-white shadow-xs scale-105"
                    : "bg-brand-500/10 text-brand-600 group-hover:scale-105"
                }`}
              >
                <Bus size={24} />
              </div>
              <span className="rounded-full bg-brand-500/10 px-3 py-1 text-xs font-extrabold text-brand-600">
                {cityCount} Lines Configured
              </span>
            </div>

            <h3 className="font-extrabold text-lg text-ink group-hover:text-brand-600 transition">
              Planned Routes
            </h3>
            <p className="text-xs text-muted mt-1 leading-relaxed">
              Morning Inbound (07:15–08:30 AM) and Evening Outbound (03:45 PM) express commuter routes covering Farid Town Point, Mall Road, High Court, and Canal corridors.
            </p>
          </div>

          <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between text-xs">
            <span className="font-semibold text-muted">Long-Distance & Commuters</span>
            <span
              className={`font-bold flex items-center gap-1 ${
                selectedCategory === "CITY_ROUTE" ? "text-brand-600" : "text-muted"
              }`}
            >
              <span>{selectedCategory === "CITY_ROUTE" ? "Active View" : "Switch to Routes"}</span>
              <ArrowRight size={13} />
            </span>
          </div>
        </div>

        {/* CARD 2: INTER-CAMPUS & INTRA-DAY SHUTTLES */}
        <div
          onClick={() => setSelectedCategory("CAMPUS_SHUTTLE")}
          className={`cursor-pointer rounded-3xl border p-6 transition shadow-2xs group flex flex-col justify-between ${
            selectedCategory === "CAMPUS_SHUTTLE"
              ? "border-cyan-600 bg-panel ring-2 ring-cyan-500/30 shadow-md"
              : "border-line bg-panel hover:border-cyan-500/60"
          }`}
        >
          <div>
            <div className="flex items-center justify-between mb-4">
              <div
                className={`flex h-12 w-12 items-center justify-center rounded-2xl transition ${
                  selectedCategory === "CAMPUS_SHUTTLE"
                    ? "bg-cyan-600 text-white shadow-xs scale-105"
                    : "bg-cyan-500/10 text-cyan-600 group-hover:scale-105"
                }`}
              >
                <Navigation size={24} />
              </div>
              <span className="rounded-full bg-cyan-500/10 px-3 py-1 text-xs font-extrabold text-cyan-600">
                Every 15–20 Mins Loop
              </span>
            </div>

            <h3 className="font-extrabold text-lg text-ink group-hover:text-cyan-600 transition">
              Shuttle Schedule
            </h3>
            <p className="text-xs text-muted mt-1 leading-relaxed">
              High-frequency circular loops between Allama Iqbal & Fatima Jinnah Hostels, Central Library, CS Block C Quadrangle, and the Sports Complex & Gym arena.
            </p>
          </div>

          <div className="mt-5 pt-3 border-t border-line/60 flex items-center justify-between text-xs">
            <span className="font-semibold text-muted">Continuous Intra-Day Transit</span>
            <span
              className={`font-bold flex items-center gap-1 ${
                selectedCategory === "CAMPUS_SHUTTLE" ? "text-cyan-600" : "text-muted"
              }`}
            >
              <span>{selectedCategory === "CAMPUS_SHUTTLE" ? "Active View" : "Switch to Shuttles"}</span>
              <ArrowRight size={13} />
            </span>
          </div>
        </div>
      </div>

      {/* ================= STOP LOOKUP & TELEMETRY CONTROLS BAR ================= */}
      <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex-1 min-w-[280px]">
            <label className="block text-xs font-bold text-ink mb-1.5 flex items-center gap-1.5">
              <Search size={13} className="text-brand-500" />
              <span>Where are you waiting? (Live Stop ETA Finder)</span>
            </label>
            <div className="relative">
              <input
                type="text"
                placeholder="Search by stop name e.g. Farid Town Point, High Court, Girls Hostel, Central Library..."
                value={stopSearchQuery}
                onChange={(e) => setStopSearchQuery(e.target.value)}
                className="w-full rounded-xl border border-line bg-surface px-3 py-2 pl-9 text-xs text-ink placeholder:text-muted focus:outline-hidden focus:ring-2 focus:ring-brand-500"
              />
              <MapPin size={14} className="absolute left-3 top-2.5 text-muted" />
              {stopSearchQuery && (
                <button
                  onClick={() => setStopSearchQuery("")}
                  className="absolute right-3 top-2.5 text-muted hover:text-ink"
                >
                  <X size={13} />
                </button>
              )}
            </div>
          </div>

          {/* Quick Telemetry Refresh */}
          <div className="flex items-center gap-3 self-end pt-1">
            <div className="text-right hidden sm:block">
              <p className="text-2xs text-muted">Sensor Ping</p>
              <p className="font-mono text-2xs font-bold text-ink">{lastRefreshedAt}</p>
            </div>
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="inline-flex items-center gap-2 rounded-xl border border-line bg-surface px-3.5 py-2 text-xs font-bold text-ink hover:border-brand-500 hover:text-brand-600 transition shadow-xs disabled:opacity-50"
            >
              <RefreshCw size={13} className={isRefreshing ? "animate-spin text-brand-600" : ""} />
              <span>{isRefreshing ? "Ping GPS…" : "Refresh GPS"}</span>
            </button>
          </div>
        </div>

        {/* Popular Stop Chips */}
        <div className="flex flex-wrap items-center gap-1.5 pt-1 border-t border-line/60">
          <span className="text-2xs font-bold uppercase tracking-wider text-muted mr-1">
            Popular Stops:
          </span>
          {[
            "Farid Town Point",
            "Jinnah Hall Chowk",
            "Fatima Jinnah Girls Hostel",
            "High Court & Bar Council",
            "Central Library",
            "Sports Complex"
          ].map((chip) => (
            <button
              key={chip}
              onClick={() => setStopSearchQuery(chip)}
              className={`rounded-lg px-2.5 py-1 text-2xs font-semibold transition border ${
                stopSearchQuery === chip
                  ? "border-brand-500 bg-brand-500/10 text-brand-600 font-bold"
                  : "border-line bg-surface text-muted hover:text-ink hover:border-brand-500/40"
              }`}
            >
              {chip}
            </button>
          ))}
          {stopSearchQuery && (
            <button
              onClick={() => setStopSearchQuery("")}
              className="ml-auto text-2xs font-semibold text-muted hover:text-red-500 transition"
            >
              Clear Search
            </button>
          )}
        </div>
      </div>

      {/* ================= STOP SEARCH MATCHES BANNER ================= */}
      {stopSearchQuery && searchedStopMatches.length > 0 && (
        <div className="rounded-2xl border border-brand-500/40 bg-brand-500/5 p-4 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="font-bold text-xs text-ink flex items-center gap-2">
              <MapPin size={14} className="text-brand-600" />
              <span>
                Buses reaching stop matching: <strong className="text-brand-600">"{stopSearchQuery}"</strong>
              </span>
            </h4>
            <span className="text-2xs font-semibold text-muted">
              {searchedStopMatches.length} Line{searchedStopMatches.length > 1 ? "s" : ""} Found
            </span>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {searchedStopMatches.map(({ route, stop }) => (
              <div
                key={`${route.id}-${stop.id}`}
                className="rounded-xl border border-line bg-panel p-3 space-y-2 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-brand-600">{route.bus.busNumber}</span>
                  <span
                    className={`rounded-full px-2 py-0.5 text-2xs font-bold ${
                      stop.delayMinutes === 0
                        ? "bg-emerald-500/15 text-emerald-600"
                        : "bg-amber-500/15 text-amber-700 dark:text-amber-300"
                    }`}
                  >
                    {stop.delayMinutes === 0 ? "On Time" : `+${stop.delayMinutes}m Delay`}
                  </span>
                </div>
                <div>
                  <p className="font-bold text-ink">{stop.name}</p>
                  <p className="text-2xs text-muted">{route.name}</p>
                </div>
                <div className="rounded-lg bg-surface border border-line/60 p-2 flex items-center justify-between text-2xs">
                  <div>
                    <span className="text-muted block">Scheduled</span>
                    <span className="font-mono font-semibold text-ink">{stop.scheduledTime}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-muted block">Estimated ETA</span>
                    <span className="font-mono font-extrabold text-brand-600 text-xs">
                      {stop.estimatedArrival}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ================= ROUTES LIST WITH STOP-BY-STOP ITINERARY ================= */}
      <div className="space-y-6">
        <div className="flex items-center justify-between px-1">
          <div>
            <h3 className="font-extrabold text-base text-ink">
              {selectedCategory === "CITY_ROUTE"
                ? "City Route Networks (Stop-by-Stop Schedule)"
                : "Inter-Campus Shuttle Loops (High-Frequency Transit)"}
            </h3>
            <p className="text-xs text-muted mt-0.5">
              Live GPS telemetry, stop-by-stop scheduled times vs ETAs, driver contacts, and seat capacity.
            </p>
          </div>

          <span className="rounded-full bg-surface border border-line px-3 py-1 text-xs font-semibold text-muted">
            Showing {filteredRoutes.length} Line{filteredRoutes.length > 1 ? "s" : ""}
          </span>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {filteredRoutes.map((route) => {
            const isExpanded = expandedRouteId === route.id;
            const isFull = route.bus.capacityStatus === "FULL";
            const isStanding = route.bus.capacityStatus === "STANDING_ONLY";

            return (
              <div
                key={route.id}
                className="rounded-3xl border border-line bg-panel p-6 shadow-2xs space-y-5 flex flex-col justify-between hover:border-brand-500/50 transition group"
              >
                <div className="space-y-4">
                  {/* Top Bar: Bus Number, Direction & Status */}
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-extrabold text-sm rounded-lg bg-brand-500/10 text-brand-600 px-2.5 py-1">
                          {route.bus.busNumber}
                        </span>
                        <span className="rounded-md bg-surface border border-line px-2 py-0.5 text-2xs font-semibold text-muted">
                          {route.direction === "INBOUND_MORNING"
                            ? "Morning Inbound"
                            : route.direction === "OUTBOUND_EVENING"
                            ? "Evening Outbound"
                            : "Circular Loop"}
                        </span>
                      </div>
                      <h4 className="font-extrabold text-base text-ink mt-2 group-hover:text-brand-600 transition">
                        {route.name}
                      </h4>
                      <p className="text-xs text-muted line-clamp-1">{route.subtitle}</p>
                    </div>

                    {/* Overall Status Badge */}
                    <div className="text-right shrink-0">
                      <span
                        className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-2xs font-extrabold ${
                          route.overallStatus === "ON_TIME"
                            ? "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300"
                            : route.overallStatus === "MINOR_DELAY"
                            ? "bg-amber-500/15 text-amber-700 dark:text-amber-300"
                            : "bg-rose-500/15 text-rose-700 dark:text-rose-300"
                        }`}
                      >
                        <span className="flex h-1.5 w-1.5 rounded-full bg-current animate-pulse" />
                        <span>
                          {route.overallStatus === "ON_TIME"
                            ? "On Schedule"
                            : route.overallStatus === "MINOR_DELAY"
                            ? "Minor Delay"
                            : "Disrupted"}
                        </span>
                      </span>
                      <p className="font-mono text-2xs text-muted mt-1">
                        Departs: <strong className="text-ink">{route.departureTime}</strong>
                      </p>
                    </div>
                  </div>

                  {/* Real-Time Telemetry Bar */}
                  <div className="rounded-2xl border border-line/60 bg-surface/50 p-3.5 space-y-2.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="flex items-center gap-1.5 text-muted">
                        <Navigation size={13} className="text-brand-500" />
                        <span>Current Fleet Position</span>
                      </span>
                      <span className="font-bold text-ink text-right">{route.currentLocationDesc}</span>
                    </div>

                    <div className="grid grid-cols-3 gap-2 pt-2 border-t border-line/40 text-2xs">
                      <div>
                        <span className="text-muted block">GPS Speed</span>
                        <span className="font-mono font-bold text-ink">{route.bus.speedKmh} km/h</span>
                      </div>
                      <div>
                        <span className="text-muted block">Amenities</span>
                        <span className="font-semibold text-ink flex items-center gap-1 mt-0.5">
                          {route.bus.hasAC && (
                            <span title="Air Conditioned">
                              <Wind size={11} className="text-sky-500" />
                            </span>
                          )}
                          {route.bus.hasWifi && (
                            <span title="High-Speed Wi-Fi">
                              <Wifi size={11} className="text-emerald-500" />
                            </span>
                          )}
                          <span>{route.bus.hasAC ? "AC Active" : "Non-AC"}</span>
                        </span>
                      </div>
                      <div className="text-right">
                        <span className="text-muted block">Signal Ping</span>
                        <span className="font-mono text-muted">{route.bus.lastPingSecondsAgo}s ago</span>
                      </div>
                    </div>
                  </div>

                  {/* Bus Capacity Segmented Status Meter */}
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      <span className="flex items-center gap-1.5 text-muted">
                        <Users size={12} className="text-brand-500" />
                        <span>Passenger Occupancy</span>
                      </span>
                      <span
                        className={`font-bold rounded-full px-2 py-0.5 text-2xs ${
                          isFull
                            ? "bg-rose-500/15 text-rose-600"
                            : isStanding
                            ? "bg-amber-500/15 text-amber-700 dark:text-amber-300"
                            : "bg-emerald-500/15 text-emerald-600"
                        }`}
                      >
                        {isFull ? "Full / At Capacity" : isStanding ? "Standing Only" : "Seats Available"} (
                        {route.bus.occupiedSeats}/{route.bus.totalSeats})
                      </span>
                    </div>

                    <div className="h-2 w-full rounded-full bg-surface overflow-hidden border border-line/60">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          isFull ? "bg-rose-500" : isStanding ? "bg-amber-500" : "bg-emerald-500"
                        }`}
                        style={{
                          width: `${Math.min((route.bus.occupiedSeats / route.bus.totalSeats) * 100, 100)}%`
                        }}
                      />
                    </div>
                  </div>

                  {/* Driver Contact & Vehicle Info */}
                  <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-line/50 bg-panel p-3 text-xs">
                    <div>
                      <p className="font-bold text-ink flex items-center gap-1.5">
                        <span>{route.bus.driverName}</span>
                        <span className="text-2xs font-normal text-muted">({route.bus.model})</span>
                      </p>
                      <p className="font-mono text-2xs text-muted">Plate: {route.bus.licensePlate}</p>
                    </div>

                    <a
                      href={`tel:${route.bus.driverPhone}`}
                      className="inline-flex items-center gap-1.5 rounded-xl border border-brand-500/40 bg-brand-500/10 px-3 py-1.5 text-xs font-bold text-brand-600 hover:bg-brand-500/20 transition"
                      title="Direct phone link to bus driver for lost items or urgent stop inquiries"
                    >
                      <Phone size={12} />
                      <span>{route.bus.driverPhone}</span>
                    </a>
                  </div>

                  {/* ================= STOP-BY-STOP ITINERARY TIMELINE ================= */}
                  <div className="space-y-3 pt-2 border-t border-line/60">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-extrabold text-ink uppercase tracking-wider flex items-center gap-1.5">
                        <Clock size={13} className="text-brand-500" />
                        <span>Complete Stop-by-Stop Schedule ({route.stops.length} Stops)</span>
                      </span>
                      <button
                        onClick={() => setExpandedRouteId(isExpanded ? null : route.id)}
                        className="text-2xs font-bold text-brand-600 hover:underline flex items-center gap-0.5"
                      >
                        <span>{isExpanded ? "Show All Stops" : "Compact View"}</span>
                        {isExpanded ? <ChevronDown size={12} /> : <ChevronUp size={12} />}
                      </button>
                    </div>

                    {/* Timeline stops — show ALL stops by default */}
                    <div className="space-y-3 relative pl-5 border-l-2 border-brand-500/30">
                      {(!isExpanded ? route.stops : route.stops.slice(0, 3)).map((stop) => {
                        const isPassed = stop.status === "PASSED";
                        const isApproaching = stop.status === "APPROACHING";
                        const isSubscribed = subscribedStops[stop.id];

                        return (
                          <div key={stop.id} className="relative group/stop">
                            {/* Timeline Node Marker */}
                            <span
                              className={`absolute -left-[27px] top-1 flex h-4 w-4 items-center justify-center rounded-full border-2 bg-panel transition ${
                                isPassed
                                  ? "border-emerald-500 text-emerald-500"
                                  : isApproaching
                                  ? "border-amber-500 text-amber-500 ring-4 ring-amber-500/20"
                                  : "border-muted/60 text-muted"
                              }`}
                            >
                              {isPassed ? (
                                <CheckCircle2 size={10} className="fill-current" />
                              ) : isApproaching ? (
                                <span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-ping" />
                              ) : (
                                <span className="h-1.5 w-1.5 rounded-full bg-muted/60" />
                              )}
                            </span>

                            <div className="flex items-start justify-between gap-3 text-xs">
                              <div>
                                <div className="flex items-center gap-2">
                                  <span
                                    className={`font-bold transition ${
                                      isApproaching
                                        ? "text-amber-700 dark:text-amber-300 font-extrabold"
                                        : isPassed
                                        ? "text-muted line-through"
                                        : "text-ink"
                                    }`}
                                  >
                                    {stop.name}
                                  </span>
                                  {isApproaching && (
                                    <span className="rounded-full bg-amber-500/20 px-2 py-0.2 text-[9px] font-extrabold text-amber-800 dark:text-amber-300 animate-pulse">
                                      NEXT STOP
                                    </span>
                                  )}
                                </div>
                                <p className="text-2xs text-muted mt-0.5">{stop.landmark}</p>
                              </div>

                              {/* Time Display */}
                              <div className="text-right shrink-0">
                                <div className="flex items-center gap-1.5 justify-end">
                                  <span className="text-2xs text-muted line-through">
                                    {stop.scheduledTime}
                                  </span>
                                  <span
                                    className={`font-mono font-extrabold text-xs ${
                                      stop.delayMinutes === 0
                                        ? "text-emerald-600"
                                        : "text-amber-600 font-bold"
                                    }`}
                                  >
                                    {stop.estimatedArrival}
                                  </span>
                                </div>
                                <span className="text-[10px] text-muted block">
                                  {stop.delayMinutes === 0
                                    ? "On Time"
                                    : `+${stop.delayMinutes}m ETA delay`}
                                </span>
                              </div>
                            </div>

                            {/* Optional Notification Bell for Stop */}
                            <div className="pt-1 flex items-center justify-end">
                              <button
                                onClick={() => toggleStopAlert(stop.id, stop.name)}
                                className={`text-[10px] font-semibold inline-flex items-center gap-1 transition ${
                                  isSubscribed
                                    ? "text-brand-600 font-bold"
                                    : "text-muted hover:text-ink"
                                }`}
                              >
                                <Bell size={10} className={isSubscribed ? "fill-current" : ""} />
                                <span>{isSubscribed ? "Arrival Alert Set" : "Notify Me"}</span>
                              </button>
                            </div>
                          </div>
                        );
                      })}

                      {isExpanded && route.stops.length > 3 && (
                        <button
                          onClick={() => setExpandedRouteId(null)}
                          className="text-2xs font-bold text-brand-600 hover:underline pt-1 block"
                        >
                          + {route.stops.length - 3} more stops along this line…
                        </button>
                      )}
                    </div>
                  </div>
                </div>

                {/* Card Bottom Status Summary */}
                <div className="mt-4 pt-3 border-t border-line/60 flex items-center justify-between text-2xs text-muted">
                  <span>Operating: {route.operatingDays}</span>
                  <span className="font-semibold text-ink">{route.delaySummary}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
