import { describe, expect, it } from "vitest";
import { defaultTimetableWindow } from "./teacher-api";

describe("teacher API contracts", () => {
  it("creates a finite two-week timetable window", () => {
    const value = defaultTimetableWindow();
    expect(value.startDate).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(value.endDate).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(new Date(value.endDate).getTime()).toBeGreaterThan(
      new Date(value.startDate).getTime()
    );
  });
});
