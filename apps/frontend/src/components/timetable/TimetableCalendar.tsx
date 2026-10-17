import { useState } from "react";

type TimetableOccurrence = {
  id: string;
  title: string;
  startsAt: string;
  endsAt: string;
  roomLabel?: string;
};

function dateKey(date: Date): string {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}

/** Accessible month calendar based on actual scheduled occurrences, never generated guesses. */
export function TimetableCalendar({ occurrences }: { occurrences: TimetableOccurrence[] }) {
  const [month, setMonth] = useState(() => {
    const first = occurrences.find((item) => Number.isFinite(Date.parse(item.startsAt)));
    const date = first ? new Date(first.startsAt) : new Date();
    return new Date(date.getFullYear(), date.getMonth(), 1);
  });
  const start = new Date(month.getFullYear(), month.getMonth(), 1);
  const cellCount = Math.ceil((start.getDay() + new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate()) / 7) * 7;
  const entries = new Map<string, TimetableOccurrence[]>();
  for (const entry of occurrences) {
    const parsed = new Date(entry.startsAt);
    if (Number.isNaN(parsed.getTime())) continue;
    const key = dateKey(parsed);
    entries.set(key, [...(entries.get(key) ?? []), entry]);
  }
  return (
    <section aria-label="Timetable calendar" className="rounded-xl border border-line bg-panel p-3">
      <div className="mb-4 flex items-center justify-between gap-3">
        <button type="button" className="rounded-lg border border-line px-3 py-2" aria-label="Previous month"
          onClick={() => setMonth(new Date(month.getFullYear(), month.getMonth() - 1, 1))}>Previous</button>
        <h2 className="font-bold" aria-live="polite">{month.toLocaleDateString([], { month: "long", year: "numeric" })}</h2>
        <button type="button" className="rounded-lg border border-line px-3 py-2" aria-label="Next month"
          onClick={() => setMonth(new Date(month.getFullYear(), month.getMonth() + 1, 1))}>Next</button>
      </div>
      <div className="grid grid-cols-7 gap-1 text-center text-xs font-semibold text-muted" aria-hidden="true">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => <span key={day}>{day}</span>)}
      </div>
      <div className="mt-2 grid grid-cols-7 gap-1">
        {Array.from({ length: cellCount }, (_, index) => {
          const date = new Date(month.getFullYear(), month.getMonth(), index - start.getDay() + 1);
          const key = dateKey(date);
          const visible = date.getMonth() === month.getMonth();
          return <div key={key} aria-label={date.toDateString()}
            className={`min-h-20 rounded border border-line p-1 text-xs ${visible ? "bg-surface" : "bg-panel opacity-50"}`}>
            <span className="block text-right font-bold">{date.getDate()}</span>
            {(entries.get(key) ?? []).map((item) => <div key={`${item.id}:${item.startsAt}`}
              title={`${item.title} – ${item.roomLabel ?? "Room TBA"}`}
              className="my-1 truncate rounded bg-brand-50 px-1 py-1 text-brand-700">
              {new Date(item.startsAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} {item.title}
            </div>)}
          </div>;
        })}
      </div>
    </section>
  );
}
