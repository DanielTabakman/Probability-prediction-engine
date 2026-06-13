import { NextResponse } from "next/server";

import { appendFeedback, validateSubmitPayload } from "@/lib/webFeedbackStore";

export const runtime = "nodejs";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const payload = validateSubmitPayload(body);
    const entry = appendFeedback(payload);
    return NextResponse.json({ ok: true, id: entry.id }, { status: 201 });
  } catch (err) {
    const message = err instanceof Error ? err.message : "invalid request";
    return NextResponse.json({ ok: false, error: message }, { status: 400 });
  }
}
