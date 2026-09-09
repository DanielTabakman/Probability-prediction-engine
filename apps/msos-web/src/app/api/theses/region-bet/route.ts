import { NextResponse } from "next/server";

import type { RegionBetContract } from "@/lib/regionBet";
import { requireProtectedIdentity } from "@/lib/msosIdentity";
import {
  getCurrentRegionBet,
  getRegionBetById,
  upsertRegionBet,
} from "@/lib/msosWorkflowStore";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const url = new URL(request.url);
    const regionBetId = url.searchParams.get("id")?.trim();
    const regionBet = regionBetId
      ? await getRegionBetById(identity.email, regionBetId)
      : await getCurrentRegionBet(identity.email);
    return NextResponse.json({ regionBet });
  } catch (err) {
    console.error("region-bet GET failed", err);
    return NextResponse.json({ error: "failed to load region bet" }, { status: 500 });
  }
}

export async function PUT(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const body = await request.json();
    const regionBet = body?.regionBet as RegionBetContract | undefined;
    if (!regionBet) {
      return NextResponse.json({ error: "missing region bet" }, { status: 400 });
    }
    const saved = await upsertRegionBet(regionBet, identity.email);
    return NextResponse.json({ regionBet: saved });
  } catch (err) {
    const message = err instanceof Error ? err.message : "failed to save region bet";
    const status = message.includes("invalid region bet") ? 400 : 500;
    console.error("region-bet PUT failed", err);
    return NextResponse.json({ error: message }, { status });
  }
}
