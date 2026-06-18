import { NextResponse } from "next/server";

import { loadHistoryFeed } from "@/lib/monitorHistoryFeed";
import { requireProtectedIdentity } from "@/lib/msosIdentity";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const feed = await loadHistoryFeed(identity.email || null);
    return NextResponse.json(feed);
  } catch (err) {
    console.error("history feed GET failed", err);
    return NextResponse.json({ error: "failed to load history feed" }, { status: 500 });
  }
}
