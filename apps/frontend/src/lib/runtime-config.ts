const trimTrailingSlash = (value: string) => value.replace(/\/+$/, "");

export const runtimeConfig = {
  apiBaseUrl: trimTrailingSlash(
    window.__APP_CONFIG__?.API_BASE_URL ??
      import.meta.env.VITE_API_BASE_URL ??
      "http://localhost:8080"
  ),
  appName:
    window.__APP_CONFIG__?.APP_NAME ??
    import.meta.env.VITE_APP_NAME ??
    "Smart Education Platform"
};
