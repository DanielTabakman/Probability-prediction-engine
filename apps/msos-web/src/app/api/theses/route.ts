import { NextResponse } from "next/server";

import type { ThesisRecord } from "@/lib/thesisPersistence";
import { requireProtectedIdentity } from "@/lib/msosIdentity";
import { getCurrentThesis, upsertCurrentThesis } from "@/lib/msosWorkflowStore";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const thesis = await getCurrentThesis(identity.email);
    return NextResponse.json({ thesis });
  } catch (err) {
    console.error("theses GET failed", err);
    return NextResponse.json({ error: "failed to load thesis" }, { status: 500 });
  }
}

export async function PUT(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const body = await request.json();
    const thesis = body?.thesis as ThesisRecord | undefined;
    const linkedSnapshotId =
      typeof body?.linkedSnapshotId === "string" ? body.linkedSnapshotId : null;
    if (!thesis) {
      return NextResponse.json({ error: "missing thesis" }, { status: 400 });
    }
    const saved = await upsertCurrentThesis(thesis, identity.email, linkedSnapshotId);
    return NextResponse.json({ thesis: saved });
  } catch (err) {
    console.error("theses PUT failed", err);
    return NextResponse.json({ error: "failed to save thesis" }, { status: 500 });
  }
}
