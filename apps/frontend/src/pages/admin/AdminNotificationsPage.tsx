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
  useNotificationCampaigns,
  useNotificationTemplates,
  useSections
} from "../../features/admin/hooks";

type TargetKind = "ROLE" | "SECTION";
type RoleTarget = "student" | "teacher" | "admin";

export function AdminNotificationsPage() {
  const templates = useNotificationTemplates();
  const campaigns = useNotificationCampaigns();
  const sections = useSections();
  const toast = useToast();

  const createTemplate = useAdminMutation(
    api.createNotificationTemplate,
    adminKeys.templates
  );
  const createCampaign = useAdminMutation(
    api.createNotificationCampaign,
    adminKeys.campaigns
  );

  const [templateForm, setTemplateForm] = useState({
    code: "",
    title_template: "",
    body_template: "",
    category: "general",
    enabled: true,
    email: false
  });

  const [campaignForm, setCampaignForm] = useState({
    targetKind: "ROLE" as TargetKind,
    role: "student" as RoleTarget,
    sectionId: "",
    templateCode: "",
    title: "",
    body: "",
    category: "general",
    priority: "NORMAL" as "LOW" | "NORMAL" | "HIGH" | "URGENT",
    email: false
  });

  if (templates.isLoading || campaigns.isLoading || sections.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading notification administration…" />
      </div>
    );
  }

  if (templates.error || campaigns.error || sections.error) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Admin" title="Announcements & notifications" />
        <InlineError message="Notification administration data could not be loaded." />
      </div>
    );
  }

  const submitTemplate = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await createTemplate.mutateAsync({
        code: templateForm.code,
        title_template: templateForm.title_template,
        body_template: templateForm.body_template,
        default_channels: templateForm.email
          ? ["IN_APP", "EMAIL"]
          : ["IN_APP"],
        category: templateForm.category,
        enabled: templateForm.enabled
      });
      setTemplateForm({
        code: "",
        title_template: "",
        body_template: "",
        category: "general",
        enabled: true,
        email: false
      });
      toast.push("Notification template created.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Could not create template.",
        "error"
      );
    }
  };

  const submitCampaign = async (event: FormEvent) => {
    event.preventDefault();

    const hasTemplate = Boolean(campaignForm.templateCode);
    if (!hasTemplate && (!campaignForm.title.trim() || !campaignForm.body.trim())) {
      toast.push("Choose a template or provide both title and body.", "error");
      return;
    }

    if (campaignForm.targetKind === "SECTION" && !campaignForm.sectionId) {
      toast.push("Choose a target section.", "error");
      return;
    }

    try {
      await createCampaign.mutateAsync({
        target:
          campaignForm.targetKind === "ROLE"
            ? {
                kind: "ROLE",
                role: campaignForm.role
              }
            : {
                kind: "SECTION",
                section_id: campaignForm.sectionId
              },
        template_code: campaignForm.templateCode || undefined,
        title: hasTemplate ? undefined : campaignForm.title.trim(),
        body: hasTemplate ? undefined : campaignForm.body.trim(),
        category: campaignForm.category,
        priority: campaignForm.priority,
        channels: campaignForm.email
          ? ["IN_APP", "EMAIL"]
          : ["IN_APP"],
        data: {}
      });
      setCampaignForm((current) => ({
        ...current,
        title: "",
        body: ""
      }));
      toast.push("Notification campaign created and dispatched.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Could not create campaign.",
        "error"
      );
    }
  };

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Admin"
        title="Announcements & notifications"
        description="Manage reusable notification templates and send role- or section-targeted campaigns through the existing delivery pipeline."
      />

      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="Create template">
          <form className="space-y-4" onSubmit={(event) => void submitTemplate(event)}>
            <Input
              label="Template code"
              hint="Letters, numbers, dot, underscore, and dash."
              value={templateForm.code}
              onChange={(e) =>
                setTemplateForm((f) => ({ ...f, code: e.target.value }))
              }
            />
            <Input
              label="Title template"
              value={templateForm.title_template}
              onChange={(e) =>
                setTemplateForm((f) => ({
                  ...f,
                  title_template: e.target.value
                }))
              }
            />
            <label className="block text-sm font-medium">
              Body template
              <textarea
                className="mt-2 min-h-32 w-full rounded-xl border border-line px-3 py-2"
                value={templateForm.body_template}
                onChange={(e) =>
                  setTemplateForm((f) => ({
                    ...f,
                    body_template: e.target.value
                  }))
                }
              />
            </label>
            <Input
              label="Category"
              value={templateForm.category}
              onChange={(e) =>
                setTemplateForm((f) => ({ ...f, category: e.target.value }))
              }
            />
            <label className="flex items-center gap-3 rounded-xl border border-line p-3 text-sm">
              <input
                type="checkbox"
                checked={templateForm.email}
                onChange={(e) =>
                  setTemplateForm((f) => ({ ...f, email: e.target.checked }))
                }
              />
              Include Email as a default channel
            </label>
            <label className="flex items-center gap-3 rounded-xl border border-line p-3 text-sm">
              <input
                type="checkbox"
                checked={templateForm.enabled}
                onChange={(e) =>
                  setTemplateForm((f) => ({ ...f, enabled: e.target.checked }))
                }
              />
              Template enabled
            </label>
            <Button type="submit" disabled={createTemplate.isPending}>
              Create template
            </Button>
          </form>
        </Card>

        <Card title="Send campaign">
          <form className="space-y-4" onSubmit={(event) => void submitCampaign(event)}>
            <label className="block text-sm font-medium">
              Target kind
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={campaignForm.targetKind}
                onChange={(e) =>
                  setCampaignForm((f) => ({
                    ...f,
                    targetKind: e.target.value as TargetKind
                  }))
                }
              >
                <option value="ROLE">Role</option>
                <option value="SECTION">Section</option>
              </select>
            </label>

            {campaignForm.targetKind === "ROLE" ? (
              <label className="block text-sm font-medium">
                Role
                <select
                  className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                  value={campaignForm.role}
                  onChange={(e) =>
                    setCampaignForm((f) => ({
                      ...f,
                      role: e.target.value as RoleTarget
                    }))
                  }
                >
                  <option value="student">Students</option>
                  <option value="teacher">Teachers</option>
                  <option value="admin">Admins</option>
                </select>
              </label>
            ) : (
              <label className="block text-sm font-medium">
                Section
                <select
                  className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                  value={campaignForm.sectionId}
                  onChange={(e) =>
                    setCampaignForm((f) => ({
                      ...f,
                      sectionId: e.target.value
                    }))
                  }
                >
                  <option value="">Select section</option>
                  {(sections.data ?? []).map((section) => (
                    <option key={section.id} value={section.id}>
                      {section.name}
                    </option>
                  ))}
                </select>
              </label>
            )}

            <label className="block text-sm font-medium">
              Template (optional)
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={campaignForm.templateCode}
                onChange={(e) =>
                  setCampaignForm((f) => ({
                    ...f,
                    templateCode: e.target.value
                  }))
                }
              >
                <option value="">Write title/body manually</option>
                {(templates.data ?? [])
                  .filter((template) => template.enabled)
                  .map((template) => (
                    <option key={template.id} value={template.code}>
                      {template.code}
                    </option>
                  ))}
              </select>
            </label>

            {!campaignForm.templateCode ? (
              <>
                <Input
                  label="Title"
                  value={campaignForm.title}
                  onChange={(e) =>
                    setCampaignForm((f) => ({ ...f, title: e.target.value }))
                  }
                />
                <label className="block text-sm font-medium">
                  Message
                  <textarea
                    className="mt-2 min-h-32 w-full rounded-xl border border-line px-3 py-2"
                    value={campaignForm.body}
                    onChange={(e) =>
                      setCampaignForm((f) => ({ ...f, body: e.target.value }))
                    }
                  />
                </label>
              </>
            ) : null}

            <div className="grid gap-3 sm:grid-cols-2">
              <Input
                label="Category"
                value={campaignForm.category}
                onChange={(e) =>
                  setCampaignForm((f) => ({ ...f, category: e.target.value }))
                }
              />
              <label className="block text-sm font-medium">
                Priority
                <select
                  className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                  value={campaignForm.priority}
                  onChange={(e) =>
                    setCampaignForm((f) => ({
                      ...f,
                      priority: e.target.value as typeof campaignForm.priority
                    }))
                  }
                >
                  <option value="LOW">Low</option>
                  <option value="NORMAL">Normal</option>
                  <option value="HIGH">High</option>
                  <option value="URGENT">Urgent</option>
                </select>
              </label>
            </div>

            <label className="flex items-center gap-3 rounded-xl border border-line p-3 text-sm">
              <input
                type="checkbox"
                checked={campaignForm.email}
                onChange={(e) =>
                  setCampaignForm((f) => ({ ...f, email: e.target.checked }))
                }
              />
              Request Email delivery in addition to in-app delivery
            </label>

            <Button type="submit" disabled={createCampaign.isPending}>
              {createCampaign.isPending ? "Dispatching…" : "Send campaign"}
            </Button>
          </form>
        </Card>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-2">
        <Card title="Templates">
          <div className="space-y-3">
            {(templates.data ?? []).map((template) => (
              <div key={template.id} className="rounded-xl border border-line p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold">{template.code}</p>
                    <p className="mt-1 text-sm">{template.titleTemplate}</p>
                    <p className="mt-2 text-xs text-muted">
                      {template.category} · {template.defaultChannels.join(", ")}
                    </p>
                  </div>
                  <Badge>{template.enabled ? "ENABLED" : "DISABLED"}</Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card title="Recent campaigns">
          <div className="space-y-3">
            {(campaigns.data ?? []).map((item) => (
              <div key={item.id} className="rounded-xl border border-line p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold">{item.title ?? item.category}</p>
                    <p className="mt-1 text-xs text-muted">
                      {item.targetKind} · {item.recipientCount} recipients ·{" "}
                      {item.channels.join(", ")}
                    </p>
                    <p className="mt-1 text-xs text-muted">
                      {new Date(item.createdAt).toLocaleString()}
                    </p>
                  </div>
                  <Badge>{item.status}</Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
