import { cookies, headers } from "next/headers";

import { devAllowsAnonymousIdentity, resolveMsosIdentityFromHeaders } from "@/lib/msosIdentity";
import { MSOS_SESSION_COOKIE, parseSessionFromCookieHeader } from "@/lib/msosSession";

/** Server components — email, session:uuid, or empty legacy anon bucket. */
export async function resolveWorkflowOwnerId(): Promise<string> {
  const requestHeaders = await headers();
  const email = resolveMsosIdentityFromHeaders(requestHeaders);
  if (email) return email;
  const cookieStore = await cookies();
  const session = cookieStore.get(MSOS_SESSION_COOKIE)?.value?.trim();
  if (session) return `session:${session}`;
  if (devAllowsAnonymousIdentity()) return "";
  return "";
}

export function resolveWorkflowOwnerFromRequest(request: Request): string | null {
  const email = resolveMsosIdentityFromHeaders(request.headers);
  if (email) return email;
  const session = parseSessionFromCookieHeader(request.headers.get("cookie"));
  if (session) return `session:${session}`;
  if (devAllowsAnonymousIdentity()) return "";
  return null;
}
