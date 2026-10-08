import {
  useCallback,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren
} from "react";

import { useQueryClient } from "@tanstack/react-query";
import { AuthContext, type AuthState } from "./useAuth";
import { refreshAccessToken } from "../../lib/api-client";
import { tokenStore } from "../../lib/token-store";
import {
  getCurrentUser,
  login as loginRequest,
  logout as logoutRequest
} from "./auth-api";
import type { AuthUser, LoginInput } from "./types";

const IDLE_TIMEOUT_MS = 10 * 60 * 1000;

export function AuthProvider({ children }: PropsWithChildren) {
  const queryClient = useQueryClient();
  const [state, setState] = useState<AuthState>("booting");
  const [user, setUser] = useState<AuthUser | null>(null);

  const clearSession = useCallback(() => {
    tokenStore.clear();
    void queryClient.cancelQueries();
    queryClient.clear();
    setUser(null);
    setState("anonymous");
  }, [queryClient]);

  const reloadUser = useCallback(async () => {
    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
      setState("authenticated");
    } catch (error) {
      clearSession();
      throw error;
    }
  }, [clearSession]);

  useEffect(() => {
    let cancelled = false;

    const bootstrap = async () => {
      if (!tokenStore.getAccessToken()) {
        const refreshed = await refreshAccessToken();
        if (!refreshed) {
          if (!cancelled) setState("anonymous");
          return;
        }
      }
      if (!cancelled) await reloadUser();
    };

    void bootstrap().catch(() => { if (!cancelled) clearSession(); });
    return () => {
      cancelled = true;
    };
  }, [reloadUser, clearSession]);

  const login = useCallback(
    async (input: LoginInput) => {
      clearSession();
      const tokens = await loginRequest(input);
      tokenStore.setAccessToken(tokens.accessToken);
      await reloadUser();
    },
    [reloadUser, clearSession]
  );

  useEffect(() => tokenStore.onClear(clearSession), [clearSession]);

  const logout = useCallback(async () => {
    try {
      await logoutRequest();
    } finally {
      clearSession();
    }
  }, [clearSession]);

  useEffect(() => {
    if (state !== "authenticated") return;

    let timer = window.setTimeout(() => {
      void logout();
    }, IDLE_TIMEOUT_MS);

    const reset = () => {
      window.clearTimeout(timer);
      timer = window.setTimeout(() => {
        void logout();
      }, IDLE_TIMEOUT_MS);
    };

    const events: Array<keyof WindowEventMap> = [
      "pointerdown",
      "keydown",
      "scroll",
      "touchstart"
    ];
    events.forEach((event) =>
      window.addEventListener(event, reset, { passive: true })
    );

    return () => {
      window.clearTimeout(timer);
      events.forEach((event) => window.removeEventListener(event, reset));
    };
  }, [state, logout]);

  const value = useMemo(
    () => ({ state, user, login, logout, reloadUser }),
    [state, user, login, logout, reloadUser]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

