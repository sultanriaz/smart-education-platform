import type { AppRole, AuthUser, TokenPair } from "./types";

const allowedRoles = new Set<AppRole>(["student", "teacher", "admin"]);

function normalizeRoles(value: unknown): AppRole[] {
  if (!Array.isArray(value)) return [];
  const roles = value
    .map((item) => {
      if (typeof item === "string") return item.toLowerCase();
      if (
        item &&
        typeof item === "object" &&
        "name" in item &&
        typeof (item as { name?: unknown }).name === "string"
      ) {
        return (item as { name: string }).name.toLowerCase();
      }
      return "";
    })
    .filter((role): role is AppRole => allowedRoles.has(role as AppRole));
  return Array.from(new Set(roles));
}

export function normalizeUser(payload: Record<string, unknown>): AuthUser {
  const rawId = payload.id ?? payload.user_id ?? payload.sub;
  if (typeof rawId !== "string") {
    throw new Error("Identity response does not contain a user identifier.");
  }

  return {
    id: rawId,
    email: typeof payload.email === "string" ? payload.email : undefined,
    fullName:
      typeof payload.full_name === "string"
        ? payload.full_name
        : typeof payload.fullName === "string"
          ? payload.fullName
          : typeof payload.name === "string"
            ? payload.name
            : undefined,
    roles: normalizeRoles(payload.roles)
  };
}

export function normalizeTokenPair(payload: Record<string, unknown>): TokenPair {
  const access =
    typeof payload.access_token === "string"
      ? payload.access_token
      : typeof payload.accessToken === "string"
        ? payload.accessToken
        : null;

  const refresh =
    typeof payload.refresh_token === "string"
      ? payload.refresh_token
      : typeof payload.refreshToken === "string"
        ? payload.refreshToken
        : null;

  if (!access) throw new Error("Identity response does not contain an access token.");

  return { accessToken: access, refreshToken: refresh };
}
