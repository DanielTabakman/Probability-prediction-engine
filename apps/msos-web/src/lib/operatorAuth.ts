import { normalizeOwnerEmail } from "@/lib/msosIdentityCore";

/** Comma-separated allowlist — Cloudflare Access email(s) for operator-only pages. */
export function resolveOperatorEmails(): Set<string> {
  const raw = process.env.MSOS_OPERATOR_EMAIL?.trim() ?? "";
  if (!raw) return new Set();
  return new Set(
    raw
      .split(",")
      .map((part) => normalizeOwnerEmail(part))
      .filter((email): email is string => Boolean(email)),
  );
}

export function operatorDevBypassEnabled(): boolean {
  return process.env.MSOS_OPERATOR_DEV_ALLOW === "1";
}

export function isOperatorIdentity(email: string | null): boolean {
  const normalized = normalizeOwnerEmail(email);
  if (!normalized) {
    return operatorDevBypassEnabled();
  }
  const allowed = resolveOperatorEmails();
  if (allowed.size === 0) {
    return operatorDevBypassEnabled();
  }
  return allowed.has(normalized);
}
