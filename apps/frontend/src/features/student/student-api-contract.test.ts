import { describe, expect, it } from "vitest";

import { gatewayNamespaces } from "../../lib/service-paths";

describe("student UX service boundaries", () => {
  it("uses gateway namespaces for every student domain", () => {
    expect(gatewayNamespaces.attendance).toBe("/api/v1/attendance");
    expect(gatewayNamespaces.scheduling).toBe("/api/v1/scheduling");
    expect(gatewayNamespaces.notifications).toBe("/api/v1/notifications");
    expect(gatewayNamespaces.facilities).toBe("/api/v1/facilities");
    expect(gatewayNamespaces.learning).toBe("/api/v1/learning");
    expect(gatewayNamespaces.assessments).toBe("/api/v1/assessments");
  });
});
