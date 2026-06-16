import { NextResponse } from "next/server";

import type { ExpressionRecord } from "@/lib/expressionPersistence";
import { getCurrentExpression, upsertCurrentExpression } from "@/lib/msosWorkflowStore";

export const runtime = "nodejs";

export async function GET() {
  try {
    const expression = await getCurrentExpression();
    return NextResponse.json({ expression });
  } catch (err) {
    console.error("expression GET failed", err);
    return NextResponse.json({ error: "failed to load expression" }, { status: 500 });
  }
}

export async function PUT(request: Request) {
  try {
    const body = await request.json();
    const expression = body?.expression as ExpressionRecord | undefined;
    if (!expression) {
      return NextResponse.json({ error: "missing expression" }, { status: 400 });
    }
    const saved = await upsertCurrentExpression(expression);
    return NextResponse.json({ expression: saved });
  } catch (err) {
    const message = err instanceof Error ? err.message : "failed to save expression";
    const status = message.includes("confirm a thesis") ? 400 : 500;
    console.error("expression PUT failed", err);
    return NextResponse.json({ error: message }, { status });
  }
}
