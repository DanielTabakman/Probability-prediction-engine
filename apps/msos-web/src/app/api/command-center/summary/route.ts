import { NextResponse } from "next/server";

import { loadCommandCenterSummary } from "@/lib/commandCenterSummary";

export const runtime = "nodejs";

export async function GET() {
  try {
    const summary = loadCommandCenterSummary();
    return NextResponse.json(summary);
  } catch (err) {
    console.error("command-center summary GET failed", err);
    return NextResponse.json(
      {
        status: "degraded",
        reason: "Failed to load snapshot summary.",
        sourceLabel: "From PPE snapshots",
        kpis: [],
        currentWork: [],
      },
      { status: 500 },
    );
  }
}
