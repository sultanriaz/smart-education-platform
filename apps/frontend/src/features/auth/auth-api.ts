import { apiRequest } from "../../lib/api-client";
import { normalizeTokenPair, normalizeUser } from "./normalizers";
import type { AuthUser, LoginInput, RegisterInput, TokenPair } from "./types";

export async function login(input: LoginInput): Promise<TokenPair> {
  const payload = await apiRequest<Record<string, unknown>>(
    "/api/v1/identity/auth/login",
    {
      method: "POST",
      auth: false,
      retryOnUnauthorized: false,
      credentials: "include",
      body: JSON.stringify(input)
    }
  );
  return normalizeTokenPair(payload);
}

export async function register(input: RegisterInput): Promise<AuthUser> {
  const payload = await apiRequest<Record<string, unknown>>(
    "/api/v1/identity/auth/register",
    {
      method: "POST",
      auth: false,
      retryOnUnauthorized: false,
      body: JSON.stringify(input)
    }
  );
  return normalizeUser(payload);
}

export async function getCurrentUser(): Promise<AuthUser> {
  const payload = await apiRequest<Record<string, unknown>>(
    "/api/v1/identity/users/me"
  );
  return normalizeUser(payload);
}

export async function logout(): Promise<void> {
  await apiRequest<void>("/api/v1/identity/auth/logout", {
    method: "POST",
    retryOnUnauthorized: false,
    credentials: "include",
    body: "{}"
  });
}

export async function requestPasswordReset(email: string): Promise<void> {
  await apiRequest("/api/v1/identity/auth/password/forgot", {
    method: "POST",
    auth: false,
    retryOnUnauthorized: false,
    body: JSON.stringify({ email })
  });
}

export async function resetPassword(
  token: string,
  newPassword: string
): Promise<void> {
  await apiRequest("/api/v1/identity/auth/password/reset", {
    method: "POST",
    auth: false,
    retryOnUnauthorized: false,
    body: JSON.stringify({
      token,
      new_password: newPassword
    })
  });
}

export async function requestEmailVerification(email: string): Promise<void> {
  await apiRequest("/api/v1/identity/auth/email/verification/request", {
    method: "POST",
    auth: false,
    retryOnUnauthorized: false,
    body: JSON.stringify({ email })
  });
}

export async function confirmEmailVerification(token: string): Promise<void> {
  await apiRequest("/api/v1/identity/auth/email/verification/confirm", {
    method: "POST",
    auth: false,
    retryOnUnauthorized: false,
    body: JSON.stringify({ token })
  });
}
