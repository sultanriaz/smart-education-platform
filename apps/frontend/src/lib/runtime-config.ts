const trimTrailingSlash = (value: string) => value.replace(/\/+$/, "");

const resolveApiBaseUrl = (): string => {
  // 1. Build-time Vite env var (configured in Vercel project environment variables)
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl && typeof envUrl === "string" && envUrl.trim()) {
    return trimTrailingSlash(envUrl.trim());
  }

  // 2. Runtime config injected via window.__APP_CONFIG__ (e.g. from /runtime-config.js)
  const windowUrl = window.__APP_CONFIG__?.API_BASE_URL;
  if (windowUrl && typeof windowUrl === "string" && windowUrl.trim()) {
    // When running in production on Vercel or cloud domain (non-localhost), don't use localhost!
    const isRemote =
      typeof window !== "undefined" &&
      window.location.hostname !== "localhost" &&
      window.location.hostname !== "127.0.0.1";

    if (isRemote && (windowUrl.includes("localhost") || windowUrl.includes("127.0.0.1"))) {
      // In cloud, default to same-origin relative path so Vercel rewrites proxy it
      return "";
    }
    return trimTrailingSlash(windowUrl.trim());
  }

  // 3. Remote cloud fallback (non-localhost): same-origin relative URL
  if (
    typeof window !== "undefined" &&
    window.location.hostname !== "localhost" &&
    window.location.hostname !== "127.0.0.1"
  ) {
    return "";
  }

  // 4. Local development default
  return "http://localhost:18080";
};

export const runtimeConfig = {
  apiBaseUrl: resolveApiBaseUrl(),
  appName:
    window.__APP_CONFIG__?.APP_NAME ??
    import.meta.env.VITE_APP_NAME ??
    "Smart Education Platform"
};
