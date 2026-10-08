import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { useTimetable } from "../../features/student/hooks";

function dayKey(value: string) {
  const date = new Date(value);
  return Number.isFinite(date.getTime())
    ? date.toLocaleDateString([], {
        weekday: "long",
        year: "numeric",
        month: "short",
        day: "numeric"
      })
    : "Unscheduled";
}

export function StudentTimetablePage() {
  const timetable = useTimetable();

  if (timetable.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading timetable…" />
      </div>
    );
  }

  if (timetable.error) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Student" title="My timetable" />
        <InlineError message="Your timetable could not be loaded." />
      </div>
    );
  }

  const sorted = [...(timetable.data ?? [])].sort(
    (a, b) => new Date(a.startsAt).getTime() - new Date(b.startsAt).getTime()
  );

  const groups = sorted.reduce<Record<string, typeof sorted>>((acc, item) => {
    const key = dayKey(item.startsAt);
    (acc[key] ??= []).push(item);
    return acc;
  }, {});

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Student"
        title="My timetable"
        description="Your current scheduled classes, rooms, and class times."
      />

      {Object.keys(groups).length ? (
        <div className="space-y-6">
          {Object.entries(groups).map(([day, items]) => (
            <Card key={day} title={day}>
              <div className="space-y-3">
                {items.map((item) => (
                  <div
                    key={item.id}
                    className="grid gap-2 rounded-xl border border-line bg-surface/50 p-4 sm:grid-cols-[8rem_minmax(0,1fr)_12rem]"
                  >
                    <div className="text-sm font-semibold text-brand-700">
                      {new Date(item.startsAt).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit"
                      })}
                      {" – "}
                      {new Date(item.endsAt).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit"
                      })}
                    </div>
                    <div>
                      <p className="font-semibold">{item.title}</p>
                      <p className="mt-1 text-xs text-muted">
                        Section: {item.sectionId ?? "—"}
                      </p>
                    </div>
                    <div className="text-sm text-muted">
                      {item.roomLabel ?? "Room TBA"}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <p className="text-sm text-muted">No timetable entries are currently available.</p>
        </Card>
      )}
    </div>
  );
}
