/**
 * Thesis persistence boundary (P5).
 * Preview: browser localStorage only — no server API, no false Live claims.
 */

export type ThesisLifecycle = "exploring" | "draft" | "confirmed";

export type ThesisRecord = {
  instrument: string;
  horizonDays: number;
  marketRangePct: number;
  thesisRangePct: number;
  referenceLabel: string;
  trustLabel: string;
  lifecycle: ThesisLifecycle;
  updatedAt: string;
};

export const THESIS_STORAGE_KEY = "msos.thesis.preview.v1";

export const THESIS_PERSISTENCE_LABEL =
  "Preview persistence — saved in this browser only; not a live account record.";

export function thesisRecordSchema(): Record<string, string> {
  return {
    instrument: "string",
    horizonDays: "number",
    marketRangePct: "number",
    thesisRangePct: "number",
    referenceLabel: "string",
    trustLabel: "string",
    lifecycle: "exploring | draft | confirmed",
    updatedAt: "ISO-8601 string",
  };
}

function isThesisRecord(value: unknown): value is ThesisRecord {
  if (!value || typeof value !== "object") {
    return false;
  }
  const row = value as Record<string, unknown>;
  return (
    typeof row.instrument === "string" &&
    typeof row.horizonDays === "number" &&
    typeof row.marketRangePct === "number" &&
    typeof row.thesisRangePct === "number" &&
    typeof row.referenceLabel === "string" &&
    typeof row.trustLabel === "string" &&
    (row.lifecycle === "exploring" || row.lifecycle === "draft" || row.lifecycle === "confirmed") &&
    typeof row.updatedAt === "string"
  );
}

export function loadThesisRecord(fallback: ThesisRecord): ThesisRecord {
  if (typeof window === "undefined") {
    return fallback;
  }
  try {
    const raw = window.localStorage.getItem(THESIS_STORAGE_KEY);
    if (!raw) {
      return fallback;
    }
    const parsed: unknown = JSON.parse(raw);
    return isThesisRecord(parsed) ? parsed : fallback;
  } catch {
    return fallback;
  }
}

export function saveThesisRecord(record: ThesisRecord): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(THESIS_STORAGE_KEY, JSON.stringify(record));
}

export function withLifecycle(record: ThesisRecord, lifecycle: ThesisLifecycle): ThesisRecord {
  return {
    ...record,
    lifecycle,
    updatedAt: new Date().toISOString(),
  };
}
