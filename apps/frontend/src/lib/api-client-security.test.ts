import { beforeEach, describe, expect, it, vi } from "vitest";

import { apiRequest, refreshAccessToken } from "./api-client";
import { tokenStore } from "./token-store";

describe("Sprint 18 API client security", () => {
  beforeEach(() => {
    tokenStore.clear();
    vi.restoreAllMocks();
  });

  it("uses credentials include for API requests", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      })
    );

    await apiRequest("/api/v1/platform/test", {
      method: "GET",
      auth: false
    });

    expect(fetchMock.mock.calls[0]?.[1]?.credentials).toBe("include");
  });

  it("does not add idempotency keys to password recovery endpoints", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ message: "accepted" }), {
        status: 202,
        headers: { "Content-Type": "application/json" }
      })
    );

    await apiRequest("/api/v1/identity/auth/password/forgot", {
      method: "POST",
      auth: false,
      body: JSON.stringify({ email: "student@example.edu" })
    });

    const headers = new Headers(fetchMock.mock.calls[0]?.[1]?.headers);
    expect(headers.get("Idempotency-Key")).toBeNull();
  });

  it("refreshes using the HttpOnly-cookie endpoint and stores only access token", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ access_token: "new-access" }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      })
    );

    expect(await refreshAccessToken()).toBe(true);
    expect(tokenStore.getAccessToken()).toBe("new-access");
    expect(tokenStore.getRefreshToken()).toBeNull();

    const init = fetchMock.mock.calls[0]?.[1];
    expect(init?.credentials).toBe("include");
    expect(new Headers(init?.headers).get("X-Requested-With")).toBe(
      "XMLHttpRequest"
    );
  });
});
