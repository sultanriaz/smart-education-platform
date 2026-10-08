import { describe, expect, it } from "vitest";
import { gatewayNamespaces } from "../../lib/service-paths";

describe("admin service boundaries", () => {
  it("uses every required Gateway namespace", () => {
    expect(gatewayNamespaces.identity).toBe("/api/v1/identity");
    expect(gatewayNamespaces.academic).toBe("/api/v1/academic");
    expect(gatewayNamespaces.scheduling).toBe("/api/v1/scheduling");
    expect(gatewayNamespaces.notifications).toBe("/api/v1/notifications");
    expect(gatewayNamespaces.facilities).toBe("/api/v1/facilities");
    expect(gatewayNamespaces.reporting).toBe("/api/v1/reporting");
    expect(gatewayNamespaces.platform).toBe("/api/v1/platform");
  });
});
