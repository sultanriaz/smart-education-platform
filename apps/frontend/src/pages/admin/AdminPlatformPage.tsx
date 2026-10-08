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
  useAuditEvents,
  useFeatureFlags,
  usePlatformJobs,
  usePlatformServices,
  usePlatformSettings,
  useSupportTickets
} from "../../features/admin/hooks";
import type { ServiceHealth } from "../../features/admin/types";

function parseObject(value: string): Record<string, unknown> {
  const parsed = JSON.parse(value);
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error("JSON value must be an object.");
  }
  return parsed as Record<string, unknown>;
}

export function AdminPlatformPage() {
  const services = usePlatformServices();
  const settings = usePlatformSettings();
  const features = useFeatureFlags();
  const jobs = usePlatformJobs();
  const tickets = useSupportTickets();
  const audits = useAuditEvents();
  const toast = useToast();

  const upsertService = useAdminMutation(
    ({
      name,
      input
    }: {
      name: string;
      input: Parameters<typeof api.upsertPlatformService>[1];
    }) => api.upsertPlatformService(name, input),
    adminKeys.services
  );
  const upsertSetting = useAdminMutation(
    ({
      key,
      input
    }: {
      key: string;
      input: Parameters<typeof api.upsertPlatformSetting>[1];
    }) => api.upsertPlatformSetting(key, input),
    adminKeys.settings
  );
  const upsertFeature = useAdminMutation(
    ({
      key,
      input
    }: {
      key: string;
      input: Parameters<typeof api.upsertFeatureFlag>[1];
    }) => api.upsertFeatureFlag(key, input),
    adminKeys.features
  );
  const createJob = useAdminMutation(api.createPlatformJob, adminKeys.jobs);
  const updateTicket = useAdminMutation(
    ({
      id,
      input
    }: {
      id: string;
      input: Parameters<typeof api.updateSupportTicket>[1];
    }) => api.updateSupportTicket(id, input),
    adminKeys.tickets
  );

  const [healthRows, setHealthRows] = useState<ServiceHealth[]>([]);

  const [serviceForm, setServiceForm] = useState({
    service_name: "",
    base_url: "",
    health_path: "/health",
    ready_path: "/ready",
    enabled: true,
    critical: false,
    timeout_seconds: 3
  });

  const [settingForm, setSettingForm] = useState({
    key: "",
    value: "{}",
    is_public: false,
    description: ""
  });

  const [featureForm, setFeatureForm] = useState({
    key: "",
    enabled: false,
    config: "{}",
    description: ""
  });

  const [jobForm, setJobForm] = useState({
    job_type: "HEALTH_SWEEP" as "IMPORT" | "EXPORT" | "HEALTH_SWEEP" | "REINDEX",
    target_service: "",
    resource_type: "",
    parameters: "{}"
  });

  const [ticketUpdates, setTicketUpdates] = useState<
    Record<string, { status: string; priority: string; assignedTo: string }>
  >({});

  const queries = [services, settings, features, jobs, tickets, audits];

  if (queries.some((query) => query.isLoading)) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading platform operations…" />
      </div>
    );
  }

  if (queries.some((query) => query.error)) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Admin" title="Platform operations" />
        <InlineError message="Platform operations data could not be loaded." />
      </div>
    );
  }

  const healthSweep = async () => {
    try {
      const rows = await api.runHealthSweep();
      setHealthRows(rows);
      toast.push("Service health sweep completed.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Health sweep failed.", "error");
    }
  };

  const saveService = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await upsertService.mutateAsync({
        name: serviceForm.service_name,
        input: serviceForm
      });
      toast.push("Service registry entry saved.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Service registry update failed.", "error");
    }
  };

  const saveSetting = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await upsertSetting.mutateAsync({
        key: settingForm.key,
        input: {
          value: parseObject(settingForm.value),
          is_public: settingForm.is_public,
          description: settingForm.description || undefined
        }
      });
      toast.push("Platform setting saved.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Setting update failed.", "error");
    }
  };

  const saveFeature = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await upsertFeature.mutateAsync({
        key: featureForm.key,
        input: {
          enabled: featureForm.enabled,
          config: parseObject(featureForm.config),
          description: featureForm.description || undefined
        }
      });
      toast.push("Feature flag saved.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Feature flag update failed.", "error");
    }
  };

  const submitJob = async (event: FormEvent) => {
    event.preventDefault();
    try {
      await createJob.mutateAsync({
        job_type: jobForm.job_type,
        target_service: jobForm.target_service || undefined,
        resource_type: jobForm.resource_type || undefined,
        parameters: parseObject(jobForm.parameters),
        payload: {}
      });
      toast.push("Platform job created.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Job creation failed.", "error");
    }
  };

  const updateOneTicket = async (id: string) => {
    const value = ticketUpdates[id];
    if (!value) return;
    try {
      await updateTicket.mutateAsync({
        id,
        input: {
          status: value.status || undefined,
          priority: value.priority || undefined,
          assigned_to_user_id: value.assignedTo || null
        }
      });
      toast.push("Support ticket updated.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Ticket update failed.", "error");
    }
  };

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Admin"
        title="Platform operations"
        description="Operate service registry and health checks, runtime settings, feature flags, support tickets, background jobs, and centralized audit events."
        actions={
          <Button onClick={() => void healthSweep()}>
            Run health sweep
          </Button>
        }
      />

      {healthRows.length ? (
        <Card className="mb-6" title="Latest health sweep">
          <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
            {healthRows.map((row) => (
              <div key={row.serviceName} className="rounded-xl border border-line p-3">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold">{row.serviceName}</p>
                  <Badge>{row.status}</Badge>
                </div>
                <p className="mt-2 text-xs text-muted">
                  health {row.healthOk ? "OK" : "FAIL"} · ready{" "}
                  {row.readyOk ? "OK" : "FAIL"} ·{" "}
                  {row.latencyMs != null ? `${row.latencyMs} ms` : "latency n/a"}
                </p>
                {row.detail ? (
                  <p className="mt-2 text-xs text-muted">{row.detail}</p>
                ) : null}
              </div>
            ))}
          </div>
        </Card>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="Service registry">
          <form className="space-y-4" onSubmit={(event) => void saveService(event)}>
            <Input
              label="Service name"
              value={serviceForm.service_name}
              onChange={(e) =>
                setServiceForm((f) => ({ ...f, service_name: e.target.value }))
              }
            />
            <Input
              label="Base URL"
              value={serviceForm.base_url}
              onChange={(e) =>
                setServiceForm((f) => ({ ...f, base_url: e.target.value }))
              }
            />
            <div className="grid gap-3 sm:grid-cols-2">
              <Input
                label="Health path"
                value={serviceForm.health_path}
                onChange={(e) =>
                  setServiceForm((f) => ({ ...f, health_path: e.target.value }))
                }
              />
              <Input
                label="Ready path"
                value={serviceForm.ready_path}
                onChange={(e) =>
                  setServiceForm((f) => ({ ...f, ready_path: e.target.value }))
                }
              />
            </div>
            <Input
              label="Timeout seconds"
              type="number"
              min={0.1}
              max={30}
              step={0.1}
              value={serviceForm.timeout_seconds}
              onChange={(e) =>
                setServiceForm((f) => ({
                  ...f,
                  timeout_seconds: Number(e.target.value) || 3
                }))
              }
            />
            <div className="flex gap-4">
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={serviceForm.enabled}
                  onChange={(e) =>
                    setServiceForm((f) => ({ ...f, enabled: e.target.checked }))
                  }
                />
                Enabled
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={serviceForm.critical}
                  onChange={(e) =>
                    setServiceForm((f) => ({ ...f, critical: e.target.checked }))
                  }
                />
                Critical
              </label>
            </div>
            <Button type="submit">Save service</Button>
          </form>

          <div className="mt-6 space-y-2">
            {(services.data ?? []).map((service) => (
              <button
                key={service.id}
                className="block w-full rounded-xl border border-line p-3 text-left hover:bg-surface"
                onClick={() =>
                  setServiceForm({
                    service_name: service.serviceName,
                    base_url: service.baseUrl,
                    health_path: service.healthPath,
                    ready_path: service.readyPath,
                    enabled: service.enabled,
                    critical: service.critical,
                    timeout_seconds: service.timeoutSeconds
                  })
                }
              >
                <span className="font-semibold">{service.serviceName}</span>
                <span className="ml-2 text-xs text-muted">{service.baseUrl}</span>
              </button>
            ))}
          </div>
        </Card>

        <Card title="Settings">
          <form className="space-y-4" onSubmit={(event) => void saveSetting(event)}>
            <Input
              label="Key"
              value={settingForm.key}
              onChange={(e) =>
                setSettingForm((f) => ({ ...f, key: e.target.value }))
              }
            />
            <label className="block text-sm font-medium">
              JSON value
              <textarea
                className="mt-2 min-h-28 w-full rounded-xl border border-line px-3 py-2 font-mono text-xs"
                value={settingForm.value}
                onChange={(e) =>
                  setSettingForm((f) => ({ ...f, value: e.target.value }))
                }
              />
            </label>
            <Input
              label="Description"
              value={settingForm.description}
              onChange={(e) =>
                setSettingForm((f) => ({ ...f, description: e.target.value }))
              }
            />
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={settingForm.is_public}
                onChange={(e) =>
                  setSettingForm((f) => ({ ...f, is_public: e.target.checked }))
                }
              />
              Expose as public authenticated setting
            </label>
            <Button type="submit">Save setting</Button>
          </form>

          <div className="mt-6 space-y-2">
            {(settings.data ?? []).map((item) => (
              <button
                key={item.key}
                className="block w-full rounded-xl border border-line p-3 text-left"
                onClick={() =>
                  setSettingForm({
                    key: item.key,
                    value: JSON.stringify(item.value, null, 2),
                    is_public: item.isPublic,
                    description: item.description ?? ""
                  })
                }
              >
                <span className="font-semibold">{item.key}</span>
                <span className="ml-2 text-xs text-muted">
                  {item.isPublic ? "public" : "private"}
                </span>
              </button>
            ))}
          </div>
        </Card>

        <Card title="Feature flags">
          <form className="space-y-4" onSubmit={(event) => void saveFeature(event)}>
            <Input
              label="Key"
              value={featureForm.key}
              onChange={(e) =>
                setFeatureForm((f) => ({ ...f, key: e.target.value }))
              }
            />
            <label className="block text-sm font-medium">
              JSON config
              <textarea
                className="mt-2 min-h-28 w-full rounded-xl border border-line px-3 py-2 font-mono text-xs"
                value={featureForm.config}
                onChange={(e) =>
                  setFeatureForm((f) => ({ ...f, config: e.target.value }))
                }
              />
            </label>
            <Input
              label="Description"
              value={featureForm.description}
              onChange={(e) =>
                setFeatureForm((f) => ({ ...f, description: e.target.value }))
              }
            />
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={featureForm.enabled}
                onChange={(e) =>
                  setFeatureForm((f) => ({ ...f, enabled: e.target.checked }))
                }
              />
              Enabled
            </label>
            <Button type="submit">Save feature flag</Button>
          </form>

          <div className="mt-6 space-y-2">
            {(features.data ?? []).map((item) => (
              <button
                key={item.key}
                className="block w-full rounded-xl border border-line p-3 text-left"
                onClick={() =>
                  setFeatureForm({
                    key: item.key,
                    enabled: item.enabled,
                    config: JSON.stringify(item.config, null, 2),
                    description: item.description ?? ""
                  })
                }
              >
                <span className="font-semibold">{item.key}</span>
                <Badge>{item.enabled ? "ON" : "OFF"}</Badge>
              </button>
            ))}
          </div>
        </Card>

        <Card title="Background jobs">
          <form className="space-y-4" onSubmit={(event) => void submitJob(event)}>
            <label className="block text-sm font-medium">
              Job type
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={jobForm.job_type}
                onChange={(e) =>
                  setJobForm((f) => ({
                    ...f,
                    job_type: e.target.value as typeof jobForm.job_type
                  }))
                }
              >
                <option value="HEALTH_SWEEP">Health sweep</option>
                <option value="IMPORT">Import</option>
                <option value="EXPORT">Export</option>
                <option value="REINDEX">Reindex</option>
              </select>
            </label>
            <Input
              label="Target service"
              value={jobForm.target_service}
              onChange={(e) =>
                setJobForm((f) => ({ ...f, target_service: e.target.value }))
              }
            />
            <Input
              label="Resource type"
              value={jobForm.resource_type}
              onChange={(e) =>
                setJobForm((f) => ({ ...f, resource_type: e.target.value }))
              }
            />
            <label className="block text-sm font-medium">
              Parameters JSON
              <textarea
                className="mt-2 min-h-24 w-full rounded-xl border border-line px-3 py-2 font-mono text-xs"
                value={jobForm.parameters}
                onChange={(e) =>
                  setJobForm((f) => ({ ...f, parameters: e.target.value }))
                }
              />
            </label>
            <Button type="submit">Create job</Button>
          </form>

          <div className="mt-6 space-y-2">
            {(jobs.data ?? []).map((item) => (
              <div key={item.id} className="rounded-xl border border-line p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold">{item.jobType}</p>
                    <p className="mt-1 text-xs text-muted">
                      {item.targetService ?? "platform"} · attempts {item.attempts}
                    </p>
                  </div>
                  <Badge>{item.status}</Badge>
                </div>
                {item.error ? (
                  <p className="mt-2 text-xs text-danger">{item.error}</p>
                ) : null}
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card className="mt-6" title="Support queue">
        <div className="space-y-4">
          {(tickets.data ?? []).map((ticket) => {
            const form = ticketUpdates[ticket.id] ?? {
              status: ticket.status,
              priority: ticket.priority,
              assignedTo: ticket.assignedToUserId ?? ""
            };
            return (
              <div key={ticket.id} className="rounded-xl border border-line p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold">
                      {ticket.ticketNumber} · {ticket.subject}
                    </p>
                    <p className="mt-2 text-sm text-muted">{ticket.description}</p>
                  </div>
                  <Badge>{ticket.status}</Badge>
                </div>

                <div className="mt-4 grid gap-3 md:grid-cols-[1fr_1fr_2fr_auto]">
                  <label className="text-sm font-medium">
                    Status
                    <input
                      className="mt-2 w-full rounded-xl border border-line px-3 py-2"
                      value={form.status}
                      onChange={(e) =>
                        setTicketUpdates((current) => ({
                          ...current,
                          [ticket.id]: { ...form, status: e.target.value }
                        }))
                      }
                    />
                  </label>
                  <label className="text-sm font-medium">
                    Priority
                    <input
                      className="mt-2 w-full rounded-xl border border-line px-3 py-2"
                      value={form.priority}
                      onChange={(e) =>
                        setTicketUpdates((current) => ({
                          ...current,
                          [ticket.id]: { ...form, priority: e.target.value }
                        }))
                      }
                    />
                  </label>
                  <label className="text-sm font-medium">
                    Assign to user UUID
                    <input
                      className="mt-2 w-full rounded-xl border border-line px-3 py-2"
                      value={form.assignedTo}
                      onChange={(e) =>
                        setTicketUpdates((current) => ({
                          ...current,
                          [ticket.id]: { ...form, assignedTo: e.target.value }
                        }))
                      }
                    />
                  </label>
                  <Button
                    className="self-end"
                    onClick={() => void updateOneTicket(ticket.id)}
                  >
                    Save
                  </Button>
                </div>
              </div>
            );
          })}
        </div>
      </Card>

      <Card className="mt-6" title="Central audit trail">
        <div className="max-h-[38rem] overflow-auto">
          <table className="w-full min-w-[1000px] text-left text-sm">
            <thead>
              <tr className="border-b border-line text-xs uppercase tracking-wide text-muted">
                <th className="px-2 py-3">Time</th>
                <th className="px-2 py-3">Service</th>
                <th className="px-2 py-3">Action</th>
                <th className="px-2 py-3">Actor</th>
                <th className="px-2 py-3">Entity</th>
                <th className="px-2 py-3">Correlation</th>
              </tr>
            </thead>
            <tbody>
              {(audits.data ?? []).map((item) => (
                <tr key={item.id} className="border-b border-line/70">
                  <td className="px-2 py-3">
                    {item.occurredAt
                      ? new Date(item.occurredAt).toLocaleString()
                      : "—"}
                  </td>
                  <td className="px-2 py-3">{item.sourceService}</td>
                  <td className="px-2 py-3">{item.action}</td>
                  <td className="px-2 py-3">{item.actorUserId ?? "system"}</td>
                  <td className="px-2 py-3">
                    {[item.entityType, item.entityId].filter(Boolean).join(" · ") || "—"}
                  </td>
                  <td className="px-2 py-3">{item.correlationId ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
