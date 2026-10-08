import { describe, expect, it } from "vitest";
import {
  campaign,
  facility,
  reportingOverview,
  serviceHealth,
  user
} from "./normalizers";

describe("admin normalizers", () => {
  it("normalizes Identity users and roles", () => {
    const value = user({
      id: "u1",
      email: "admin@example.edu",
      full_name: "Platform Admin",
      is_active: true,
      is_verified: true,
      roles: [{ name: "admin" }]
    });

    expect(value.fullName).toBe("Platform Admin");
    expect(value.roles).toEqual(["admin"]);
  });

  it("normalizes Facility Service schema", () => {
    const value = facility({
      id: "f1",
      code: "LAB-1",
      name: "Computer Lab",
      kind: "LAB",
      capacity: 40,
      is_active: true,
      is_bookable: true
    });

    expect(value.kind).toBe("LAB");
    expect(value.capacity).toBe(40);
  });

  it("normalizes Reporting overview", () => {
    const value = reportingOverview({
      active_enrollments: 100,
      attendance_records: 500,
      attendance_percentage: 88.5,
      graded_attempts: 42,
      assessment_average_percent: 73,
      assessment_pass_rate: 81,
      facility_bookings: 20,
      approved_facility_bookings: 12,
      notification_deliveries: 400,
      notification_success_rate: 99.2,
      schedule_changes: 8
    });

    expect(value.activeEnrollments).toBe(100);
    expect(value.notificationSuccessRate).toBe(99.2);
  });

  it("normalizes service health sweep", () => {
    const value = serviceHealth({
      service_name: "identity",
      status: "healthy",
      health_ok: true,
      ready_ok: true,
      latency_ms: 12
    });

    expect(value.healthOk).toBe(true);
    expect(value.latencyMs).toBe(12);
  });

  it("normalizes notification campaigns", () => {
    const value = campaign({
      id: "c1",
      target_kind: "ROLE",
      target_value: { role: "student" },
      category: "general",
      channels: ["IN_APP"],
      status: "COMPLETED",
      recipient_count: 10,
      created_at: "2026-10-07T10:00:00Z"
    });

    expect(value.targetKind).toBe("ROLE");
    expect(value.recipientCount).toBe(10);
  });
});
