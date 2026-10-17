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
  useAdminBookings,
  useAdminFacilities,
  useEquipment,
  useAdminMutation,
  useFacilityBlocks
} from "../../features/admin/hooks";

export function AdminFacilitiesPage() {
  const facilities = useAdminFacilities();
  const equipment = useEquipment();
  const bookings = useAdminBookings();
  const blocks = useFacilityBlocks();
  const toast = useToast();

  const createEquipment = useAdminMutation(api.createEquipment, adminKeys.equipment);
  const assignEquipment = useAdminMutation(api.assignEquipment, adminKeys.facilities);
  const [equipmentForm, setEquipmentForm] = useState({code:"", name:"", description:""});
  const [equipmentAssignment, setEquipmentAssignment] = useState({facilityId:"", equipment_id:"", quantity:1});
  const createFacility = useAdminMutation(api.createFacility, adminKeys.facilities);
  const updateFacility = useAdminMutation(
    ({ id, input }: { id: string; input: Parameters<typeof api.updateFacility>[1] }) =>
      api.updateFacility(id, input),
    adminKeys.facilities
  );
  const decideBooking = useAdminMutation(
    ({
      id,
      decision,
      note
    }: {
      id: string;
      decision: "approve" | "reject";
      note?: string;
    }) => api.decideBooking(id, decision, note),
    adminKeys.bookings
  );
  const createBlock = useAdminMutation(api.createFacilityBlock, adminKeys.blocks);
  const cancelBlock = useAdminMutation(api.cancelFacilityBlock, adminKeys.blocks);

  const [facilityForm, setFacilityForm] = useState({
    code: "",
    name: "",
    kind: "ROOM",
    description: "",
    building: "",
    floor: "",
    capacity: 30,
    opens_at_local: "",
    closes_at_local: "",
    operating_timezone: "UTC",
    is_bookable: true
  });
  const [decisionNotes, setDecisionNotes] = useState<Record<string, string>>({});
  const [blockForm, setBlockForm] = useState({
    facility_id: "",
    starts_at: "",
    ends_at: "",
    reason: ""
  });

  if (facilities.isLoading || bookings.isLoading || blocks.isLoading || equipment.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading facility administration…" />
      </div>
    );
  }

  if (facilities.error || bookings.error || blocks.error || equipment.error) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Admin" title="Facilities" />
        <InlineError message="Facility administration data could not be loaded." />
      </div>
    );
  }

  async function perform<T>(fn: () => Promise<T>, message: string) {
    try {
      await fn();
      toast.push(message, "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Facility operation failed.", "error");
    }
  }

  const submitFacility = async (event: FormEvent) => {
    event.preventDefault();
    await perform(
      () =>
        createFacility.mutateAsync({
          code: facilityForm.code,
          name: facilityForm.name,
          kind: facilityForm.kind,
          description: facilityForm.description || undefined,
          building: facilityForm.building || undefined,
          floor: facilityForm.floor || undefined,
          capacity: facilityForm.capacity,
          is_bookable: facilityForm.is_bookable,
          opens_at_local: facilityForm.opens_at_local || undefined,
          closes_at_local: facilityForm.closes_at_local || undefined,
          operating_timezone: facilityForm.operating_timezone,
          metadata: {}
        }),
      "Facility created."
    );
  };

  const submitBlock = async (event: FormEvent) => {
    event.preventDefault();
    if (!blockForm.facility_id || !blockForm.starts_at || !blockForm.ends_at) {
      toast.push("Complete all block fields.", "error");
      return;
    }

    const start = new Date(blockForm.starts_at);
    const end = new Date(blockForm.ends_at);
    if (end <= start) {
      toast.push("Block end must be after start.", "error");
      return;
    }

    await perform(
      () =>
        createBlock.mutateAsync({
          facility_id: blockForm.facility_id,
          starts_at: start.toISOString(),
          ends_at: end.toISOString(),
          reason: blockForm.reason
        }),
      "Facility block created."
    );
  };

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Admin"
        title="Facilities"
        description="Manage rooms/labs, approve or reject booking requests, and block unavailable facility windows."
      />

      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="Equipment administration">
          <form className="space-y-3" onSubmit={event => {
            event.preventDefault(); void perform(() => createEquipment.mutateAsync(equipmentForm), "Equipment created.");
          }}>
            <Input label="Equipment code" value={equipmentForm.code} onChange={e => setEquipmentForm(f=>({...f,code:e.target.value}))} />
            <Input label="Equipment name" value={equipmentForm.name} onChange={e => setEquipmentForm(f=>({...f,name:e.target.value}))} />
            <Button type="submit" disabled={createEquipment.isPending}>Create equipment</Button>
          </form>
          <form className="mt-5 space-y-3" onSubmit={event => {
            event.preventDefault(); void perform(() => assignEquipment.mutateAsync(equipmentAssignment), "Equipment assigned.");
          }}>
            <label className="block text-sm font-medium">Facility
              <select className="mt-2 w-full rounded-xl border border-line bg-panel p-3" value={equipmentAssignment.facilityId}
                onChange={e => setEquipmentAssignment(f=>({...f,facilityId:e.target.value}))}>
                <option value="">Select facility</option>
                {(facilities.data ?? []).map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
              </select>
            </label>
            <label className="block text-sm font-medium">Equipment
              <select className="mt-2 w-full rounded-xl border border-line bg-panel p-3" value={equipmentAssignment.equipment_id}
                onChange={e => setEquipmentAssignment(f=>({...f,equipment_id:e.target.value}))}>
                <option value="">Select equipment</option>
                {(equipment.data ?? []).map(x => <option key={x.id} value={x.id}>{x.name}</option>)}
              </select>
            </label>
            <Input label="Quantity" type="number" min={1} value={equipmentAssignment.quantity}
              onChange={e => setEquipmentAssignment(f=>({...f,quantity:Number(e.target.value)}))} />
            <Button type="submit" disabled={!equipmentAssignment.facilityId || !equipmentAssignment.equipment_id || assignEquipment.isPending}>Assign equipment</Button>
          </form>
        </Card>
        <Card title="Create facility">
          <form className="space-y-4" onSubmit={(event) => void submitFacility(event)}>
            <div className="grid gap-3 sm:grid-cols-2">
              <Input
                label="Code"
                value={facilityForm.code}
                onChange={(e) =>
                  setFacilityForm((f) => ({ ...f, code: e.target.value }))
                }
              />
              <Input
                label="Name"
                value={facilityForm.name}
                onChange={(e) =>
                  setFacilityForm((f) => ({ ...f, name: e.target.value }))
                }
              />
            </div>

            <label className="block text-sm font-medium">
              Kind
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={facilityForm.kind}
                onChange={(e) =>
                  setFacilityForm((f) => ({ ...f, kind: e.target.value }))
                }
              >
                {["ROOM", "LAB", "HALL", "AUDITORIUM", "SPORTS", "OTHER"].map((kind) => (
                  <option key={kind} value={kind}>{kind}</option>
                ))}
              </select>
            </label>

            <Input
              label="Description"
              value={facilityForm.description}
              onChange={(e) =>
                setFacilityForm((f) => ({ ...f, description: e.target.value }))
              }
            />

            <div className="grid gap-3 sm:grid-cols-2">
              <Input
                label="Building"
                value={facilityForm.building}
                onChange={(e) =>
                  setFacilityForm((f) => ({ ...f, building: e.target.value }))
                }
              />
              <Input
                label="Floor"
                value={facilityForm.floor}
                onChange={(e) =>
                  setFacilityForm((f) => ({ ...f, floor: e.target.value }))
                }
              />
            </div>

            <Input
              label="Capacity"
              type="number"
              min={1}
              value={facilityForm.capacity}
              onChange={(e) =>
                setFacilityForm((f) => ({
                  ...f,
                  capacity: Number(e.target.value) || 1
                }))
              }
            />

            <div className="grid gap-3 sm:grid-cols-2">
              <Input label="Opening time (optional)" type="time" value={facilityForm.opens_at_local}
                onChange={e => setFacilityForm(f=>({...f,opens_at_local:e.target.value}))} />
              <Input label="Closing time (optional)" type="time" value={facilityForm.closes_at_local}
                onChange={e => setFacilityForm(f=>({...f,closes_at_local:e.target.value}))} />
            </div>
            <Input label="Operating timezone (IANA)" value={facilityForm.operating_timezone}
              onChange={e => setFacilityForm(f=>({...f,operating_timezone:e.target.value}))} />
            <label className="flex items-center gap-3 rounded-xl border border-line p-3 text-sm">
              <input
                type="checkbox"
                checked={facilityForm.is_bookable}
                onChange={(e) =>
                  setFacilityForm((f) => ({
                    ...f,
                    is_bookable: e.target.checked
                  }))
                }
              />
              Allow booking requests
            </label>

            <Button type="submit" disabled={createFacility.isPending}>
              Create facility
            </Button>
          </form>
        </Card>

        <Card title="Block facility availability">
          <form className="space-y-4" onSubmit={(event) => void submitBlock(event)}>
            <label className="block text-sm font-medium">
              Facility
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={blockForm.facility_id}
                onChange={(e) =>
                  setBlockForm((f) => ({ ...f, facility_id: e.target.value }))
                }
              >
                <option value="">Select facility</option>
                {(facilities.data ?? []).map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.code} · {item.name}
                  </option>
                ))}
              </select>
            </label>
            <Input
              label="Starts"
              type="datetime-local"
              value={blockForm.starts_at}
              onChange={(e) =>
                setBlockForm((f) => ({ ...f, starts_at: e.target.value }))
              }
            />
            <Input
              label="Ends"
              type="datetime-local"
              value={blockForm.ends_at}
              onChange={(e) =>
                setBlockForm((f) => ({ ...f, ends_at: e.target.value }))
              }
            />
            <Input
              label="Reason"
              value={blockForm.reason}
              onChange={(e) =>
                setBlockForm((f) => ({ ...f, reason: e.target.value }))
              }
            />
            <Button type="submit" disabled={createBlock.isPending}>
              Create block
            </Button>
          </form>

          <div className="mt-6 space-y-3">
            {(blocks.data ?? []).map((item) => (
              <div key={item.id} className="rounded-xl border border-line p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold">Facility {item.facilityId}</p>
                    <p className="mt-1 text-xs text-muted">
                      {new Date(item.startsAt).toLocaleString()} –{" "}
                      {new Date(item.endsAt).toLocaleString()}
                    </p>
                    <p className="mt-2 text-sm text-muted">{item.reason}</p>
                  </div>
                  <Badge>{item.status}</Badge>
                </div>
                {item.status !== "CANCELLED" ? (
                  <Button
                    variant="secondary"
                    className="mt-3"
                    onClick={() =>
                      void perform(
                        () => cancelBlock.mutateAsync(item.id),
                        "Facility block cancelled."
                      )
                    }
                  >
                    Cancel block
                  </Button>
                ) : null}
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card className="mt-6" title="Facility directory">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[850px] text-left text-sm">
            <thead>
              <tr className="border-b border-line text-xs uppercase tracking-wide text-muted">
                <th className="px-2 py-3">Facility</th>
                <th className="px-2 py-3">Location</th>
                <th className="px-2 py-3">Capacity</th>
                <th className="px-2 py-3">Active</th>
                <th className="px-2 py-3">Bookable</th>
                <th className="px-2 py-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {(facilities.data ?? []).map((item) => (
                <tr key={item.id} className="border-b border-line/70">
                  <td className="px-2 py-3">
                    <p className="font-semibold">{item.code} · {item.name}</p>
                    <p className="mt-1 text-xs text-muted">{item.kind}</p>
                  </td>
                  <td className="px-2 py-3">
                    {[item.building, item.floor].filter(Boolean).join(" · ") || "—"}
                  </td>
                  <td className="px-2 py-3">{item.capacity}</td>
                  <td className="px-2 py-3">{item.isActive ? "Yes" : "No"}</td>
                  <td className="px-2 py-3">{item.isBookable ? "Yes" : "No"}</td>
                  <td className="px-2 py-3">
                    <Button
                      variant="secondary"
                      onClick={() =>
                        void perform(
                          () =>
                            updateFacility.mutateAsync({
                              id: item.id,
                              input: { is_bookable: !item.isBookable }
                            }),
                          item.isBookable
                            ? "Facility booking disabled."
                            : "Facility booking enabled."
                        )
                      }
                    >
                      {item.isBookable ? "Disable booking" : "Enable booking"}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      <Card className="mt-6" title="Booking approval queue">
        <div className="space-y-4">
          {(bookings.data ?? []).map((item) => (
            <div key={item.id} className="rounded-xl border border-line p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="font-semibold">{item.purpose}</p>
                  <p className="mt-1 text-xs text-muted">
                    Facility {item.facilityId} · requester {item.requesterUserId}
                  </p>
                  <p className="mt-1 text-xs text-muted">
                    {new Date(item.startsAt).toLocaleString()} –{" "}
                    {new Date(item.endsAt).toLocaleString()} · {item.attendees} attendees
                  </p>
                </div>
                <Badge>{item.status}</Badge>
              </div>

              {item.status === "PENDING" ? (
                <div className="mt-4 flex flex-col gap-2 sm:flex-row">
                  <input
                    className="min-w-0 flex-1 rounded-xl border border-line px-3 py-2 text-sm"
                    placeholder="Decision note (optional)"
                    value={decisionNotes[item.id] ?? ""}
                    onChange={(e) =>
                      setDecisionNotes((current) => ({
                        ...current,
                        [item.id]: e.target.value
                      }))
                    }
                  />
                  <Button
                    onClick={() =>
                      void perform(
                        () =>
                          decideBooking.mutateAsync({
                            id: item.id,
                            decision: "approve",
                            note: decisionNotes[item.id]
                          }),
                        "Booking approved."
                      )
                    }
                  >
                    Approve
                  </Button>
                  <Button
                    variant="secondary"
                    onClick={() =>
                      void perform(
                        () =>
                          decideBooking.mutateAsync({
                            id: item.id,
                            decision: "reject",
                            note: decisionNotes[item.id]
                          }),
                        "Booking rejected."
                      )
                    }
                  >
                    Reject
                  </Button>
                </div>
              ) : null}
            </div>
          ))}

          {!(bookings.data ?? []).length ? (
            <p className="text-sm text-muted">No booking records are available.</p>
          ) : null}
        </div>
      </Card>
    </div>
  );
}
