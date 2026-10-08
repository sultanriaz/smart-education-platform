import { beforeEach, describe, expect, it } from "vitest";

import { tokenStore } from "./token-store";

describe("Sprint 18 token store", () => {
  beforeEach(() => {
    tokenStore.clear();
    window.sessionStorage.clear();
    window.localStorage.clear();
  });

  it("keeps access token in memory", () => {
    tokenStore.setAccessToken("access");
    expect(tokenStore.getAccessToken()).toBe("access");
  });

  it("never exposes or persists refresh tokens", () => {
    tokenStore.setTokens("access", "refresh-secret");

    expect(tokenStore.getRefreshToken()).toBeNull();
    expect(window.sessionStorage.length).toBe(0);
    expect(window.localStorage.length).toBe(0);
  });

  it("clears the in-memory access token", () => {
    tokenStore.setAccessToken("access");
    tokenStore.clear();
    expect(tokenStore.getAccessToken()).toBeNull();
  });
});
