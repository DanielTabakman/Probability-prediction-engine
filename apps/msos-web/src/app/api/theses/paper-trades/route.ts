import { NextResponse } from "next/server";

import type { ExpressionRecord } from "@/lib/expressionPersistence";
import { requireProtectedIdentity } from "@/lib/msosIdentity";
import { appendPaperTrade, clearPaperTrades, listPaperTrades } from "@/lib/msosWorkflowStore";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const paperTrades = await listPaperTrades(identity.email);
    return NextResponse.json({ paperTrades });
  } catch (err) {
    console.error("paper-trades GET failed", err);
    return NextResponse.json({ error: "failed to load paper trades" }, { status: 500 });
  }
}

export async function POST(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const body = await request.json();
    const expression = body?.expression as ExpressionRecord | undefined;
    if (!expression) {
      return NextResponse.json({ error: "missing expression" }, { status: 400 });
    }
    const saved = await appendPaperTrade(
      { ...expression, lifecycle: "simulated" },
      identity.email,
    );
    return NextResponse.json({ expression: saved });
  } catch (err) {
    const message = err instanceof Error ? err.message : "failed to save paper trade";
    const status =
      message.includes("confirm a thesis") || message.includes("simulated lifecycle") ? 400 : 500;
    console.error("paper-trades POST failed", err);
    return NextResponse.json({ error: message }, { status });
  }
}

export async function DELETE(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const removed = await clearPaperTrades(identity.email);
    return NextResponse.json({ removed });
  } catch (err) {
    console.error("paper-trades DELETE all failed", err);
    return NextResponse.json({ error: "failed to clear paper trades" }, { status: 500 });
  }
}
