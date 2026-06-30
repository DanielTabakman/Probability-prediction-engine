/** Client-safe snapshot review types and helpers (no Node/sqlite imports). */

export const REVIEW_STATUSES = [
  "pending",
  "supportive",
  "contradictory",
  "contaminated",
  "not_judgeable",
] as const;

export type ReviewStatus = (typeof REVIEW_STATUSES)[number];

export const POST_MORTEM_STATUSES: ReviewStatus[] = [
  "supportive",
  "contradictory",
  "contaminated",
  "not_judgeable",
];

export function isValidReviewStatus(status: string): status is ReviewStatus {
  return (REVIEW_STATUSES as readonly string[]).includes(status);
}

export type SnapshotReviewRow = {
  id: string;
  snapshotId: string;
  reviewStatus: ReviewStatus;
  outcomeNotes: string | null;
  reviewedAtUtc: string;
  reviewHorizonRef: string | null;
  paperTag: string | null;
};

export type ReviewTag = {
  tag: string;
  tone?: string;
};

export function reviewTagForStatus(status: string | null | undefined): ReviewTag {
  switch ((status ?? "").trim().toLowerCase()) {
    case "supportive":
      return { tag: "Held up", tone: "teal" };
    case "contradictory":
      return { tag: "Didn't hold", tone: "amber" };
    case "contaminated":
      return { tag: "Bad data", tone: "red" };
    case "not_judgeable":
      return { tag: "Unclear" };
    case "pending":
      return { tag: "Review due", tone: "amber" };
    default:
      return { tag: "Needs review", tone: "amber" };
  }
}

export function reviewStatusLabel(status: ReviewStatus): string {
  switch (status) {
    case "supportive":
      return "Held up — view matched the market";
    case "contradictory":
      return "Didn't hold — market moved elsewhere";
    case "contaminated":
      return "Bad data — snapshot wasn't trustworthy";
    case "not_judgeable":
      return "Unclear — couldn't tell from outcome";
    case "pending":
      return "Pending — not finished";
    default:
      return status;
  }
}

export function reviewHorizonRefFromFrozen(record: Record<string, unknown>): string | null {
  const verification = record.verification;
  if (!verification || typeof verification !== "object") return null;
  const vs = (verification as Record<string, unknown>).verification_summary;
  const inner = vs && typeof vs === "object" ? (vs as Record<string, unknown>) : {};
  const parts = [
    String(record.expiry ?? "").trim(),
    String(inner.as_of_utc ?? "").trim(),
    String(inner.disagreement_category_id ?? "").trim(),
  ].filter(Boolean);
  return parts.length ? parts.join(" · ") : null;
}

export function classificationLine(record: Record<string, unknown>): string | null {
  const verification = record.verification;
  if (!verification || typeof verification !== "object") return null;
  const vs = (verification as Record<string, unknown>).verification_summary;
  if (!vs || typeof vs !== "object") return null;
  const cat = (vs as Record<string, unknown>).disagreement_category_id;
  return typeof cat === "string" && cat.trim() ? cat.trim() : null;
}
