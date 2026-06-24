export const ACCESS_EMAIL_HEADERS = [
  "cf-access-authenticated-user-email",
  "x-forwarded-email",
] as const;

export function normalizeOwnerEmail(raw: string | null | undefined): string | null {
  const email = (raw ?? "").trim().toLowerCase();
  return email || null;
}

/** Resolve Cloudflare Access email from reverse-proxy headers or dev overrides. */
export function resolveMsosIdentityFromHeaders(headers: Headers): string | null {
  const envOverride =
    process.env.MSOS_IDENTITY_EMAIL?.trim() || process.env.PPE_OWNER_EMAIL?.trim();
  if (envOverride) {
    return normalizeOwnerEmail(envOverride);
  }
  for (const name of ACCESS_EMAIL_HEADERS) {
    const val = headers.get(name);
    const normalized = normalizeOwnerEmail(val);
    if (normalized) return normalized;
  }
  return null;
}

export function devAllowsAnonymousIdentity(): boolean {
  return process.env.MSOS_IDENTITY_DEV_ALLOW_ANON === "1";
}
