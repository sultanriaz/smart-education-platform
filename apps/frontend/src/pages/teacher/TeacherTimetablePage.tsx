import { TimetableCalendar } from "../../components/timetable/TimetableCalendar";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { useTeacherTimetable } from "../../features/teacher/hooks";

export function TeacherTimetablePage() {
  const timetable = useTeacherTimetable();

  if (timetable.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading teaching timetable…" />
      </div>
    );
  }

  if (timetable.error) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Teacher" title="Teaching timetable" />
        <InlineError message="Your teaching timetable could not be loaded." />
      </div>
    );
  }

  const sorted = [...(timetable.data ?? [])].sort(
    (a, b) => new Date(a.startsAt).getTime() - new Date(b.startsAt).getTime()
  );

  const groups = sorted.reduce<Record<string, typeof sorted>>((acc, item) => {
    const key = new Date(item.startsAt).toLocaleDateString([], {
      weekday: "long",
      year: "numeric",
      month: "short",
      day: "numeric"
    });
    (acc[key] ??= []).push(item);
    return acc;
  }, {});

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Teacher"
        title="Teaching timetable"
        description="Your assigned class occurrences for the current two-week window."
      />

      <TimetableCalendar occurrences={sorted} />

      {Object.entries(groups).length ? (
        <div className="space-y-6">
          {Object.entries(groups).map(([day, items]) => (
            <Card key={day} title={day}>
              <div className="space-y-3">
                {items.map((item) => (
                  <div
                    key={item.id}
                    className="grid gap-2 rounded-xl border border-line bg-surface/50 p-4 sm:grid-cols-[9rem_minmax(0,1fr)_12rem]"
                  >
                    <div className="font-semibold text-brand-700">
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
                        Section {item.sectionId}
                      </p>
                    </div>
                    <div className="text-sm text-muted">
                      {item.roomId ?? "Room TBA"}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <p className="text-sm text-muted">No teaching occurrences are available in this window.</p>
        </Card>
      )}
    </div>
  );
}
