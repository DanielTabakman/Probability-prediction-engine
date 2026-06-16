import { NextResponse } from "next/server";

import { loadWorkflowSummary } from "@/lib/msosWorkflowStore";

export const runtime = "nodejs";

export async function GET() {
  try {
    const summary = await loadWorkflowSummary();
    return NextResponse.json(summary);
  } catch (err) {
    console.error("theses summary GET failed", err);
    return NextResponse.json({ error: "failed to load workflow summary" }, { status: 500 });
  }
}
