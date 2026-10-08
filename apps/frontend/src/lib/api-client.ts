import { runtimeConfig } from "./runtime-config";
import { tokenStore } from "./token-store";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly body?: unknown,
    public readonly requestId?: string | null,
    public readonly correlationId?: string | null
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type RequestOptions = RequestInit & {
  auth?: boolean;
  retryOnUnauthorized?: boolean;
  idempotencyKey?: string;
};

const mutatingMethods = new Set(["POST", "PUT", "PATCH", "DELETE"]);
const idempotencyExcludedPathPrefixes = [
  "/api/v1/identity/auth/login",
  "/api/v1/identity/auth/refresh",
  "/api/v1/identity/auth/logout",
  "/api/v1/identity/auth/password/",
  "/api/v1/identity/auth/email/verification/"
];

function shouldAutoIdempotencyKey(path: string, options: RequestOptions) {
  const method = (options.method ?? "GET").toUpperCase();
  if (!mutatingMethods.has(method)) return false;
  if (options.body instanceof FormData) return false;
  return !idempotencyExcludedPathPrefixes.some((prefix) =>
    path.startsWith(prefix)
  );
}

let refreshPromise: Promise<boolean> | null = null;

function newIdempotencyKey() {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `web-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

async function parseBody(response: Response) {
  if (response.status === 204) return null;
  const contentType = response.headers.get("content-type") ?? "";
  return contentType.includes("application/json")
    ? response.json()
    : response.text();
}

export async function refreshAccessToken(): Promise<boolean> {
  if (!refreshPromise) {
    refreshPromise = (async () => {
      try {
        const response = await fetch(
          `${runtimeConfig.apiBaseUrl}/api/v1/identity/auth/refresh`,
          {
            method: "POST",
            credentials: "include",
            headers: {
              "Content-Type": "application/json",
              "X-Requested-With": "XMLHttpRequest"
            },
            body: "{}",
            cache: "no-store",
            signal: AbortSignal.timeout(5_000)
          }
        );

        if (!response.ok) {
          tokenStore.clear();
          return false;
        }

        const body = (await response.json()) as Record<string, unknown>;
        const access =
          typeof body.access_token === "string"
            ? body.access_token
            : typeof body.accessToken === "string"
              ? body.accessToken
              : null;

        if (!access) {
          tokenStore.clear();
          return false;
        }

        tokenStore.setAccessToken(access);
        return true;
      } catch {
        tokenStore.clear();
        return false;
      } finally {
        refreshPromise = null;
      }
    })();
  }

  return refreshPromise;
}

function authenticatedHeaders(headersInit?: HeadersInit, auth = true) {
  const headers = new Headers(headersInit);
  if (auth) {
    const accessToken = tokenStore.getAccessToken();
    if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
  }
  return headers;
}

function prepareHeaders(
  path: string,
  options: RequestOptions,
  auth: boolean
): Headers {
  const headers = authenticatedHeaders(options.headers, auth);
  if (
    !headers.has("Content-Type") &&
    options.body &&
    !(options.body instanceof FormData)
  ) {
    headers.set("Content-Type", "application/json");
  }

  if (
    shouldAutoIdempotencyKey(path, options) &&
    !headers.has("Idempotency-Key")
  ) {
    headers.set(
      "Idempotency-Key",
      options.idempotencyKey ?? newIdempotencyKey()
    );
  }

  return headers;
}

async function throwApiError(response: Response, body: unknown): Promise<never> {
  let message = `Request failed with status ${response.status}`;

  if (body && typeof body === "object") {
    const detail = (body as { detail?: unknown }).detail;
    const gatewayError = (
      body as {
        error?: {
          message?: unknown;
          request_id?: unknown;
          correlation_id?: unknown;
        };
      }
    ).error;

    if (typeof detail === "string") message = detail;
    if (typeof gatewayError?.message === "string") {
      message = gatewayError.message;
    }
  }

  const requestId =
    response.headers.get("X-Request-ID") ??
    (body && typeof body === "object"
      ? String(
          (body as { error?: { request_id?: unknown } }).error?.request_id ?? ""
        ) || null
      : null);

  const correlationId =
    response.headers.get("X-Correlation-ID") ??
    (body && typeof body === "object"
      ? String(
          (body as { error?: { correlation_id?: unknown } }).error?.correlation_id ?? ""
        ) || null
      : null);

  throw new ApiError(
    response.status,
    message,
    body,
    requestId,
    correlationId
  );
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const auth = options.auth ?? true;
  const retryOnUnauthorized = options.retryOnUnauthorized ?? true;
  const headers = prepareHeaders(path, options, auth);

  const response = await fetch(`${runtimeConfig.apiBaseUrl}${path}`, {
    ...options,
    signal: options.signal ? AbortSignal.any([options.signal, AbortSignal.timeout(15_000)]) : AbortSignal.timeout(15_000),
    headers,
    credentials: options.credentials ?? "include",
    cache: options.cache ?? "no-store"
  });

  if (response.status === 401 && auth && retryOnUnauthorized) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      return apiRequest<T>(path, {
        ...options,
        headers,
        retryOnUnauthorized: false
      });
    }
  }

  const body = await parseBody(response);
  if (!response.ok) await throwApiError(response, body);
  return body as T;
}

export async function apiDownload(
  path: string,
  retryOnUnauthorized = true
): Promise<{ blob: Blob; filename?: string }> {
  const response = await fetch(`${runtimeConfig.apiBaseUrl}${path}`, {
    credentials: "include",
    cache: "no-store",
    signal: AbortSignal.timeout(30_000),
    headers: authenticatedHeaders(undefined, true)
  });

  if (response.status === 401 && retryOnUnauthorized) {
    const refreshed = await refreshAccessToken();
    if (refreshed) return apiDownload(path, false);
  }

  if (!response.ok) {
    const body = await parseBody(response);
    await throwApiError(response, body);
  }

  const disposition = response.headers.get("content-disposition") ?? "";
  const match = disposition.match(/filename="?([^";]+)"?/i);

  return {
    blob: await response.blob(),
    filename: match?.[1]
  };
}
