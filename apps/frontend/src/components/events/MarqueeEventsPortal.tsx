import { useState, useMemo } from "react";
import {
  Trophy,
  Calendar,
  Clock,
  MapPin,
  Users,
  Award,
  Sparkles,
  Laptop,
  GraduationCap,
  Bell,
  CheckCircle2,
  Filter,
  ArrowRight,
  ChevronRight,
  Flame,
  Activity,
  ShieldAlert,
  Code,
  Terminal,
  Briefcase,
  X,
  ExternalLink
} from "lucide-react";

import {
  SPORTS_FIXTURES,
  DEPARTMENT_STANDINGS,
  TOURNAMENT_BRACKETS,
  TECH_GALA_EVENTS,
  CAREER_FAIR_COMPANIES,
  type MarqueeSeasonMode,
  type TournamentMatch,
  type TechGalaCompetition,
  type CareerFairCompany
} from "../../features/events/marquee-events-data";

interface Props {
  initialMode?: MarqueeSeasonMode;
}

export function MarqueeEventsPortal({ initialMode = "SPORTS_GALA" }: Props) {
  const [activeSeason, setActiveSeason] = useState<MarqueeSeasonMode>(initialMode);

  // Sports Tournament sub-tabs
  const [sportsSubTab, setSportsSubTab] = useState<"fixtures" | "brackets" | "standings">("fixtures");

  // Fixtures filters
  const [filterDay, setFilterDay] = useState<string>("All");
  const [filterSport, setFilterSport] = useState<string>("All");
  const [filterDept, setFilterDept] = useState<string>("All");

  // Subscribed departments / sports notifications
  const [followedDepartments, setFollowedDepartments] = useState<string[]>(["Computer Science"]);
  const [followedMatches, setFollowedMatches] = useState<Record<string, boolean>>({});

  // Modals
  const [registeredComp, setRegisteredComp] = useState<TechGalaCompetition | null>(null);
  const [interviewBookingCompany, setInterviewBookingCompany] = useState<CareerFairCompany | null>(null);
  const [teamNameInput, setTeamNameInput] = useState("");
  const [regSuccess, setRegSuccess] = useState(false);

  // Toggle department follow
  const toggleFollowDept = (dept: string) => {
    setFollowedDepartments((prev) =>
      prev.includes(dept) ? prev.filter((d) => d !== dept) : [...prev, dept]
    );
  };

  // Toggle match alert
  const toggleMatchAlert = (matchId: string) => {
    setFollowedMatches((prev) => ({
      ...prev,
      [matchId]: !prev[matchId]
    }));
  };

  // Filtered fixtures
  const filteredFixtures = useMemo(() => {
    return SPORTS_FIXTURES.filter((m) => {
      if (filterDay !== "All" && m.day !== filterDay) return false;
      if (filterSport !== "All" && m.sport !== filterSport) return false;
      if (
        filterDept !== "All" &&
        m.teamA.department !== filterDept &&
        m.teamB.department !== filterDept
      ) {
        return false;
      }
      return true;
    });
  }, [filterDay, filterSport, filterDept]);

  // Ordered sports week days for grouping & top selector
  const SPORTS_DAYS = [
    "Day 1 (Monday)",
    "Day 2 (Tuesday)",
    "Day 3 (Wednesday)",
    "Day 4 (Thursday)",
    "Day 5 (Friday)"
  ] as const;

  // Group filtered fixtures chronologically by day
  const fixturesByDay = useMemo(() => {
    const groups: { day: string; matches: TournamentMatch[] }[] = [];
    for (const day of SPORTS_DAYS) {
      const dayMatches = filteredFixtures.filter((m) => m.day === day);
      if (dayMatches.length > 0) {
        groups.push({ day, matches: dayMatches });
      }
    }
    return groups;
  }, [filteredFixtures]);

  // Live match count
  const liveCount = SPORTS_FIXTURES.filter((m) => m.status === "LIVE_NOW").length;

  return (
    <div className="space-y-6">
      {/* ================= MARQUEE SEASON ARCHITECTURE SELECTOR ================= */}
      <div className="rounded-3xl border border-line bg-panel p-6 shadow-2xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="flex h-2.5 w-2.5 rounded-full bg-rose-500 animate-pulse" />
              <h3 className="text-base font-extrabold text-ink">
                Campus Life, Marquee Events & Gala Engine
              </h3>
              <span className="rounded-full bg-rose-500/10 px-2.5 py-0.5 text-2xs font-extrabold text-rose-600">
                Dynamic Academic Calendar Morphing
              </span>
            </div>
            <p className="text-xs text-muted mt-1">
              Platform dynamically transforms between athletic championships, coding hackathons, and employer convocations.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-2xs font-bold text-muted uppercase tracking-wider hidden sm:block">
              University Calendar Mode:
            </span>
            <div className="inline-flex rounded-2xl border border-line bg-surface p-1 shadow-2xs">
              <button
                onClick={() => setActiveSeason("SPORTS_GALA")}
                className={`inline-flex items-center gap-1.5 rounded-xl px-3.5 py-2 text-xs font-bold transition ${
                  activeSeason === "SPORTS_GALA"
                    ? "bg-rose-600 text-white shadow-xs"
                    : "text-muted hover:text-ink"
                }`}
              >
                <Trophy size={14} />
                <span>Sports Olympiad (Spring)</span>
              </button>

              <button
                onClick={() => setActiveSeason("TECH_GALA")}
                className={`inline-flex items-center gap-1.5 rounded-xl px-3.5 py-2 text-xs font-bold transition ${
                  activeSeason === "TECH_GALA"
                    ? "bg-indigo-600 text-white shadow-xs"
                    : "text-muted hover:text-ink"
                }`}
              >
                <Code size={14} />
                <span>Tech Gala & Hackathon (Fall)</span>
              </button>

              <button
                onClick={() => setActiveSeason("CAREER_CONVOCATION")}
                className={`inline-flex items-center gap-1.5 rounded-xl px-3.5 py-2 text-xs font-bold transition ${
                  activeSeason === "CAREER_CONVOCATION"
                    ? "bg-emerald-600 text-white shadow-xs"
                    : "text-muted hover:text-ink"
                }`}
              >
                <GraduationCap size={14} />
                <span>Career Fair & Convocation (Winter)</span>
              </button>
            </div>
          </div>
        </div>

        {/* Following Department Alert Strip */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-line/60 text-xs text-muted">
          <div className="flex items-center gap-2">
            <Bell size={13} className="text-rose-500" />
            <span>Following Department Notifications:</span>
            {["Computer Science", "Software Engineering", "Electrical Engineering", "Management Sciences"].map((dept) => {
              const isFollowed = followedDepartments.includes(dept);
              return (
                <button
                  key={dept}
                  onClick={() => toggleFollowDept(dept)}
                  className={`rounded-lg px-2.5 py-0.5 text-2xs font-bold transition border ${
                    isFollowed
                      ? "border-rose-500 bg-rose-500/10 text-rose-600 font-extrabold"
                      : "border-line bg-surface text-muted hover:text-ink"
                  }`}
                >
                  {isFollowed ? `✓ Following ${dept.split(" ")[0]}` : `+ ${dept.split(" ")[0]}`}
                </button>
              );
            })}
          </div>

          <span className="text-2xs text-emerald-600 font-semibold">
            ● Push Alerts Active (15m before match start)
          </span>
        </div>
      </div>

      {/* ================= MODE 1: SPORTS OLYMPIAD GALA (TOURNAMENT ENGINE) ================= */}
      {activeSeason === "SPORTS_GALA" && (
        <div className="space-y-6 animate-in fade-in duration-200">
          {/* Sub-tabs: Fixtures vs Brackets vs Standings */}
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-line pb-3">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setSportsSubTab("fixtures")}
                className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-bold transition ${
                  sportsSubTab === "fixtures"
                    ? "bg-rose-600 text-white shadow-xs"
                    : "bg-panel text-muted hover:text-ink border border-line"
                }`}
              >
                <Flame size={14} />
                <span>Live Fixtures & Results</span>
                {liveCount > 0 && (
                  <span className="rounded-full bg-white/20 px-2 py-0.2 text-[10px] font-black animate-pulse">
                    {liveCount} LIVE
                  </span>
                )}
              </button>

              <button
                onClick={() => setSportsSubTab("brackets")}
                className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-bold transition ${
                  sportsSubTab === "brackets"
                    ? "bg-rose-600 text-white shadow-xs"
                    : "bg-panel text-muted hover:text-ink border border-line"
                }`}
              >
                <Activity size={14} />
                <span>Knockout Elimination Brackets</span>
              </button>

              <button
                onClick={() => setSportsSubTab("standings")}
                className={`inline-flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-bold transition ${
                  sportsSubTab === "standings"
                    ? "bg-rose-600 text-white shadow-xs"
                    : "bg-panel text-muted hover:text-ink border border-line"
                }`}
              >
                <Award size={14} />
                <span>Points Table & Overall Trophy</span>
              </button>
            </div>

            <div className="text-xs text-muted">
              Annual Inter-Departmental Championship · Sahiwal Sports Complex
            </div>
          </div>

          {/* SUB-VIEW 1: FIXTURES & RESULTS */}
          {sportsSubTab === "fixtures" && (
            <div className="space-y-6">
              {/* Top Day Selector Pills */}
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={() => setFilterDay("All")}
                  className={`rounded-xl px-4 py-2 text-xs font-bold transition ${
                    filterDay === "All"
                      ? "bg-rose-600 text-white shadow-xs"
                      : "bg-panel text-muted border border-line hover:text-ink"
                  }`}
                >
                  All Days (Full Week)
                </button>
                {SPORTS_DAYS.map((day) => (
                  <button
                    key={day}
                    type="button"
                    onClick={() => setFilterDay(day)}
                    className={`rounded-xl px-4 py-2 text-xs font-bold transition ${
                      filterDay === day
                        ? "bg-rose-600 text-white shadow-xs"
                        : "bg-panel text-muted border border-line hover:text-ink"
                    }`}
                  >
                    {day}
                  </button>
                ))}
              </div>

              {/* Filter Bar */}
              <div className="rounded-2xl border border-line bg-panel p-5 shadow-2xs space-y-4">
                <div className="flex flex-wrap items-center gap-4 text-xs">
                  {/* Day Filter */}
                  <div>
                    <label className="block font-bold text-muted mb-1 flex items-center gap-1">
                      <Calendar size={12} className="text-rose-500" />
                      <span>Filter Day:</span>
                    </label>
                    <select
                      value={filterDay}
                      onChange={(e) => setFilterDay(e.target.value)}
                      className="rounded-xl border border-line bg-surface px-3 py-1.5 font-semibold text-ink focus:outline-hidden"
                    >
                      <option value="All">All 5 Days (Full Gala)</option>
                      <option value="Day 1 (Monday)">Day 1 (Monday)</option>
                      <option value="Day 2 (Tuesday)">Day 2 (Tuesday)</option>
                      <option value="Day 3 (Wednesday)">Day 3 (Wednesday)</option>
                      <option value="Day 4 (Thursday)">Day 4 (Thursday)</option>
                      <option value="Day 5 (Friday)">Day 5 (Friday - Finals)</option>
                    </select>
                  </div>

                  {/* Sport Filter */}
                  <div>
                    <label className="block font-bold text-muted mb-1 flex items-center gap-1">
                      <Trophy size={12} className="text-rose-500" />
                      <span>Sport:</span>
                    </label>
                    <select
                      value={filterSport}
                      onChange={(e) => setFilterSport(e.target.value)}
                      className="rounded-xl border border-line bg-surface px-3 py-1.5 font-semibold text-ink focus:outline-hidden"
                    >
                      <option value="All">All Disciplines</option>
                      <option value="Cricket">Cricket</option>
                      <option value="Futsal">Futsal / Football</option>
                      <option value="Badminton">Badminton</option>
                      <option value="Basketball">Basketball</option>
                      <option value="Table Tennis">Table Tennis</option>
                      <option value="Chess">Chess</option>
                    </select>
                  </div>

                  {/* Department Filter */}
                  <div>
                    <label className="block font-bold text-muted mb-1 flex items-center gap-1">
                      <Users size={12} className="text-rose-500" />
                      <span>Department:</span>
                    </label>
                    <select
                      value={filterDept}
                      onChange={(e) => setFilterDept(e.target.value)}
                      className="rounded-xl border border-line bg-surface px-3 py-1.5 font-semibold text-ink focus:outline-hidden"
                    >
                      <option value="All">All Departments</option>
                      <option value="Computer Science">Computer Science (CS)</option>
                      <option value="Software Engineering">Software Engineering (SE)</option>
                      <option value="Electrical Engineering">Electrical Engineering (EE)</option>
                      <option value="Management Sciences">Management Sciences (MS)</option>
                    </select>
                  </div>

                  {(filterDay !== "All" || filterSport !== "All" || filterDept !== "All") && (
                    <button
                      onClick={() => {
                        setFilterDay("All");
                        setFilterSport("All");
                        setFilterDept("All");
                      }}
                      className="ml-auto text-2xs font-semibold text-muted hover:text-red-500 self-end py-1.5"
                    >
                      Reset Filters
                    </button>
                  )}
                </div>
              </div>

              {/* Match Fixture Cards Grouped by Day */}
              <div className="space-y-8">
                {fixturesByDay.map((group) => (
                  <div key={group.day} className="space-y-4">
                    <div className="flex items-center justify-between border-b border-line pb-2">
                      <h3 className="font-extrabold text-base text-ink flex items-center gap-2">
                        <Calendar size={16} className="text-rose-600" />
                        <span>{group.day}</span>
                      </h3>
                      <span className="rounded-full bg-rose-500/10 px-2.5 py-0.5 text-xs font-bold text-rose-600">
                        {group.matches.length} {group.matches.length === 1 ? "Game" : "Games"} Scheduled
                      </span>
                    </div>

                    <div className="grid gap-5 md:grid-cols-2">
                      {group.matches.map((match) => {
                  const isLive = match.status === "LIVE_NOW";
                  const isSubscribed = followedMatches[match.id];

                  return (
                    <div
                      key={match.id}
                      className={`flex flex-col justify-between rounded-3xl border p-5 shadow-2xs transition group ${
                        isLive
                          ? "border-rose-500/80 bg-rose-500/5 ring-2 ring-rose-500/20"
                          : "border-line bg-panel hover:border-rose-500/50"
                      }`}
                    >
                      <div className="space-y-4">
                        {/* Match Header: Sport, Stage, Status */}
                        <div className="flex items-center justify-between border-b border-line pb-3">
                          <div className="flex items-center gap-2">
                            <span className="rounded-lg bg-rose-500/10 px-2.5 py-1 font-extrabold text-xs text-rose-600">
                              {match.sport}
                            </span>
                            <span className="rounded-md bg-surface border border-line px-2 py-0.5 text-2xs font-semibold text-muted">
                              {match.stage}
                            </span>
                          </div>

                          {isLive ? (
                            <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-600 px-3 py-1 text-2xs font-black text-white shadow-xs animate-pulse">
                              <span className="h-2 w-2 rounded-full bg-white" />
                              <span>LIVE NOW</span>
                            </span>
                          ) : match.status === "COMPLETED" ? (
                            <span className="rounded-full bg-surface border border-line px-2.5 py-0.5 text-2xs font-bold text-muted">
                              Final Result
                            </span>
                          ) : (
                            <span className="rounded-full bg-indigo-500/10 px-2.5 py-0.5 text-2xs font-bold text-indigo-600">
                              Scheduled
                            </span>
                          )}
                        </div>

                        {/* Teams & Scoreboard */}
                        <div className="rounded-2xl border border-line/60 bg-surface/50 p-4 space-y-3">
                          {/* Team A */}
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2.5">
                              <span className={`flex h-6 w-6 items-center justify-center rounded-lg text-2xs font-extrabold ${match.teamA.jerseyColor}`}>
                                {match.teamA.department.split(" ")[0]![0]}
                              </span>
                              <div>
                                <p className={`font-extrabold text-sm ${match.teamA.isWinner ? "text-rose-600 font-black" : "text-ink"}`}>
                                  {match.teamA.name}
                                </p>
                                <p className="text-[10px] text-muted">{match.teamA.department}</p>
                              </div>
                            </div>
                            {match.teamA.score && (
                              <span className="font-mono font-black text-sm text-ink">
                                {match.teamA.score}
                              </span>
                            )}
                          </div>

                          <div className="border-t border-line/40 flex items-center justify-center -my-1">
                            <span className="bg-panel px-2 text-[10px] font-bold text-muted/60 uppercase">VS</span>
                          </div>

                          {/* Team B */}
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2.5">
                              <span className={`flex h-6 w-6 items-center justify-center rounded-lg text-2xs font-extrabold ${match.teamB.jerseyColor}`}>
                                {match.teamB.department.split(" ")[0]![0]}
                              </span>
                              <div>
                                <p className={`font-extrabold text-sm ${match.teamB.isWinner ? "text-rose-600 font-black" : "text-ink"}`}>
                                  {match.teamB.name}
                                </p>
                                <p className="text-[10px] text-muted">{match.teamB.department}</p>
                              </div>
                            </div>
                            {match.teamB.score && (
                              <span className="font-mono font-black text-sm text-ink">
                                {match.teamB.score}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Venue & Timing */}
                        <div className="space-y-1.5 text-xs text-muted">
                          <p className="flex items-center gap-1.5">
                            <MapPin size={13} className="text-rose-500 shrink-0" />
                            <span className="font-semibold text-ink">{match.venue}</span>
                            <span className="text-2xs text-muted">({match.groundMapZone})</span>
                          </p>
                          <p className="flex items-center gap-1.5">
                            <Clock size={13} className="text-brand-500 shrink-0" />
                            <span>{match.day} · <strong>{match.time}</strong></span>
                          </p>
                        </div>

                        {/* Summary Result / MVP */}
                        {match.summaryResult && (
                          <div className="rounded-xl bg-panel border border-line p-2.5 text-2xs space-y-0.5">
                            <p className="font-bold text-ink">Result: {match.summaryResult}</p>
                            {match.mvpPlayer && (
                              <p className="text-muted">⭐ MVP: <strong className="text-rose-600">{match.mvpPlayer}</strong></p>
                            )}
                          </div>
                        )}
                      </div>

                      {/* Card Action Footer */}
                      <div className="mt-4 pt-3 border-t border-line/60 flex items-center justify-between">
                        <span className="text-2xs text-muted">Official University Fixture</span>
                        <button
                          onClick={() => toggleMatchAlert(match.id)}
                          className={`inline-flex items-center gap-1 text-xs font-bold transition ${
                            isSubscribed ? "text-rose-600 font-extrabold" : "text-muted hover:text-ink"
                          }`}
                        >
                          <Bell size={12} className={isSubscribed ? "fill-current" : ""} />
                          <span>{isSubscribed ? "Alert Subscribed" : "Notify Match Start"}</span>
                        </button>
                      </div>
                    </div>
                  );
                })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SUB-VIEW 2: KNOCKOUT ELIMINATION BRACKETS */}
          {sportsSubTab === "brackets" && (
            <div className="rounded-3xl border border-line bg-panel p-6 shadow-2xs space-y-6">
              <div className="flex items-center justify-between border-b border-line pb-3">
                <div>
                  <h4 className="font-extrabold text-base text-ink">
                    Cricket Championship Elimination Bracket Tree
                  </h4>
                  <p className="text-xs text-muted mt-0.5">
                    Live progression from Quarter Finals to Semi Finals and Friday Grand Final.
                  </p>
                </div>
                <span className="rounded-full bg-rose-500/10 px-3 py-1 text-xs font-bold text-rose-600">
                  Single Elimination Knockout
                </span>
              </div>

              {/* Bracket Nodes Grid */}
              <div className="grid gap-6 md:grid-cols-3">
                {TOURNAMENT_BRACKETS.map((bracket) => (
                  <div key={bracket.round} className="space-y-4">
                    <div className="rounded-xl bg-surface border border-line p-2.5 text-center">
                      <span className="font-bold text-xs text-ink uppercase tracking-wider">
                        {bracket.round}
                      </span>
                    </div>

                    <div className="space-y-4">
                      {bracket.matches.map((bm) => (
                        <div
                          key={bm.id}
                          className="rounded-2xl border border-line bg-surface/50 p-3.5 space-y-2 hover:border-rose-500/60 transition shadow-2xs"
                        >
                          <div className="flex items-center justify-between text-2xs text-muted border-b border-line/40 pb-1.5">
                            <span>{bm.timing}</span>
                            <span className="font-semibold text-rose-600">Winner: {bm.winner}</span>
                          </div>

                          {/* Team 1 */}
                          <div className="flex items-center justify-between text-xs">
                            <span className={`font-bold ${bm.winner.includes(bm.team1) ? "text-rose-600 font-black" : "text-ink"}`}>
                              {bm.team1}
                            </span>
                            <span className="font-mono text-2xs text-muted">{bm.score1}</span>
                          </div>

                          {/* Team 2 */}
                          <div className="flex items-center justify-between text-xs">
                            <span className={`font-bold ${bm.winner.includes(bm.team2) ? "text-rose-600 font-black" : "text-ink"}`}>
                              {bm.team2}
                            </span>
                            <span className="font-mono text-2xs text-muted">{bm.score2}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SUB-VIEW 3: POINTS TABLE & OVERALL TROPHY STANDINGS */}
          {sportsSubTab === "standings" && (
            <div className="rounded-3xl border border-line bg-panel p-6 shadow-2xs space-y-6">
              <div className="flex items-center justify-between border-b border-line pb-3">
                <div>
                  <h4 className="font-extrabold text-base text-ink">
                    Overall Department Points Table & Sports Gala 2026 Trophy
                  </h4>
                  <p className="text-xs text-muted mt-0.5">
                    Accumulated points based on official Gold, Silver, and Bronze medal victories.
                  </p>
                </div>
                <div className="flex items-center gap-1.5 text-xs font-bold text-rose-600">
                  <Trophy size={16} />
                  <span>Championship Trophy</span>
                </div>
              </div>

              {/* Leaderboard Cards */}
              <div className="space-y-3">
                {DEPARTMENT_STANDINGS.map((dept) => (
                  <div
                    key={dept.code}
                    className={`flex flex-wrap items-center justify-between gap-4 rounded-2xl border p-4 transition shadow-2xs ${
                      dept.rank === 1
                        ? "border-amber-500/60 bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent"
                        : "border-line bg-surface/50"
                    }`}
                  >
                    <div className="flex items-center gap-3.5">
                      <div
                        className={`flex h-10 w-10 items-center justify-center rounded-xl font-mono font-black text-sm ${
                          dept.rank === 1
                            ? "bg-amber-500 text-white shadow-xs"
                            : dept.rank === 2
                            ? "bg-zinc-300 text-zinc-900"
                            : dept.rank === 3
                            ? "bg-amber-700 text-white"
                            : "bg-surface border border-line text-muted"
                        }`}
                      >
                        #{dept.rank}
                      </div>

                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-extrabold text-base text-ink">{dept.department}</h4>
                          <span className={`rounded-md px-2 py-0.5 text-2xs font-extrabold ${dept.colorScheme.badge}`}>
                            {dept.code}
                          </span>
                        </div>
                        <p className="text-2xs text-muted mt-0.5">{dept.keyStrength}</p>
                      </div>
                    </div>

                    {/* Medal Counts */}
                    <div className="flex items-center gap-6">
                      <div className="flex items-center gap-3 text-xs">
                        <span className="flex items-center gap-1 font-bold text-amber-600" title="Gold Medals">
                          <span>🥇</span>
                          <span>{dept.goldMedals}</span>
                        </span>
                        <span className="flex items-center gap-1 font-bold text-zinc-500" title="Silver Medals">
                          <span>🥈</span>
                          <span>{dept.silverMedals}</span>
                        </span>
                        <span className="flex items-center gap-1 font-bold text-amber-800" title="Bronze Medals">
                          <span>🥉</span>
                          <span>{dept.bronzeMedals}</span>
                        </span>
                      </div>

                      <div className="text-right min-w-[90px]">
                        <span className="text-2xs text-muted block uppercase font-bold">Total Points</span>
                        <span className="font-mono font-black text-lg text-ink">
                          {dept.totalPoints} PTS
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ================= MODE 2: TECH GALA & HACKATHON (FALL SESSION) ================= */}
      {activeSeason === "TECH_GALA" && (
        <div className="space-y-6 animate-in fade-in duration-200">
          {/* Hackathon Hero Timer */}
          <div className="rounded-3xl border border-indigo-500/40 bg-gradient-to-r from-indigo-500/15 via-purple-500/10 to-transparent p-6 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-6">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Terminal size={18} className="text-indigo-600" />
                  <h3 className="text-base font-extrabold text-ink">
                    HackCOMSATS 2026: 48-Hour AI Code Sprint
                  </h3>
                  <span className="rounded-full bg-indigo-500/20 px-2.5 py-0.5 text-2xs font-extrabold text-indigo-700 dark:text-indigo-300">
                    Live Code Sprint
                  </span>
                </div>
                <p className="text-xs text-muted">
                  Software Labs 1 & 2 · 28 Teams Competing · Total Prize Pool: <strong className="text-ink">PKR 500,000</strong>
                </p>
              </div>

              {/* Countdown Digits */}
              <div className="rounded-2xl border border-line bg-panel p-4 text-center min-w-[200px] shadow-xs">
                <span className="text-2xs font-bold text-muted uppercase tracking-wider block">
                  Time Remaining to Code Freeze
                </span>
                <span className="font-mono font-black text-2xl text-indigo-600">
                  18h : 42m : 19s
                </span>
                <span className="text-[10px] text-emerald-600 font-semibold block mt-0.5">
                  ● Mentors on Duty in Lab 1
                </span>
              </div>
            </div>
          </div>

          {/* Competitions Grid */}
          <div className="grid gap-6 md:grid-cols-2">
            {TECH_GALA_EVENTS.map((comp) => (
              <div
                key={comp.id}
                className="rounded-3xl border border-line bg-panel p-6 shadow-2xs space-y-4 flex flex-col justify-between hover:border-indigo-500/60 transition group"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <span className="rounded-md bg-indigo-500/10 px-2.5 py-0.5 text-2xs font-extrabold text-indigo-600">
                      {comp.category}
                    </span>
                    <span className="rounded-full bg-emerald-500/15 px-2.5 py-0.5 text-2xs font-bold text-emerald-600">
                      {comp.status === "HACKING_IN_PROGRESS" ? "In Progress" : "Registration Open"}
                    </span>
                  </div>

                  <div>
                    <h4 className="font-extrabold text-base text-ink group-hover:text-indigo-600 transition">
                      {comp.title}
                    </h4>
                    <p className="text-xs text-muted mt-0.5 flex items-center gap-1.5">
                      <MapPin size={12} className="text-brand-500 shrink-0" />
                      <span>{comp.venue}</span>
                    </p>
                  </div>

                  <div className="rounded-2xl border border-line/60 bg-surface/50 p-3 space-y-1.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-muted">Prize Pool</span>
                      <span className="font-bold text-emerald-600">{comp.prizePool}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-muted">Schedule Window</span>
                      <span className="font-semibold text-ink">{comp.timeWindow}</span>
                    </div>
                    <div className="flex items-center justify-between text-2xs text-muted pt-1 border-t border-line/40">
                      <span>Mentor: {comp.mentor}</span>
                      <span>{comp.registeredTeams} Teams Registered</span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => {
                    setRegisteredComp(comp);
                    setRegSuccess(false);
                    setTeamNameInput("");
                  }}
                  className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-indigo-600 py-2.5 text-xs font-bold text-white hover:bg-indigo-700 transition shadow-xs"
                >
                  <Code size={14} />
                  <span>Register Team / Submit Hack</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ================= MODE 3: CAREER FAIR & CONVOCATION (WINTER SESSION) ================= */}
      {activeSeason === "CAREER_CONVOCATION" && (
        <div className="space-y-6 animate-in fade-in duration-200">
          <div className="rounded-3xl border border-emerald-500/40 bg-gradient-to-r from-emerald-500/15 via-teal-500/10 to-transparent p-6 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-6">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Briefcase size={18} className="text-emerald-600" />
                  <h3 className="text-base font-extrabold text-ink">
                    Annual Mega Career Fair & Convocation 2026
                  </h3>
                  <span className="rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-2xs font-extrabold text-emerald-700 dark:text-emerald-300">
                    60+ Tech Employers On-Campus
                  </span>
                </div>
                <p className="text-xs text-muted">
                  Main Quaid-e-Azam Auditorium & D Block Incubation Center · On-the-spot interviews and graduate offer letters.
                </p>
              </div>

              <div className="rounded-2xl border border-line bg-panel p-3.5 text-center min-w-[150px] shadow-xs">
                <span className="text-2xs font-bold text-muted uppercase tracking-wider block">
                  Hiring Quota
                </span>
                <span className="font-mono font-black text-xl text-emerald-600">
                  250+ Positions
                </span>
                <span className="text-[10px] text-muted block mt-0.5">Across CS, SE & EE Grads</span>
              </div>
            </div>
          </div>

          {/* Companies Grid */}
          <div className="grid gap-6 md:grid-cols-2">
            {CAREER_FAIR_COMPANIES.map((company) => (
              <div
                key={company.id}
                className="rounded-3xl border border-line bg-panel p-6 shadow-2xs space-y-4 flex flex-col justify-between hover:border-emerald-500/60 transition group"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="rounded-md bg-emerald-500/10 px-2 py-0.5 text-2xs font-extrabold text-emerald-600">
                        {company.sector}
                      </span>
                      <h4 className="font-extrabold text-base text-ink mt-1 group-hover:text-emerald-600 transition">
                        {company.companyName}
                      </h4>
                      <p className="text-xs text-muted flex items-center gap-1.5 mt-0.5">
                        <MapPin size={12} className="text-brand-500" />
                        <span>{company.boothNumber}</span>
                      </p>
                    </div>

                    <span className="rounded-full bg-surface border border-line px-2.5 py-1 text-2xs font-bold text-muted">
                      {company.hiringTarget}
                    </span>
                  </div>

                  <div className="rounded-2xl border border-line/60 bg-surface/50 p-3 space-y-1.5 text-xs">
                    <span className="text-2xs font-bold text-muted uppercase tracking-wider block">
                      Open Job Profiles:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {company.openRoles.map((role, idx) => (
                        <span key={idx} className="rounded-md bg-panel border border-line px-2 py-0.5 text-2xs font-semibold text-ink">
                          ✓ {role}
                        </span>
                      ))}
                    </div>

                    <div className="pt-2 border-t border-line/40 text-2xs text-muted flex items-center justify-between">
                      <span>Interview Hours:</span>
                      <span className="font-semibold text-ink">{company.interviewSlots}</span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => setInterviewBookingCompany(company)}
                  className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 py-2.5 text-xs font-bold text-white hover:bg-emerald-700 transition shadow-xs"
                >
                  <Briefcase size={14} />
                  <span>Book Walk-in Interview FastPass</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ================= MODAL: TECH GALA REGISTRATION ================= */}
      {registeredComp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
          <div className="w-full max-w-md rounded-3xl border border-line bg-panel p-6 shadow-2xl space-y-5 animate-in zoom-in-95 duration-200">
            <div className="flex items-start justify-between">
              <div>
                <span className="rounded-full bg-indigo-500/10 px-2.5 py-0.5 text-2xs font-extrabold text-indigo-600 uppercase">
                  Tech Competition Entry
                </span>
                <h3 className="font-extrabold text-base text-ink mt-1">
                  {registeredComp.title}
                </h3>
              </div>
              <button onClick={() => setRegisteredComp(null)} className="rounded-xl p-1 text-muted hover:text-ink">
                <X size={16} />
              </button>
            </div>

            {regSuccess ? (
              <div className="rounded-2xl border border-emerald-500/40 bg-emerald-500/10 p-5 text-center space-y-2">
                <CheckCircle2 size={24} className="mx-auto text-emerald-600" />
                <h4 className="font-bold text-sm text-ink">Team Registered Successfully!</h4>
                <p className="text-2xs text-muted">
                  Team "{teamNameInput}" has been confirmed. Software Lab workstations and credentials dispatched to student emails.
                </p>
                <button
                  onClick={() => setRegisteredComp(null)}
                  className="rounded-xl bg-emerald-600 px-5 py-2 text-xs font-bold text-white hover:bg-emerald-700 mt-2"
                >
                  Close Pass
                </button>
              </div>
            ) : (
              <div className="space-y-4 text-xs">
                <div>
                  <label className="block font-bold text-ink mb-1">Team Name</label>
                  <input
                    type="text"
                    placeholder="e.g. ByteCraft AI, Algorithmic Aces..."
                    value={teamNameInput}
                    onChange={(e) => setTeamNameInput(e.target.value)}
                    className="w-full rounded-xl border border-line bg-surface p-2.5 text-xs text-ink placeholder:text-muted focus:outline-hidden focus:ring-2 focus:ring-indigo-500"
                  />
                </div>

                <div className="rounded-xl border border-line bg-surface/60 p-3 text-2xs text-muted space-y-1">
                  <p className="font-bold text-ink">Competition Specs:</p>
                  <p>• Venue: {registeredComp.venue}</p>
                  <p>• Prize Pool: {registeredComp.prizePool}</p>
                  <p>• Bring student ID card for lab workstation allocation.</p>
                </div>

                <div className="flex items-center justify-end gap-2 pt-2 border-t border-line/60">
                  <button
                    onClick={() => setRegisteredComp(null)}
                    className="rounded-xl border border-line bg-surface px-4 py-2 text-xs font-bold text-muted hover:text-ink"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => setRegSuccess(true)}
                    disabled={!teamNameInput.trim()}
                    className="rounded-xl bg-indigo-600 px-5 py-2 text-xs font-bold text-white hover:bg-indigo-700 disabled:opacity-50"
                  >
                    Confirm Registration
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ================= MODAL: CAREER INTERVIEW FASTPASS ================= */}
      {interviewBookingCompany && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-xs p-4 animate-in fade-in duration-200">
          <div className="w-full max-w-sm rounded-3xl border border-line bg-panel p-6 shadow-2xl text-center space-y-5 animate-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between text-left">
              <div>
                <h4 className="font-extrabold text-sm text-ink">{interviewBookingCompany.companyName}</h4>
                <p className="text-2xs text-muted">{interviewBookingCompany.boothNumber}</p>
              </div>
              <button onClick={() => setInterviewBookingCompany(null)} className="rounded-xl p-1 text-muted hover:text-ink">
                <X size={16} />
              </button>
            </div>

            <div className="rounded-2xl border-2 border-dashed border-emerald-500/40 bg-surface/80 p-5 space-y-2">
              <span className="text-2xs font-extrabold text-muted uppercase">FastPass Reserved</span>
              <div className="font-mono font-black text-2xl text-emerald-600">
                SLOT #INT-48
              </div>
              <p className="text-2xs text-muted">
                Reporting Time: <strong className="text-ink">11:30 AM (Auditorium Booth #01)</strong>
              </p>
            </div>

            <p className="text-2xs text-muted">
              Carry 2 printed copies of your CV and final transcript.
            </p>

            <button
              onClick={() => setInterviewBookingCompany(null)}
              className="w-full rounded-xl bg-emerald-600 py-2.5 text-xs font-bold text-white hover:bg-emerald-700 transition"
            >
              Add to Calendar & Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
