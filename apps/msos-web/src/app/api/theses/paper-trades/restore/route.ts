import { NextResponse } from "next/server";

import type { StoredExpression } from "@/lib/msosWorkflowStore";
import { requireProtectedIdentity } from "@/lib/msosIdentity";
import { restorePaperTrade } from "@/lib/msosWorkflowStore";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const body = await request.json();
    const expression = body?.expression as StoredExpression | undefined;
    if (!expression?.id || !expression.thesisId) {
      return NextResponse.json({ error: "missing expression" }, { status: 400 });
    }
    const restored = await restorePaperTrade(identity.email, expression);
    if (!restored) {
      return NextResponse.json({ error: "could not restore paper trade" }, { status: 400 });
    }
    return NextResponse.json({ expression: restored });
  } catch (err) {
    console.error("paper-trades restore POST failed", err);
    return NextResponse.json({ error: "failed to restore paper trade" }, { status: 500 });
  }
}
