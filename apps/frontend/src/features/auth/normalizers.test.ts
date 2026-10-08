import { describe, expect, it } from "vitest";
import { normalizeTokenPair, normalizeUser } from "./normalizers";

describe("identity normalizers", () => {
  it("normalizes snake case tokens", () => {
    expect(normalizeTokenPair({ access_token: "a", refresh_token: "r" })).toEqual({
      accessToken: "a",
      refreshToken: "r"
    });
  });

  it("normalizes role objects", () => {
    const user = normalizeUser({
      id: "11111111-1111-1111-1111-111111111111",
      roles: [{ name: "Student" }]
    });
    expect(user.roles).toEqual(["student"]);
  });
});
