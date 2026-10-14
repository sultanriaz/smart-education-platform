import { useState, type FormEvent } from "react";
import { apiRequest } from "../../lib/api-client";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { useToast } from "../../components/ui/useToast";
import {
  useCancelTeacherBooking,
  useCreateTeacherBooking,
  useTeacherBookings,
  useTeacherFacilities
} from "../../features/teacher/hooks";

export function TeacherFacilitiesPage() {
  const facilities = useTeacherFacilities();
  const bookings = useTeacherBookings();
  const createBooking = useCreateTeacherBooking();
  const cancelBooking = useCancelTeacherBooking();
  const toast = useToast();

  const [facilityId, setFacilityId] = useState("");
  const [facilitySearch, setFacilitySearch] = useState("");
  const [checking, setChecking] = useState(false);
  const [availability, setAvailability] = useState<string | null>(null);
  async function checkAvailability() {
    if (!facilityId || !startsAt || !endsAt) { toast.push("Select a facility and both times.", "error"); return; }
    const from = new Date(startsAt); const to = new Date(endsAt);
    if (!(to > from)) { toast.push("End must be after start.", "error"); return; }
    try {
      setChecking(true);
      const params = new URLSearchParams({ starts_at: from.toISOString(), ends_at: to.toISOString() });
      const result = await apiRequest<{ available: boolean; conflicts: unknown[] }>(`/api/v1/facilities/facilities/${encodeURIComponent(facilityId)}/availability?${params}`);
      setAvailability(result.available ? "Available for this time window" : `Not available: ${result.conflicts.length} conflicting reservations`);
    } catch (error) { setAvailability(null); toast.push(error instanceof Error ? error.message : "Availability check failed", "error"); }
    finally { setChecking(false); }
  }

  const [purpose, setPurpose] = useState("");
  const [startsAt, setStartsAt] = useState("");
  const [endsAt, setEndsAt] = useState("");
  const [attendees, setAttendees] = useState(1);
  const [cancelReasons, setCancelReasons] = useState<Record<string, string>>({});

  if (facilities.isLoading || bookings.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading facilities…" />
      </div>
    );
  }

  if (facilities.error || bookings.error) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Teacher" title="Facility bookings" />
        <InlineError message="Facility booking data could not be loaded." />
      </div>
    );
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault();

    const start = new Date(startsAt);
    const end = new Date(endsAt);
    if (!facilityId || !purpose.trim() || !startsAt || !endsAt) {
      toast.push("Complete every booking field.", "error");
      return;
    }
    if (end <= start) {
      toast.push("End time must be after start time.", "error");
      return;
    }

    try {
      await createBooking.mutateAsync({
        facility_id: facilityId,
        purpose: purpose.trim(),
        starts_at: start.toISOString(),
        ends_at: end.toISOString(),
        attendees
      });
      setPurpose("");
      toast.push("Facility booking request submitted.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Booking failed.", "error");
    }
  };

  const cancel = async (bookingId: string) => {
    const reason = cancelReasons[bookingId]?.trim();
    if (!reason) {
      toast.push("Enter a cancellation reason.", "error");
      return;
    }

    try {
      await cancelBooking.mutateAsync({ bookingId, reason });
      setCancelReasons((current) => ({ ...current, [bookingId]: "" }));
      toast.push("Booking cancelled.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Cancellation failed.",
        "error"
      );
    }
  };

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Teacher"
        title="Facility bookings"
        description="Request rooms, labs, halls, and other bookable campus facilities for teaching activities."
      />

      <div className="my-4 space-y-3">
        <Input label="Search facilities" value={facilitySearch} onChange={e => setFacilitySearch(e.target.value)} placeholder="Name, code, building, or type" />
        <Button variant="secondary" onClick={() => void checkAvailability()} disabled={checking || !facilityId || !startsAt || !endsAt}>{checking ? "Checking…" : "Check slot availability"}</Button>
        {availability && <p className="text-sm" role="status">{availability}</p>}
      </div>

      <div className="grid gap-6 xl:grid-cols-[0.8fr_1.2fr]">
        <Card title="New booking request">
          <form className="space-y-4" onSubmit={(event) => void submit(event)}>
            <label className="block text-sm font-medium">
              Facility
              <select
                className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={facilityId}
                onChange={(event) => setFacilityId(event.target.value)}
              >
                <option value="">Select facility</option>
                {(facilities.data ?? [])
                  .filter((facility) => facility.isBookable)
                  .map((facility) => (
                    <option key={facility.id} value={facility.id}>
                      {facility.name}
                      {facility.capacity ? ` · capacity ${facility.capacity}` : ""}
                    </option>
                  ))}
              </select>
            </label>

            <Input
              label="Purpose"
              value={purpose}
              onChange={(event) => setPurpose(event.target.value)}
            />

            <Input
              label="Attendees"
              type="number"
              min={1}
              value={attendees}
              onChange={(event) =>
                setAttendees(Math.max(1, Number(event.target.value) || 1))
              }
            />

            <Input
              label="Starts"
              type="datetime-local"
              value={startsAt}
              onChange={(event) => setStartsAt(event.target.value)}
            />

            <Input
              label="Ends"
              type="datetime-local"
              value={endsAt}
              onChange={(event) => setEndsAt(event.target.value)}
            />

            <Button type="submit" disabled={createBooking.isPending}>
              {createBooking.isPending ? "Submitting…" : "Request booking"}
            </Button>
          </form>
        </Card>

        <Card title="My bookings">
          {bookings.data?.length ? (
            <div className="space-y-4">
              {bookings.data.map((booking) => (
                <div key={booking.id} className="rounded-xl border border-line p-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold">{booking.purpose}</p>
                      <p className="mt-1 text-xs text-muted">
                        {new Date(booking.startsAt).toLocaleString()}
                        {" – "}
                        {new Date(booking.endsAt).toLocaleString()}
                      </p>
                      <p className="mt-1 text-xs text-muted">
                        {booking.attendees} attendee
                        {booking.attendees === 1 ? "" : "s"}
                      </p>
                    </div>
                    <Badge>{booking.status}</Badge>
                  </div>

                  {["PENDING", "APPROVED"].includes(booking.status) ? (
                    <div className="mt-4 flex flex-col gap-2 sm:flex-row">
                      <input
                        className="min-w-0 flex-1 rounded-xl border border-line px-3 py-2 text-sm"
                        placeholder="Cancellation reason"
                        value={cancelReasons[booking.id] ?? ""}
                        onChange={(event) =>
                          setCancelReasons((current) => ({
                            ...current,
                            [booking.id]: event.target.value
                          }))
                        }
                      />
                      <Button
                        variant="secondary"
                        onClick={() => void cancel(booking.id)}
                        disabled={cancelBooking.isPending}
                      >
                        Cancel
                      </Button>
                    </div>
                  ) : null}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted">You have no facility bookings yet.</p>
          )}
        </Card>
      </div>
    </div>
  );
}
