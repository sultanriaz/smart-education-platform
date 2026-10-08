import type { AppRole } from "./types";

export function hasAnyRole(userRoles: AppRole[], requiredRoles: AppRole[]) {
  if (requiredRoles.length === 0) return true;
  return requiredRoles.some((role) => userRoles.includes(role));
}

export function primaryRole(roles: AppRole[]): AppRole | null {
  if (roles.includes("admin")) return "admin";
  if (roles.includes("teacher")) return "teacher";
  if (roles.includes("student")) return "student";
  return null;
}
