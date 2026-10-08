import { describe, expect, it } from "vitest";
import { hasAnyRole, primaryRole } from "./permissions";

describe("role helpers", () => {
  it("matches allowed roles", () => {
    expect(hasAnyRole(["student"], ["student"])).toBe(true);
    expect(hasAnyRole(["teacher"], ["student", "teacher"])).toBe(true);
    expect(hasAnyRole(["student"], ["admin"])).toBe(false);
  });

  it("uses deterministic role priority", () => {
    expect(primaryRole(["student"])).toBe("student");
    expect(primaryRole(["student", "teacher"])).toBe("teacher");
    expect(primaryRole(["student", "admin"])).toBe("admin");
    expect(primaryRole([])).toBeNull();
  });
});
