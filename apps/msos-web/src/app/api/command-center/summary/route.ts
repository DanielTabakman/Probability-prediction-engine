import { NextResponse } from "next/server";

import { loadCommandCenterSummary } from "@/lib/commandCenterSummary";
import { requireProtectedIdentity } from "@/lib/msosIdentity";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const summary = loadCommandCenterSummary(identity.email || null);
    return NextResponse.json(summary);
  } catch (err) {
    console.error("command-center summary GET failed", err);
    return NextResponse.json({ error: "failed to load command center summary" }, { status: 500 });
  }
}
