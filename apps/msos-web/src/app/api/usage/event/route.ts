import { NextResponse } from "next/server";

import { appendProductUsageEvent } from "@/lib/webProductUsage";

export const runtime = "nodejs";

function asTrimmed(value: unknown, max = 4000): string | undefined {
  if (typeof value !== "string") return undefined;
  const trimmed = value.trim();
  if (!trimmed) return undefined;
  return trimmed.length > max ? trimmed.slice(0, max) : trimmed;
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const eventName = asTrimmed(body?.event_name, 120);
    if (!eventName) {
      return NextResponse.json({ error: "event_name required" }, { status: 400 });
    }

    const record = await appendProductUsageEvent({
      event_name: eventName,
      source: asTrimmed(body?.source, 80) || "msos-web",
      path: asTrimmed(body?.path, 500),
      asset_id: asTrimmed(body?.asset_id, 32),
      snapshot_id: asTrimmed(body?.snapshot_id, 120),
      owner_email: asTrimmed(body?.owner_email, 200),
      review_status: asTrimmed(body?.review_status, 64),
    });

    return NextResponse.json({ ok: true, id: record.id });
  } catch (err) {
    console.error("usage event POST failed", err);
    return NextResponse.json({ error: "failed to save usage event" }, { status: 500 });
  }
}
