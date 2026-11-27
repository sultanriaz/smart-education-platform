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
import { DynamicSpaceFinder } from "../../components/facilities/DynamicSpaceFinder";
import { Sparkles, Building2 } from "lucide-react";

export function TeacherFacilitiesPage() {
  const facilities = useTeacherFacilities();
  const bookings = useTeacherBookings();
  const createBooking = useCreateTeacherBooking();
  const cancelBooking = useCancelTeacherBooking();
  const toast = useToast();

  const [activeTab, setActiveTab] = useState<"space_finder" | "formal_bookings">("space_finder");

  const [facilityId, setFacilityId] = useState("");
  const [facilitySearch, setFacilitySearch] = useState("");
  const [checking, setChecking] = useState(false);
  const [availability, setAvailability] = useState<string | null>(null);

  async function checkAvailability() {
    if (!facilityId || !startsAt || !endsAt) {
      toast.push("Select a facility and both times.", "error");
      return;
    }
    const from = new Date(startsAt);
    const to = new Date(endsAt);
    if (!(to > from)) {
      toast.push("End must be after start.", "error");
      return;
    }
    try {
      setChecking(true);
      const params = new URLSearchParams({ starts_at: from.toISOString(), ends_at: to.toISOString() });
      const result = await apiRequest<{ available: boolean; conflicts: unknown[] }>(
        `/api/v1/facilities/facilities/${encodeURIComponent(facilityId)}/availability?${params}`
      );
      setAvailability(
        result.available
          ? "Available for this time window"
          : `Not available: ${result.conflicts.length} conflicting reservations`
      );
    } catch (error) {
      setAvailability(null);
      toast.push(error instanceof Error ? error.message : "Availability check failed", "error");
    } finally {
      setChecking(false);
    }
  }

  const [purpose, setPurpose] = useState("");
  const [startsAt, setStartsAt] = useState("");
  const [endsAt, setEndsAt] = useState("");
  const [attendees, setAttendees] = useState(1);
  const [cancelReasons, setCancelReasons] = useState<Record<string, string>>({});

  if (facilities.isLoading || bookings.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading faculty spaces & facilities…" />
      </div>
    );
  }

  if (facilities.error || bookings.error) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Teacher" title="Faculty Facility & Space Booking" />
        <InlineError
          message="Facility booking data could not be loaded."
          onRetry={() => {
            void facilities.refetch();
            void bookings.refetch();
          }}
          isRetrying={facilities.isFetching || bookings.isFetching}
        />
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
      setCancelReasons((prev) => ({ ...prev, [bookingId]: "" }));
      toast.push("Booking cancelled.", "success");
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Cancellation failed.", "error");
    }
  };

  return (
    <div className="page-container space-y-6">
      <PageHeader
        eyebrow="Faculty Operations"
        title="Dynamic Space Finder & Free Slots Navigator"
        description="Inspect block-by-block classroom telemetry, find free lecture slots for makeup classes, or reserve labs for examinations and viva sessions."
      />

      {/* Top Workspace Tabs */}
      <div className="flex border-b border-line gap-2">
        <button
          onClick={() => setActiveTab("space_finder")}
          className={`flex items-center gap-2 border-b-2 px-4 py-3 text-sm font-semibold transition ${
            activeTab === "space_finder"
              ? "border-brand-600 text-brand-600"
              : "border-transparent text-muted hover:text-ink"
          }`}
        >
          <Sparkles size={16} />
          <span>Dynamic Space Finder (Live Free Slots)</span>
        </button>

        <button
          onClick={() => setActiveTab("formal_bookings")}
          className={`flex items-center gap-2 border-b-2 px-4 py-3 text-sm font-semibold transition ${
            activeTab === "formal_bookings"
              ? "border-brand-600 text-brand-600"
              : "border-transparent text-muted hover:text-ink"
          }`}
        >
          <Building2 size={16} />
          <span>Formal Faculty Reservations & Ledger</span>
          {bookings.data && bookings.data.length > 0 && (
            <span className="rounded-full bg-surface px-2 py-0.5 text-2xs font-bold text-muted border border-line">
              {bookings.data.length}
            </span>
          )}
        </button>
      </div>

      {/* TAB 1: DYNAMIC SPACE FINDER FOR FACULTY */}
      {activeTab === "space_finder" && (
        <DynamicSpaceFinder
          mode="teacher"
          onBookingSuccess={(res) => {
            toast.push(`Room ${res.roomCode} locked for faculty session!`, "success");
          }}
        />
      )}

      {/* TAB 2: FORMAL FACILITY BOOKINGS & LEDGER */}
      {activeTab === "formal_bookings" && (
        <div className="space-y-6">
          <div className="my-2 space-y-3">
            <Input
              label="Search facilities"
              value={facilitySearch}
              onChange={(e) => setFacilitySearch(e.target.value)}
              placeholder="Name, code, building, or type"
            />
            <Button
              variant="secondary"
              onClick={() => void checkAvailability()}
              disabled={checking || !facilityId || !startsAt || !endsAt}
            >
              {checking ? "Checking…" : "Check slot availability"}
            </Button>
            {availability && (
              <p className="text-sm font-semibold text-brand-600" role="status">
                {availability}
              </p>
            )}
          </div>

          <div className="grid gap-6 xl:grid-cols-[1fr_1.25fr]">
            <Card title="Reserve faculty space">
              <form className="space-y-4" onSubmit={(event) => void submit(event)}>
                <Input
                  label="Attendees"
                  type="number"
                  min={1}
                  required
                  value={attendees}
                  onChange={(event) => setAttendees(Number(event.target.value))}
                />
                <label className="block text-sm font-medium">
                  Facility
                  <select
                    className="mt-2 block w-full rounded-xl border border-line bg-panel px-3 py-2.5 text-sm"
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
                    className="mt-2 min-h-24 w-full rounded-xl border border-line bg-panel px-3 py-2.5 text-sm"
                    value={purpose}
                    onChange={(event) => setPurpose(event.target.value)}
                    placeholder="Describe why you need this facility (e.g. Makeup Lecture, Lab Exam)."
                  />
                </label>

                <Button type="submit" disabled={createBooking.isPending}>
                  {createBooking.isPending ? "Submitting…" : "Submit faculty booking"}
                </Button>
              </form>
            </Card>

            <Card title="My Faculty Bookings">
              {bookings.data?.length ? (
                <div className="space-y-4">
                  {bookings.data.map((booking) => (
                    <div key={booking.id} className="rounded-xl border border-line p-4 space-y-3">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <p className="font-semibold text-ink">
                            {booking.facilityId}
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
                        <p className="text-sm text-muted">{booking.purpose}</p>
                      ) : null}

                      {["PENDING", "APPROVED"].includes(booking.status) ? (
                        <div className="pt-2 border-t border-line/60 space-y-2">
                          <Input
                            label="Reason for cancellation"
                            value={cancelReasons[booking.id] ?? ""}
                            onChange={(event) =>
                              setCancelReasons((prev) => ({
                                ...prev,
                                [booking.id]: event.target.value
                              }))
                            }
                            placeholder="State reason (e.g. Rescheduled lecture)"
                          />
                          <Button
                            variant="secondary"
                            onClick={() => void cancel(booking.id)}
                            disabled={
                              cancelBooking.isPending ||
                              ((cancelReasons[booking.id]?.trim().length ?? 0) < 3)
                            }
                          >
                            Cancel booking
                          </Button>
                        </div>
                      ) : null}
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted">No faculty bookings recorded.</p>
              )}
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
