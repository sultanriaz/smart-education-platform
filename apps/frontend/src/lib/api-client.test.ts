import { afterEach, describe, expect, it, vi } from "vitest";
import { apiRequest } from "./api-client";
import { tokenStore } from "./token-store";

afterEach(() => vi.unstubAllGlobals());

describe("apiRequest", () => {
  it("adds bearer token", async () => {
    tokenStore.setAccessToken("access-token");
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      })
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await apiRequest<{ ok: boolean }>("/api/v1/platform/features");
    expect(result.ok).toBe(true);

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(new Headers(init.headers).get("Authorization")).toBe("Bearer access-token");
  });

  it("surfaces API errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: "Forbidden" }), {
          status: 403,
          headers: { "Content-Type": "application/json" }
        })
      )
    );

    await expect(
      apiRequest("/api/v1/platform/admin/audit", { auth: false })
    ).rejects.toThrow("Forbidden");
  });
});
