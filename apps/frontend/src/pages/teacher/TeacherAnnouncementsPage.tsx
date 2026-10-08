import { useState, type FormEvent } from "react";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { useToast } from "../../components/ui/useToast";
import {
  useCreateTeacherAnnouncement,
  useTeacherAnnouncements,
  useTeacherSections
} from "../../features/teacher/hooks";

export function TeacherAnnouncementsPage() {
  const sections = useTeacherSections();
  const announcements = useTeacherAnnouncements();
  const create = useCreateTeacherAnnouncement();
  const toast = useToast();

  const [sectionId, setSectionId] = useState("");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [priority, setPriority] =
    useState<"LOW" | "NORMAL" | "HIGH" | "URGENT">("NORMAL");
  const [sendEmail, setSendEmail] = useState(false);

  if (sections.isLoading || announcements.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading announcements…" />
      </div>
    );
  }

  if (sections.error || announcements.error) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Teacher" title="Announcements" />
        <InlineError message="The announcement workspace could not be loaded." />
      </div>
    );
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault();

    if (!sectionId || !title.trim() || !body.trim()) {
      toast.push("Choose a section and provide title and message.", "error");
      return;
    }

    try {
      await create.mutateAsync({
        section_id: sectionId,
        title: title.trim(),
        body: body.trim(),
        category: "teacher_announcement",
        priority,
        channels: sendEmail ? ["IN_APP", "EMAIL"] : ["IN_APP"]
      });
      setTitle("");
      setBody("");
      toast.push("Announcement sent to the assigned section.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Announcement could not be sent.",
        "error"
      );
    }
  };

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Teacher"
        title="Announcements"
        description="Send section-scoped announcements only to classes assigned to you."
      />

      <div className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
        <Card title="New section announcement">
          <form className="space-y-4" onSubmit={(event) => void submit(event)}>
            <label className="block text-sm font-medium">
              Section
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={sectionId}
                onChange={(event) => setSectionId(event.target.value)}
              >
                <option value="">Select assigned section</option>
                {(sections.data ?? []).map((section) => (
                  <option key={section.id} value={section.id}>
                    {section.courseCode ? `${section.courseCode} · ` : ""}
                    {section.name}
                  </option>
                ))}
              </select>
            </label>

            <Input
              label="Title"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
            />

            <label className="block text-sm font-medium">
              Message
              <textarea
                className="mt-2 min-h-40 w-full rounded-xl border border-line px-3 py-2"
                value={body}
                onChange={(event) => setBody(event.target.value)}
              />
            </label>

            <label className="block text-sm font-medium">
              Priority
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={priority}
                onChange={(event) =>
                  setPriority(event.target.value as typeof priority)
                }
              >
                <option value="LOW">Low</option>
                <option value="NORMAL">Normal</option>
                <option value="HIGH">High</option>
                <option value="URGENT">Urgent</option>
              </select>
            </label>

            <label className="flex items-center gap-3 rounded-xl border border-line p-3 text-sm">
              <input
                type="checkbox"
                checked={sendEmail}
                onChange={(event) => setSendEmail(event.target.checked)}
              />
              Also request email delivery where recipients allow it
            </label>

            <Button type="submit" disabled={create.isPending}>
              {create.isPending ? "Sending…" : "Send announcement"}
            </Button>
          </form>
        </Card>

        <Card title="My recent announcements">
          {announcements.data?.length ? (
            <div className="space-y-3">
              {announcements.data.map((announcement) => (
                <article
                  key={announcement.id}
                  className="rounded-xl border border-line p-4"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <h2 className="font-semibold">{announcement.title}</h2>
                      <p className="mt-2 text-sm leading-6 text-muted">
                        {announcement.body}
                      </p>
                    </div>
                    <Badge>{announcement.status}</Badge>
                  </div>
                  <p className="mt-3 text-xs text-muted">
                    {announcement.recipientCount} recipient
                    {announcement.recipientCount === 1 ? "" : "s"} ·{" "}
                    {announcement.channels.join(", ")} ·{" "}
                    {announcement.createdAt
                      ? new Date(announcement.createdAt).toLocaleString()
                      : ""}
                  </p>
                </article>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted">You have not sent any section announcements yet.</p>
          )}
        </Card>
      </div>
    </div>
  );
}
