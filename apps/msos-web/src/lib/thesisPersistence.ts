/**
 * Thesis persistence boundary (P5).
 * Preview: browser localStorage only — no server API, no false Live claims.
 */

export type ThesisLifecycle = "exploring" | "draft" | "confirmed";

export type ThesisBeliefSnapshot = {
  forwardMult: number;
  volMult: number;
  viewLabel?: string;
};

export type ThesisRecord = {
  instrument: string;
  horizonDays: number;
  marketRangePct: number;
  thesisRangePct: number;
  referenceLabel: string;
  trustLabel: string;
  lifecycle: ThesisLifecycle;
  updatedAt: string;
  /** Captured from Strategy Lab at confirm time. */
  expiryDate?: string;
  beliefSnapshot?: ThesisBeliefSnapshot;
  disagreementLine?: string;
  spotUsdAtConfirm?: number;
};

export const THESIS_STORAGE_KEY = "msos.thesis.preview.v1";

export const THESIS_PERSISTENCE_LABEL =
  "Saved to your workspace on this demo — paper trading only, not a brokerage record.";

export const THESIS_PREVIEW_MIGRATION_NOTE =
  "One-time import from browser preview keys (msos.thesis.preview.v1) when server store is empty.";

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

export async function fetchThesisRecord(fallback: ThesisRecord): Promise<ThesisRecord> {
  if (typeof window === "undefined") {
    return fallback;
  }
  try {
    const response = await fetch("/api/theses", { cache: "no-store", credentials: "include" });
    if (!response.ok) {
      return loadThesisRecord(fallback);
    }
    const payload = (await response.json()) as { thesis?: ThesisRecord | null };
    if (payload.thesis && isThesisRecord(payload.thesis)) {
      saveThesisRecord(payload.thesis);
      return payload.thesis;
    }
    const preview = loadThesisRecord(fallback);
    if (preview.updatedAt !== fallback.updatedAt) {
      await persistThesisRecord(preview);
      return preview;
    }
    return fallback;
  } catch {
    return loadThesisRecord(fallback);
  }
}

export async function persistThesisRecord(record: ThesisRecord): Promise<boolean> {
  saveThesisRecord(record);
  if (typeof window === "undefined") {
    return true;
  }
  try {
    const response = await fetch("/api/theses", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ thesis: record }),
    });
    return response.ok;
  } catch {
    return false;
  }
}

export function withLifecycle(record: ThesisRecord, lifecycle: ThesisLifecycle): ThesisRecord {
  return {
    ...record,
    lifecycle,
    updatedAt: new Date().toISOString(),
  };
}
