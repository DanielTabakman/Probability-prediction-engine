import { NextResponse } from "next/server";

import {
  applyLemonSqueezyWebhook,
  parseLemonSqueezyWebhook,
  verifyLemonSqueezySignature,
} from "@/lib/lemonSqueezyWebhook";

export const runtime = "nodejs";

export async function POST(request: Request) {
  const secret = process.env.LEMONSQUEEZY_WEBHOOK_SECRET?.trim();
  if (!secret) {
    return NextResponse.json({ error: "webhook not configured" }, { status: 503 });
  }

  const rawBody = await request.text();
  const signature = request.headers.get("X-Signature");

  if (!verifyLemonSqueezySignature(rawBody, signature, secret)) {
    return NextResponse.json({ error: "invalid signature" }, { status: 400 });
  }

  const payload = parseLemonSqueezyWebhook(rawBody);
  if (!payload) {
    return NextResponse.json({ error: "invalid payload" }, { status: 400 });
  }

  const result = applyLemonSqueezyWebhook(payload);
  if (!result.ok) {
    if (result.reason.startsWith("ignored event")) {
      return NextResponse.json({ ok: true, ignored: result.reason });
    }
    console.warn("lemon-squeezy webhook apply failed", result.reason, payload.meta.event_name);
    return NextResponse.json({ error: result.reason }, { status: 422 });
  }

  console.info(
    "lemon-squeezy webhook applied",
    result.eventName,
    result.email,
    result.tier,
  );
  return NextResponse.json({ ok: true, email: result.email, tier: result.tier });
}
