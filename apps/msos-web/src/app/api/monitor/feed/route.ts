import { NextResponse } from "next/server";

import { loadMonitorFeed } from "@/lib/monitorHistoryFeed";
import { requireProtectedIdentity } from "@/lib/msosIdentity";

export const runtime = "nodejs";

export async function GET(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const feed = await loadMonitorFeed(identity.email);
    return NextResponse.json(feed);
  } catch (err) {
    console.error("monitor feed GET failed", err);
    return NextResponse.json({ error: "failed to load monitor feed" }, { status: 500 });
  }
}
