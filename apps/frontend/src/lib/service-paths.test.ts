import { describe, expect, it } from "vitest";
import { gatewayNamespaces } from "./service-paths";

describe("gateway namespaces", () => {
  it("contains all backend services", () => {
    expect(Object.keys(gatewayNamespaces)).toHaveLength(10);
    expect(gatewayNamespaces.identity).toBe("/api/v1/identity");
    expect(gatewayNamespaces.platform).toBe("/api/v1/platform");
  });
});
