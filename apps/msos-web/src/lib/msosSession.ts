/** Browser session cookie — scopes workflow store when Cloudflare Access email is absent. */

export const MSOS_SESSION_COOKIE = "msos_session";

export function parseSessionFromCookieHeader(cookieHeader: string | null): string | null {
  if (!cookieHeader) return null;
  for (const part of cookieHeader.split(";")) {
    const [rawName, ...rest] = part.trim().split("=");
    if (rawName?.trim() === MSOS_SESSION_COOKIE) {
      const value = rest.join("=").trim();
      return value || null;
    }
  }
  return null;
}

export function scopeOwnerId(raw: string | null | undefined): string | null {
  const trimmed = (raw ?? "").trim();
  if (!trimmed) return null;
  if (trimmed.startsWith("session:")) return trimmed;
  return trimmed.toLowerCase();
}
