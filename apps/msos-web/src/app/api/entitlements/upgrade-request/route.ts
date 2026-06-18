import { NextResponse } from "next/server";

import { appendUpgradeRequest, getOrCreateEntitlement } from "@/lib/msosEntitlements";
import { requireProtectedIdentity } from "@/lib/msosIdentity";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  let note = "";
  try {
    const body = (await request.json()) as { note?: string };
    note = typeof body.note === "string" ? body.note : "";
  } catch {
    note = "";
  }
  try {
    getOrCreateEntitlement(identity.email);
    appendUpgradeRequest(identity.email, note);
    return NextResponse.json({ ok: true, logged: true });
  } catch (err) {
    console.error("entitlements upgrade-request POST failed", err);
    return NextResponse.json({ error: "failed to log upgrade request" }, { status: 500 });
  }
}
