import { NextResponse } from "next/server";

import { requireProtectedIdentity } from "@/lib/msosIdentity";
import { loadWorkflowSummary } from "@/lib/msosWorkflowStore";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const summary = await loadWorkflowSummary(identity.email);
    return NextResponse.json(summary);
  } catch (err) {
    console.error("theses summary GET failed", err);
    return NextResponse.json({ error: "failed to load workflow summary" }, { status: 500 });
  }
}
