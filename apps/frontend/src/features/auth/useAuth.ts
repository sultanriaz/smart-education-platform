import { createContext, useContext } from "react";
import type { AppRole, AuthUser, LoginInput } from "./types";

export type AuthState = "booting" | "authenticated" | "anonymous";

export type AuthContextValue = {
  state: AuthState;
  user: AuthUser | null;
  login: (input: LoginInput, requiredRole?: AppRole) => Promise<void>;
  logout: () => Promise<void>;
  reloadUser: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextValue | null>(null);

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider.");
  return value;
}
