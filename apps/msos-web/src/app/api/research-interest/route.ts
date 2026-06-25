import { NextResponse } from "next/server";

import { appendWebFeedback } from "@/lib/webFeedback";

export const runtime = "nodejs";

function asTrimmed(value: unknown, max = 500): string | undefined {
  if (typeof value !== "string") return undefined;
  const trimmed = value.trim();
  if (!trimmed) return undefined;
  return trimmed.length > max ? trimmed.slice(0, max) : trimmed;
}

/** Public research-beta interest — no auth required on demo homepage. */
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const email = asTrimmed(body?.email, 200);
    const note = asTrimmed(body?.note, 2000);
    if (!email && !note) {
      return NextResponse.json({ error: "email or note required" }, { status: 400 });
    }

    const record = await appendWebFeedback({
      source: "research_beta_request",
      session_note: email ? `email: ${email}` : undefined,
      objections_text: note,
      confusion_category: "feature request / later-scope item",
      usefulness: 4,
      repeat_use_intent: 4,
    });

    return NextResponse.json({ ok: true, id: record.id });
  } catch (err) {
    console.error("research-interest POST failed", err);
    return NextResponse.json({ error: "failed to save request" }, { status: 500 });
  }
}
