/**
 * Post sign-in return path — sessionStorage fallback when Cloudflare Access ignores returnTo.
 */

export const POST_AUTH_RETURN_KEY = "msos.postAuthReturn.v1";

const RETURN_QUERY_KEYS = ["returnTo", "return_to", "redirect", "next"] as const;

function normalizeAppPath(path: string): string | null {
  const trimmed = path.trim();
  if (!trimmed.startsWith("/") || trimmed.startsWith("//")) {
    return null;
  }
  return trimmed;
}

export function stashPostAuthReturnPath(path: string): void {
  if (typeof window === "undefined") return;
  const normalized = normalizeAppPath(path.startsWith("/") ? path : `/${path}`);
  if (!normalized) return;
  try {
    window.sessionStorage.setItem(POST_AUTH_RETURN_KEY, normalized);
  } catch {
    /* ignore quota */
  }
}

export function parseReturnToFromSearch(search: string, origin: string): string | null {
  const params = new URLSearchParams(search);
  for (const key of RETURN_QUERY_KEYS) {
    const raw = params.get(key)?.trim();
    if (!raw) continue;
    if (raw.startsWith("/")) {
      return normalizeAppPath(raw);
    }
    try {
      const url = new URL(raw);
      if (url.origin === origin) {
        return normalizeAppPath(`${url.pathname}${url.search}`);
      }
    } catch {
      /* not a URL */
    }
  }
  return null;
}

export function peekPostAuthReturnPath(): string | null {
  if (typeof window === "undefined") return null;
  const fromUrl = parseReturnToFromSearch(window.location.search, window.location.origin);
  if (fromUrl) return fromUrl;
  try {
    const stored = window.sessionStorage.getItem(POST_AUTH_RETURN_KEY);
    return stored ? normalizeAppPath(stored) : null;
  } catch {
    return null;
  }
}

export function consumePostAuthReturnPath(): string | null {
  const target = peekPostAuthReturnPath();
  if (!target || typeof window === "undefined") return target;
  try {
    window.sessionStorage.removeItem(POST_AUTH_RETURN_KEY);
  } catch {
    /* ignore */
  }
  const url = new URL(window.location.href);
  let changed = false;
  for (const key of RETURN_QUERY_KEYS) {
    if (url.searchParams.has(key)) {
      url.searchParams.delete(key);
      changed = true;
    }
  }
  if (changed) {
    const next = `${url.pathname}${url.search}${url.hash}`;
    window.history.replaceState({}, "", next);
  }
  return target;
}

export function currentAppPath(): string {
  if (typeof window === "undefined") return "/";
  return `${window.location.pathname}${window.location.search}`;
}
