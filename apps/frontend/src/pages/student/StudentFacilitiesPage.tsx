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
  useBookings,
  useCancelBooking,
  useCreateBooking,
  useFacilities
} from "../../features/student/hooks";

export function StudentFacilitiesPage() {
  const facilities = useFacilities();
  const bookings = useBookings();
  const createBooking = useCreateBooking();
  const cancelBooking = useCancelBooking();
  const toast = useToast();

  const [facilityId, setFacilityId] = useState("");
  const [startsAt, setStartsAt] = useState("");
  const [endsAt, setEndsAt] = useState("");
  const [purpose, setPurpose] = useState("");
  const [attendees, setAttendees] = useState(1);
  const [cancellationReason, setCancellationReason] = useState("");

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
        <PageHeader eyebrow="Student" title="Facility bookings" />
        <InlineError message="Facility information could not be loaded." />
      </div>
    );
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault();

    if (!facilityId || !startsAt || !endsAt || !purpose.trim()) {
      toast.push("Complete all booking fields.", "error");
      return;
    }

    const start = new Date(startsAt);
    const end = new Date(endsAt);
    if (end <= start) {
      toast.push("Booking end time must be after the start time.", "error");
      return;
    }

    try {
      await createBooking.mutateAsync({
        facility_id: facilityId,
        starts_at: start.toISOString(),
        ends_at: end.toISOString(),
        purpose: purpose.trim(),
        attendees
      });
      setPurpose("");
      toast.push("Booking request submitted.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Booking failed.", "error");
    }
  };

  const cancel = async (bookingId: string) => {
    try {
      await cancelBooking.mutateAsync({ bookingId, reason: cancellationReason.trim() });
      toast.push("Booking cancelled.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Cancellation failed.", "error");
    }
  };

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Student"
        title="Facility bookings"
        description="Browse bookable campus facilities and request an available time slot."
      />

      <div className="grid gap-6 xl:grid-cols-[1fr_1.25fr]">
        <Card title="Request a booking">
          <form className="space-y-4" onSubmit={(event) => void submit(event)}>
            <Input label="Attendees" type="number" min={1} required value={attendees} onChange={event => setAttendees(Number(event.target.value))} />
            <label className="block text-sm font-medium">
              Facility
              <select
                className="mt-2 block w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={facilityId}
                onChange={(event) => setFacilityId(event.target.value)}
              >
                <option value="">Select a facility</option>
                {(facilities.data ?? [])
                  .filter((item) => item.isBookable)
                  .map((facility) => (
                    <option key={facility.id} value={facility.id}>
                      {facility.name}
                      {facility.capacity ? ` · capacity ${facility.capacity}` : ""}
                    </option>
                  ))}
              </select>
            </label>

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

            <label className="block text-sm font-medium">
              Purpose
              <textarea
                className="mt-2 min-h-24 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                value={purpose}
                onChange={(event) => setPurpose(event.target.value)}
                placeholder="Describe why you need this facility."
              />
            </label>

            <Button type="submit" disabled={createBooking.isPending}>
              {createBooking.isPending ? "Submitting…" : "Request booking"}
            </Button>
          </form>
        </Card>

        <Card title="My bookings">
          <Input label="Cancellation reason" value={cancellationReason} onChange={event => setCancellationReason(event.target.value)} placeholder="Required when cancelling a booking" />
          {bookings.data?.length ? (
            <div className="space-y-3">
              {bookings.data.map((booking) => (
                <div key={booking.id} className="rounded-xl border border-line p-4">
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="font-semibold">
                        {booking.facilityName ?? booking.facilityId}
                      </p>
                      <p className="mt-1 text-xs text-muted">
                        {new Date(booking.startsAt).toLocaleString()}
                        {" – "}
                        {new Date(booking.endsAt).toLocaleString()}
                      </p>
                    </div>
                    <Badge>{booking.status}</Badge>
                  </div>

                  {booking.purpose ? (
                    <p className="mt-3 text-sm text-muted">{booking.purpose}</p>
                  ) : null}

                  {["PENDING", "APPROVED"].includes(booking.status) ? (
                    <Button
                      variant="secondary"
                      className="mt-4"
                      onClick={() => void cancel(booking.id)}
                      disabled={cancelBooking.isPending || cancellationReason.trim().length < 3}
                    >
                      Cancel booking
                    </Button>
                  ) : null}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted">You have not requested any bookings yet.</p>
          )}
        </Card>
      </div>
    </div>
  );
}
