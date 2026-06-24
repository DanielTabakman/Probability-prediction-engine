import { NextResponse } from "next/server";

import { devAllowsAnonymousIdentity, resolveMsosIdentityFromHeaders } from "@/lib/msosIdentityCore";
import { MSOS_SESSION_COOKIE, parseSessionFromCookieHeader } from "@/lib/msosSession";

/** Route handlers — email, session:uuid, legacy anon, or null (401). */
export function resolveWorkflowOwnerFromRequest(request: Request): string | null {
  const email = resolveMsosIdentityFromHeaders(request.headers);
  if (email) return email;
  const session = parseSessionFromCookieHeader(request.headers.get("cookie"));
  if (session) return `session:${session}`;
  if (devAllowsAnonymousIdentity()) return "";
  return null;
}

export function requireProtectedIdentity(
  request: Request,
): { ok: true; email: string } | { ok: false; response: NextResponse } {
  const owner = resolveWorkflowOwnerFromRequest(request);
  if (owner !== null) {
    return { ok: true, email: owner };
  }
  return {
    ok: false,
    response: NextResponse.json({ error: "authentication required" }, { status: 401 }),
  };
}

export type MsosIdentityResult = ReturnType<typeof requireProtectedIdentity>;
