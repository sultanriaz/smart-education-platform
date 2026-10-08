import { describe, expect, it } from "vitest";
import {
  normalizeAnnouncement,
  normalizeAttendanceSession,
  normalizeQuestion,
  normalizeSection,
  normalizeTimetable
} from "./normalizers";

describe("teacher normalizers", () => {
  it("normalizes an academic section", () => {
    const section = normalizeSection({
      section_id: "section-1",
      section_name: "BSCS-7A",
      course_id: "course-1",
      course_code: "CSC401",
      course_title: "Software Engineering"
    });

    expect(section.id).toBe("section-1");
    expect(section.courseCode).toBe("CSC401");
  });

  it("normalizes scheduling occurrences with date/time parts", () => {
    const item = normalizeTimetable({
      occurrence_id: "o1",
      occurrence_date: "2026-10-07",
      section_id: "s1",
      starts_at: "09:00:00",
      ends_at: "10:30:00"
    });

    expect(item.startsAt).toContain("2026-10-07T09:00:00");
    expect(item.endsAt).toContain("2026-10-07T10:30:00");
  });

  it("normalizes attendance session state", () => {
    const session = normalizeAttendanceSession({
      id: "a1",
      section_id: "s1",
      session_date: "2026-10-07",
      status: "OPEN"
    });

    expect(session.status).toBe("OPEN");
  });

  it("keeps teacher answer keys available only in teacher question model", () => {
    const question = normalizeQuestion({
      id: "q1",
      bank_id: "b1",
      question_type: "MCQ_SINGLE",
      prompt: "Question?",
      points: 1,
      choices: [
        { id: "c1", text: "A", is_correct: true },
        { id: "c2", text: "B", is_correct: false }
      ]
    });

    expect(question.choices[0]?.isCorrect).toBe(true);
  });

  it("normalizes teacher section announcements", () => {
    const announcement = normalizeAnnouncement({
      id: "c1",
      target_value: { section_id: "s1" },
      title: "Room change",
      body: "Use Lab 2",
      channels: ["IN_APP"],
      recipient_count: 25,
      status: "COMPLETED",
      created_at: "2026-10-07T10:00:00Z"
    });

    expect(announcement.sectionId).toBe("s1");
    expect(announcement.recipientCount).toBe(25);
  });
});
