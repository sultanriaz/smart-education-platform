let accessToken: string | null = null;
const clearListeners = new Set<() => void>();

/**
 * Sprint 18 deliberately keeps the access token in process memory only.
 *
 * The refresh token is owned by Identity and stored in a Secure, HttpOnly,
 * SameSite=Strict cookie scoped to /api/v1/identity/auth. Browser JavaScript
 * cannot read it.
 */
export const tokenStore = {
  getAccessToken: () => accessToken,

  setAccessToken(value: string) {
    accessToken = value;
  },

  // Compatibility shim for older call sites. The refresh token argument is
  // intentionally ignored and never written to Web Storage.
  setTokens(value: string, _refreshToken?: string | null) {
    void _refreshToken;
    accessToken = value;
  },

  // Refresh tokens are no longer JavaScript-readable.
  getRefreshToken: () => null,

  onClear(listener: () => void) {
    clearListeners.add(listener);
    return () => { clearListeners.delete(listener); };
  },

  clear() {
    const hadToken = accessToken !== null;
    accessToken = null;
    // Notify once; listeners may themselves clear an already empty session.
    if (hadToken) clearListeners.forEach((listener) => listener());
  }
};
