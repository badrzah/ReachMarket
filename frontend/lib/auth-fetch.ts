/**
 * Modern auth-aware fetch wrapper.
 *
 * Automatically attaches Bearer token, handles 401 → refresh → retry,
 * and queues concurrent requests during refresh so we don't hammer the
 * refresh endpoint. Drops in as a drop-in replacement for `fetch`.
 *
 * Usage:
 *   import { authFetch } from "@/lib/auth-fetch";
 *   const res = await authFetch("/api/v1/strategy/");
 *   const data = await res.json();
 */

type AuthFetchOptions = RequestInit & {
  /** Skip auth header — use for login/register */
  noAuth?: boolean;
};

let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

async function tryRefreshToken(): Promise<boolean> {
  if (isRefreshing && refreshPromise) return refreshPromise;

  isRefreshing = true;
  refreshPromise = (async () => {
    const base = "https://reachgtm-api-proxy.badrpcc.workers.dev";
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) return false;

    try {
      const res = await fetch(`${base}/api/v1/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (!res.ok) return false;
      const tokens = await res.json();
      localStorage.setItem("access_token", tokens.access_token);
      localStorage.setItem("refresh_token", tokens.refresh_token);
      return true;
    } catch {
      return false;
    } finally {
      isRefreshing = false;
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

export async function authFetch(
  input: URL | RequestInfo,
  options?: AuthFetchOptions
): Promise<Response> {
  const base = "https://reachgtm-api-proxy.badrpcc.workers.dev";
  const url = typeof input === "string" && input.startsWith("/")
    ? `${base}${input}`
    : input;

  const headers = new Headers(options?.headers);
  if (!options?.noAuth) {
    const token = localStorage.getItem("access_token");
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }

  let res = await fetch(url, { ...options, headers } as RequestInit);

  // On 401, try to refresh the token and retry once
  if (res.status === 401 && !options?.noAuth) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      const newToken = localStorage.getItem("access_token");
      const retryHeaders = new Headers(options?.headers);
      if (newToken) retryHeaders.set("Authorization", `Bearer ${newToken}`);
      res = await fetch(url, { ...options, headers: retryHeaders } as RequestInit);
    }
  }

  return res;
}

/**
 * Convenience: authFetch that parses JSON response.
 * Throws on non-ok status with the response body as the error message.
 */
export async function authFetchJSON<T = unknown>(
  input: URL | RequestInfo,
  options?: AuthFetchOptions
): Promise<T> {
  const res = await authFetch(input, options);
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`Request failed (${res.status}): ${body.slice(0, 200)}`);
  }
  return res.json();
}
