import { NextResponse } from "next/server";

import { requireProtectedIdentity } from "@/lib/msosIdentity";
import { isValidReviewStatus, upsertSnapshotReview } from "@/lib/snapshotReview";

export const runtime = "nodejs";

function asTrimmed(value: unknown, max: number): string | undefined {
  if (typeof value !== "string") return undefined;
  const trimmed = value.trim();
  if (!trimmed) return undefined;
  return trimmed.length > max ? trimmed.slice(0, max) : trimmed;
}

type RouteContext = {
  params: Promise<{ id: string }>;
};

export async function POST(request: Request, context: RouteContext) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;

  const { id: snapshotId } = await context.params;
  const sid = snapshotId?.trim();
  if (!sid) {
    return NextResponse.json({ error: "snapshot id required" }, { status: 400 });
  }

  let body: Record<string, unknown>;
  try {
    body = (await request.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ error: "invalid JSON body" }, { status: 400 });
  }

  const reviewStatus = asTrimmed(body.review_status, 64);
  if (!reviewStatus) {
    return NextResponse.json({ error: "review_status required" }, { status: 400 });
  }
  if (!isValidReviewStatus(reviewStatus)) {
    return NextResponse.json(
      {
        error: "invalid review_status",
        allowed: ["pending", "supportive", "contradictory", "contaminated", "not_judgeable"],
      },
      { status: 400 },
    );
  }

  const result = upsertSnapshotReview({
    snapshotId: sid,
    reviewStatus,
    outcomeNotes: asTrimmed(body.outcome_notes, 4000) ?? null,
    paperTag: asTrimmed(body.paper_tag, 120) ?? null,
    ownerEmail: identity.email || null,
  });

  if (!result.ok) {
    return NextResponse.json({ error: result.error }, { status: result.httpStatus });
  }

  return NextResponse.json({ ok: true, review: result.review });
}
