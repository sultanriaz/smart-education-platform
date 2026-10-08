import { beforeEach, describe, expect, it, vi } from "vitest";

import { apiRequest } from "./api-client";
import { tokenStore } from "./token-store";

describe("Sprint 16 API client idempotency", () => {
  beforeEach(() => {
    tokenStore.clear();
    vi.restoreAllMocks();
  });

  it("adds an Idempotency-Key to mutating requests", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      })
    );

    await apiRequest("/api/v1/platform/test", {
      method: "POST",
      auth: false,
      body: JSON.stringify({ value: 1 })
    });

    const requestInit = fetchMock.mock.calls[0]?.[1];
    const headers = new Headers(requestInit?.headers);
    expect(headers.get("Idempotency-Key")).toBeTruthy();
  });

  it("does not add an Idempotency-Key to GET requests", async () => {
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

    const requestInit = fetchMock.mock.calls[0]?.[1];
    const headers = new Headers(requestInit?.headers);
    expect(headers.get("Idempotency-Key")).toBeNull();
  });

  it("does not cache sensitive login token responses", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ access_token: "x", refresh_token: "y" }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      })
    );

    await apiRequest("/api/v1/identity/auth/login", {
      method: "POST",
      auth: false,
      body: JSON.stringify({ email: "user@example.edu", password: "secret" })
    });

    const requestInit = fetchMock.mock.calls[0]?.[1];
    const headers = new Headers(requestInit?.headers);
    expect(headers.get("Idempotency-Key")).toBeNull();
  });

});
