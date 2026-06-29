import { NextResponse } from "next/server";

import type { HorizonRegionIntent } from "@/lib/horizonRegion";
import { requireProtectedIdentity } from "@/lib/msosIdentity";
import {
  getCurrentHorizonRegion,
  getHorizonRegionById,
  upsertHorizonRegion,
} from "@/lib/msosWorkflowStore";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const url = new URL(request.url);
    const regionId = url.searchParams.get("id")?.trim();
    const region = regionId
      ? await getHorizonRegionById(identity.email, regionId)
      : await getCurrentHorizonRegion(identity.email);
    return NextResponse.json({ region });
  } catch (err) {
    console.error("horizon-region GET failed", err);
    return NextResponse.json({ error: "failed to load horizon region" }, { status: 500 });
  }
}

export async function PUT(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const body = await request.json();
    const region = body?.region as HorizonRegionIntent | undefined;
    if (!region) {
      return NextResponse.json({ error: "missing region" }, { status: 400 });
    }
    const saved = await upsertHorizonRegion(region, identity.email);
    return NextResponse.json({ region: saved });
  } catch (err) {
    const message = err instanceof Error ? err.message : "failed to save horizon region";
    const status = message.includes("invalid horizon region") ? 400 : 500;
    console.error("horizon-region PUT failed", err);
    return NextResponse.json({ error: message }, { status });
  }
}
