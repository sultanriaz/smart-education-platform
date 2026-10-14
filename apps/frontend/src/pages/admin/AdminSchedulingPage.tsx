import { useState, type FormEvent } from "react";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { useToast } from "../../components/ui/useToast";
import * as api from "../../features/admin/admin-api";
import {
  adminKeys,
  useAdminMutation,
  useSchedules,
  useSections,
  useTeacherProfiles
} from "../../features/admin/hooks";

const weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

export function AdminSchedulingPage() {
  const schedules = useSchedules();
  const sections = useSections();
  const teachers = useTeacherProfiles();
  const toast = useToast();

  const create = useAdminMutation(api.createSchedule, adminKeys.schedules);
  const publish = useAdminMutation(api.publishSchedule, adminKeys.schedules);
  const update = useAdminMutation(
    ({ id, input }: { id: string; input: Parameters<typeof api.updateSchedule>[1] }) =>
      api.updateSchedule(id, input), adminKeys.schedules
  );
  const [editing, setEditing] = useState<string | null>(null);
  const [editStart, setEditStart] = useState("09:00");
  const [editEnd, setEditEnd] = useState("10:30");
  const [historyId, setHistoryId] = useState<string | null>(null);
  const [historyText, setHistoryText] = useState("");

  const cancel = useAdminMutation(
    ({ id, reason }: { id: string; reason?: string }) => api.cancelSchedule(id, reason),
    adminKeys.schedules
  );
  const override = useAdminMutation(
    ({
      id,
      input
    }: {
      id: string;
      input: Parameters<typeof api.createScheduleOverride>[1];
    }) => api.createScheduleOverride(id, input),
    adminKeys.schedules
  );

  const [form, setForm] = useState({
    section_id: "",
    teacher_user_id: "",
    room_id: "",
    weekday: 0,
    starts_at: "09:00",
    ends_at: "10:30",
    effective_from: "",
    effective_to: "",
    timezone_name: "Asia/Karachi",
    publish: false
  });

  const [cancelReasons, setCancelReasons] = useState<Record<string, string>>({});
  const [overrideScheduleId, setOverrideScheduleId] = useState("");
  const [overrideForm, setOverrideForm] = useState({
    occurrence_date: "",
    kind: "CANCELLED" as "CANCELLED" | "RESCHEDULED",
    starts_at: "",
    ends_at: "",
    room_id: "",
    reason: ""
  });

  if (schedules.isLoading || sections.isLoading || teachers.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading scheduling administration…" />
      </div>
    );
  }

  if (schedules.error || sections.error || teachers.error) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Admin" title="Scheduling" />
        <InlineError message="Scheduling administration data could not be loaded." />
      </div>
    );
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await create.mutateAsync({
        section_id: form.section_id,
        teacher_user_id: form.teacher_user_id || undefined,
        room_id: form.room_id || undefined,
        weekday: form.weekday,
        starts_at: form.starts_at,
        ends_at: form.ends_at,
        effective_from: form.effective_from,
        effective_to: form.effective_to,
        timezone_name: form.timezone_name || undefined,
        publish: form.publish
      });
      toast.push("Schedule created.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Could not create schedule.", "error");
    }
  };

  const cancelOne = async (id: string) => {
    try {
      await cancel.mutateAsync({ id, reason: cancelReasons[id]?.trim() || undefined });
      toast.push("Schedule cancelled.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Could not cancel schedule.", "error");
    }
  };

  const submitOverride = async (event: FormEvent) => {
    event.preventDefault();
    if (!overrideScheduleId || !overrideForm.occurrence_date) {
      toast.push("Select a schedule and occurrence date.", "error");
      return;
    }

    try {
      await override.mutateAsync({
        id: overrideScheduleId,
        input: {
          occurrence_date: overrideForm.occurrence_date,
          kind: overrideForm.kind,
          starts_at:
            overrideForm.kind === "RESCHEDULED" ? overrideForm.starts_at : undefined,
          ends_at:
            overrideForm.kind === "RESCHEDULED" ? overrideForm.ends_at : undefined,
          room_id:
            overrideForm.kind === "RESCHEDULED" && overrideForm.room_id
              ? overrideForm.room_id
              : undefined,
          reason: overrideForm.reason || undefined
        }
      });
      toast.push("Schedule override created.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Override failed.", "error");
    }
  };

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Admin"
        title="Scheduling"
        description="Create recurring schedules, resolve conflicts through Scheduling Service rules, cancel schedules, and apply occurrence overrides."
      />

      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="Create recurring schedule">
          <form className="space-y-4" onSubmit={(event) => void submit(event)}>
            <label className="block text-sm font-medium">
              Section
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={form.section_id}
                onChange={(e) => setForm((f) => ({ ...f, section_id: e.target.value }))}
              >
                <option value="">Select section</option>
                {(sections.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>{item.name}</option>
                ))}
              </select>
            </label>

            <label className="block text-sm font-medium">
              Teacher
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={form.teacher_user_id}
                onChange={(e) =>
                  setForm((f) => ({ ...f, teacher_user_id: e.target.value }))
                }
              >
                <option value="">Let Academic contract resolve Teacher if supported</option>
                {(teachers.data ?? []).map((item) => (
                  <option key={item.id} value={item.identityUserId}>
                    {item.employeeId} · {item.identityUserId}
                  </option>
                ))}
              </select>
            </label>

            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={form.publish} onChange={event => setForm(current => ({ ...current, publish: event.target.checked }))} />
              Publish immediately (leave unchecked to save a private draft)
            </label>

            <Input
              label="Room UUID"
              hint="Leave blank when the class has no room assignment."
              value={form.room_id}
              onChange={(e) => setForm((f) => ({ ...f, room_id: e.target.value }))}
            />

            <label className="block text-sm font-medium">
              Weekday
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={form.weekday}
                onChange={(e) =>
                  setForm((f) => ({ ...f, weekday: Number(e.target.value) }))
                }
              >
                {weekdays.map((day, index) => (
                  <option key={day} value={index}>{day}</option>
                ))}
              </select>
            </label>

            <div className="grid gap-3 sm:grid-cols-2">
              <Input
                label="Starts"
                type="time"
                value={form.starts_at}
                onChange={(e) => setForm((f) => ({ ...f, starts_at: e.target.value }))}
              />
              <Input
                label="Ends"
                type="time"
                value={form.ends_at}
                onChange={(e) => setForm((f) => ({ ...f, ends_at: e.target.value }))}
              />
              <Input
                label="Effective from"
                type="date"
                value={form.effective_from}
                onChange={(e) => setForm((f) => ({ ...f, effective_from: e.target.value }))}
              />
              <Input
                label="Effective to"
                type="date"
                value={form.effective_to}
                onChange={(e) => setForm((f) => ({ ...f, effective_to: e.target.value }))}
              />
            </div>

            <Input
              label="Timezone"
              value={form.timezone_name}
              onChange={(e) => setForm((f) => ({ ...f, timezone_name: e.target.value }))}
            />

            <Button type="submit" disabled={create.isPending}>
              {create.isPending ? "Creating…" : "Create schedule"}
            </Button>
          </form>
        </Card>

        <Card title="Occurrence override">
          <form className="space-y-4" onSubmit={(event) => void submitOverride(event)}>
            <label className="block text-sm font-medium">
              Schedule
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={overrideScheduleId}
                onChange={(e) => setOverrideScheduleId(e.target.value)}
              >
                <option value="">Select schedule</option>
                {(schedules.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    Section {item.sectionId} · {weekdays[item.weekday]} · {item.startsAt}
                  </option>
                ))}
              </select>
            </label>

            <Input
              label="Occurrence date"
              type="date"
              value={overrideForm.occurrence_date}
              onChange={(e) =>
                setOverrideForm((f) => ({ ...f, occurrence_date: e.target.value }))
              }
            />

            <label className="block text-sm font-medium">
              Override kind
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={overrideForm.kind}
                onChange={(e) =>
                  setOverrideForm((f) => ({
                    ...f,
                    kind: e.target.value as "CANCELLED" | "RESCHEDULED"
                  }))
                }
              >
                <option value="CANCELLED">Cancel occurrence</option>
                <option value="RESCHEDULED">Reschedule occurrence</option>
              </select>
            </label>

            {overrideForm.kind === "RESCHEDULED" ? (
              <div className="grid gap-3 sm:grid-cols-2">
                <Input
                  label="New start"
                  type="time"
                  value={overrideForm.starts_at}
                  onChange={(e) =>
                    setOverrideForm((f) => ({ ...f, starts_at: e.target.value }))
                  }
                />
                <Input
                  label="New end"
                  type="time"
                  value={overrideForm.ends_at}
                  onChange={(e) =>
                    setOverrideForm((f) => ({ ...f, ends_at: e.target.value }))
                  }
                />
                <Input
                  label="New room UUID"
                  value={overrideForm.room_id}
                  onChange={(e) =>
                    setOverrideForm((f) => ({ ...f, room_id: e.target.value }))
                  }
                />
              </div>
            ) : null}

            <Input
              label="Reason"
              value={overrideForm.reason}
              onChange={(e) =>
                setOverrideForm((f) => ({ ...f, reason: e.target.value }))
              }
            />

            <Button type="submit" disabled={override.isPending}>
              Create override
            </Button>
          </form>
        </Card>
      </div>

      <Card className="mt-6" title="Schedules">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[1050px] text-left text-sm">
            <thead>
              <tr className="border-b border-line text-xs uppercase tracking-wide text-muted">
                <th className="px-2 py-3">Section</th>
                <th className="px-2 py-3">Teacher</th>
                <th className="px-2 py-3">Day/time</th>
                <th className="px-2 py-3">Room</th>
                <th className="px-2 py-3">Effective</th>
                <th className="px-2 py-3">Status</th>
                <th className="px-2 py-3">Actions / history</th>
              </tr>
            </thead>
            <tbody>
              {(schedules.data ?? []).map((item) => (
                <tr key={item.id} className="border-b border-line/70">
                  <td className="px-2 py-3">{item.sectionId}</td>
                  <td className="px-2 py-3">{item.teacherUserId}</td>
                  <td className="px-2 py-3">
                    {weekdays[item.weekday]} · {item.startsAt}–{item.endsAt}
                  </td>
                  <td className="px-2 py-3">{item.roomId ?? "—"}</td>
                  <td className="px-2 py-3">
                    {item.effectiveFrom} → {item.effectiveTo}
                  </td>
                  <td className="px-2 py-3">
                    <Badge>{item.status}</Badge>
                  </td>
                  <td className="px-2 py-3">
                    <div className="flex flex-wrap gap-2 mb-2">
                      {item.status === "DRAFT" && <Button disabled={publish.isPending} onClick={() => void publish.mutateAsync(item.id).then(() => toast.push("Timetable published.", "success")).catch(error => toast.push(error instanceof Error ? error.message : "Publish failed.", "error"))}>Publish</Button>}
                      {item.status !== "CANCELLED" && <Button variant="secondary" onClick={() => { setEditing(item.id); setEditStart(item.startsAt.slice(0,5)); setEditEnd(item.endsAt.slice(0,5)); }}>Edit time</Button>}
                      <Button variant="ghost" onClick={() => void api.getScheduleHistory(item.id).then(history => { setHistoryId(item.id); setHistoryText(JSON.stringify(history, null, 2)); }).catch(error => toast.push(error instanceof Error ? error.message : "History failed.", "error"))}>History</Button>
                    </div>
                    {editing === item.id && <div className="space-y-2 mb-2">
                      <Input label="Start time" type="time" value={editStart} onChange={e => setEditStart(e.target.value)} />
                      <Input label="End time" type="time" value={editEnd} onChange={e => setEditEnd(e.target.value)} />
                      <Button disabled={update.isPending} onClick={() => void update.mutateAsync({ id: item.id, input: { starts_at: editStart, ends_at: editEnd } }).then(() => { setEditing(null); toast.push("Timetable updated.", "success"); }).catch(error => toast.push(error instanceof Error ? error.message : "Update failed.", "error"))}>Save</Button>
                      <Button variant="ghost" onClick={() => setEditing(null)}>Close</Button>
                    </div>}
                    {historyId === item.id && <div className="space-y-2 mb-2"><pre className="max-w-sm overflow-auto whitespace-pre-wrap text-xs" aria-label="Schedule change history">{historyText}</pre><Button variant="ghost" onClick={() => setHistoryId(null)}>Close history</Button></div>}
                    {item.status !== "CANCELLED" ? (
                      <div className="flex gap-2">
                        <input
                          className="w-44 rounded-lg border border-line px-2 py-2 text-xs"
                          placeholder="Reason"
                          value={cancelReasons[item.id] ?? ""}
                          onChange={(e) =>
                            setCancelReasons((current) => ({
                              ...current,
                              [item.id]: e.target.value
                            }))
                          }
                        />
                        <Button
                          variant="secondary"
                          onClick={() => void cancelOne(item.id)}
                        >
                          Cancel
                        </Button>
                      </div>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
