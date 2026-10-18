import { describe, expect, it } from "vitest";
import { gatewayNamespaces } from "./service-paths";

describe("gateway namespaces", () => {
  it("contains all backend services", () => {
    expect(Object.keys(gatewayNamespaces)).toHaveLength(12);
    expect(gatewayNamespaces.identity).toBe("/api/v1/identity");
    expect(gatewayNamespaces.finance).toBe("/api/v1/finance");
    expect(gatewayNamespaces.payroll).toBe("/api/v1/payroll");
    expect(gatewayNamespaces.platform).toBe("/api/v1/platform");
  });
});
