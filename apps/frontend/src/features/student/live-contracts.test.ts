import { describe, expect, it } from "vitest";
import { normalizeAttendanceSummary, normalizeLearningResource, normalizeTimetableItem } from "./normalizers";

describe("merged service response contracts", () => {
  it("reads the owned Attendance totals envelope", () => {
    expect(normalizeAttendanceSummary({ totals: { present_sessions: 3, late_sessions: 1, absent_sessions: 1, total_considered_sessions: 5, attendance_percentage: 80 } }))
      .toMatchObject({ present: 3, late: 1, absent: 1, totalConsidered: 5, percentage: 80 });
  });
  it("reads versioned notes from recommendation envelopes", () => {
    const resource = normalizeLearningResource({ resource: { id: "r1", title: "Notes", resource_type: "NOTE", versions: [
      { version_number: 2, text_content: "Current notes" }, { version_number: 1, text_content: "Old notes" }
    ] }, score: 90 });
    expect(resource).toMatchObject({ id: "r1", title: "Notes", textContent: "Current notes", score: 90 });
  });
  it("combines scheduling occurrence dates with time fields", () => {
    expect(normalizeTimetableItem({ occurrence_date: "2026-10-08", starts_at: "09:00:00", ends_at: "10:00:00" }))
      .toMatchObject({ startsAt: "2026-10-08T09:00:00", endsAt: "2026-10-08T10:00:00" });
  });
});
