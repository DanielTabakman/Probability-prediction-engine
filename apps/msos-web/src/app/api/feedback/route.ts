import { NextResponse } from "next/server";

import { CONFUSION_CATEGORIES, isConfusionCategory } from "@/lib/feedbackForm";
import { appendWebFeedback } from "@/lib/webFeedback";
import { appendProductUsageEvent } from "@/lib/webProductUsage";

export const runtime = "nodejs";

function asTrimmed(value: unknown, max = 4000): string | undefined {
  if (typeof value !== "string") return undefined;
  const trimmed = value.trim();
  if (!trimmed) return undefined;
  return trimmed.length > max ? trimmed.slice(0, max) : trimmed;
}

function asYn(value: unknown): string | undefined {
  const v = asTrimmed(value, 8)?.toUpperCase();
  if (v === "Y" || v === "N") return v;
  return undefined;
}

function asLikert(value: unknown): number | undefined {
  const n = typeof value === "number" ? value : Number(value);
  if (!Number.isInteger(n) || n < 1 || n > 5) return undefined;
  return n;
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const confusion = asTrimmed(body?.confusion_category, 120);
    if (!confusion || !isConfusionCategory(confusion)) {
      return NextResponse.json(
        { error: "invalid confusion_category", allowed: CONFUSION_CATEGORIES },
        { status: 400 },
      );
    }
    const usefulness = asLikert(body?.usefulness);
    const repeatUse = asLikert(body?.repeat_use_intent);
    if (usefulness === undefined || repeatUse === undefined) {
      return NextResponse.json({ error: "invalid usefulness or repeat_use_intent" }, { status: 400 });
    }

    const record = await appendWebFeedback({
      source: asTrimmed(body?.source, 80) || "public_feedback",
      tester_profile: asTrimmed(body?.tester_profile, 200),
      comprehension: asYn(body?.comprehension),
      thesis_confirm: asYn(body?.thesis_confirm),
      return_intent: asYn(body?.return_intent),
      paid_interest: asYn(body?.paid_interest),
      confusion_category: confusion,
      usefulness,
      repeat_use_intent: repeatUse,
      objections_text: asTrimmed(body?.objections_text, 4000),
      session_note: asTrimmed(body?.session_note, 500),
      reality_check_row: asTrimmed(body?.reality_check_row, 500),
      session_started_at: asTrimmed(body?.session_started_at, 40),
    });

    try {
      await appendProductUsageEvent({
        event_name: "feedback_submit",
        source: asTrimmed(body?.source, 80) || "operator_session_notebook",
        path: "/api/feedback",
        review_status: confusion,
      });
    } catch (err) {
      console.error("usage append failed", err);
    }

    return NextResponse.json({ ok: true, id: record.id });
  } catch (err) {
    console.error("feedback POST failed", err);
    return NextResponse.json({ error: "failed to save feedback" }, { status: 500 });
  }
}
