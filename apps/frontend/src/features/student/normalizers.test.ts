import { describe, expect, it } from "vitest";

import {
  extractList,
  normalizeAssignmentDetail,
  normalizeAttendanceSummary,
  normalizeBooking,
  normalizeNotification
} from "./normalizers";

describe("student response normalizers", () => {
  it("extracts common paginated list shapes", () => {
    expect(extractList({ items: [{ id: 1 }] })).toHaveLength(1);
    expect(extractList({ records: [{ id: 1 }, { id: 2 }] })).toHaveLength(2);
    expect(extractList([])).toEqual([]);
  });

  it("normalizes attendance summary contract variants", () => {
    expect(
      normalizeAttendanceSummary({
        present_sessions: 8,
        absent_sessions: 2,
        late_sessions: 1,
        excused_sessions: 1,
        total_considered_sessions: 11,
        attendance_percentage: 81.82
      })
    ).toEqual({
      present: 8,
      absent: 2,
      late: 1,
      excused: 1,
      totalConsidered: 11,
      percentage: 81.82
    });
  });

  it("never requires answer-key fields for assessment rendering", () => {
    const detail = normalizeAssignmentDetail({
      id: "assignment-1",
      quiz_id: "quiz-1",
      title: "Quiz",
      opens_at: "2026-10-07T10:00:00Z",
      due_at: "2026-10-07T11:00:00Z",
      attempt_limit: 1,
      questions: [
        {
          id: "q1",
          question_type: "MCQ_SINGLE",
          prompt: "Question?",
          points: 1,
          choices: [
            { id: "c1", text: "A" },
            { id: "c2", text: "B" }
          ]
        }
      ]
    });

    expect(detail.questions[0]?.choices).toEqual([
      { id: "c1", text: "A" },
      { id: "c2", text: "B" }
    ]);
  });

  it("normalizes booking status", () => {
    expect(
      normalizeBooking({
        id: "b1",
        facility_id: "f1",
        starts_at: "2026-10-07T10:00:00Z",
        ends_at: "2026-10-07T11:00:00Z",
        status: "PENDING"
      }).status
    ).toBe("PENDING");
  });

  it("normalizes unread notification", () => {
    const item = normalizeNotification({
      id: "n1",
      title: "Schedule updated",
      message: "Room changed",
      created_at: "2026-10-07T10:00:00Z"
    });
    expect(item.readAt).toBeNull();
  });
});
