import { NextResponse } from "next/server";

import { requireProtectedIdentity } from "@/lib/msosIdentity";
import {
  closePaperTrade,
  deletePaperTrade,
  getPaperTradeById,
} from "@/lib/msosWorkflowStore";

export const runtime = "nodejs";

type RouteContext = { params: Promise<{ id: string }> };

export async function GET(request: Request, context: RouteContext) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  const { id } = await context.params;
  try {
    const trade = await getPaperTradeById(identity.email, id);
    if (!trade) {
      return NextResponse.json({ error: "paper trade not found" }, { status: 404 });
    }
    return NextResponse.json({ expression: trade });
  } catch (err) {
    console.error("paper-trades GET by id failed", err);
    return NextResponse.json({ error: "failed to load paper trade" }, { status: 500 });
  }
}

export async function DELETE(request: Request, context: RouteContext) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  const { id } = await context.params;
  try {
    const removed = await deletePaperTrade(identity.email, id);
    if (!removed) {
      return NextResponse.json({ error: "paper trade not found" }, { status: 404 });
    }
    return NextResponse.json({ ok: true });
  } catch (err) {
    console.error("paper-trades DELETE failed", err);
    return NextResponse.json({ error: "failed to delete paper trade" }, { status: 500 });
  }
}

export async function PATCH(request: Request, context: RouteContext) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  const { id } = await context.params;
  try {
    const body = await request.json();
    const action = String(body?.action ?? "").trim().toLowerCase();
    if (action !== "close") {
      return NextResponse.json({ error: "unsupported action" }, { status: 400 });
    }
    const closed = await closePaperTrade(identity.email, id);
    if (!closed) {
      return NextResponse.json({ error: "paper trade not found" }, { status: 404 });
    }
    return NextResponse.json({ expression: closed });
  } catch (err) {
    console.error("paper-trades PATCH failed", err);
    return NextResponse.json({ error: "failed to update paper trade" }, { status: 500 });
  }
}
