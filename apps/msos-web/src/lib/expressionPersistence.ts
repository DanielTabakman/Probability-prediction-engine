/**
 * Expression persistence boundary (P6).
 * Preview: browser localStorage only — sim-only save, no order transmission.
 */

import type { StoredExpression } from "@/lib/msosWorkflowStore";
import { clearPaperTradeUndo, stashPaperTradeUndo } from "@/lib/paperTradeUndo";
import {
  optimizedPlan,
  planLegs,
  statusGridPlanned,
  type PlanLeg,
  type StatusCell,
} from "@/data/expressionPlanningFixtures";

export type ExpressionLifecycle = "planned" | "simulated";

export type PaperTradeStatus = "open" | "closed" | "expired";

export type BeliefSnapshot = {
  forwardMult: number;
  volMult: number;
};

/** Mark captured at paper-trade save (display/proxy fields only — no TS math). */
export type PaperTradeMarkSnapshot = {
  spotUsd?: number;
  netCostUsd?: number | null;
  maxGainUsd?: number | null;
  maxLossUsd?: number | null;
  markedAt: string;
};

export type ExpressionRecord = {
  familyId: string;
  planHeadline: string;
  planSummary: string;
  legs: PlanLeg[];
  lifecycle: ExpressionLifecycle;
  updatedAt: string;
  /** Paper-trade metadata (optional on planned drafts). */
  expiryDate?: string;
  instrument?: string;
  beliefSnapshot?: BeliefSnapshot;
  markAtSave?: PaperTradeMarkSnapshot;
  savedAt?: string;
  paperTradeStatus?: PaperTradeStatus;
  closedAt?: string;
};

export const EXPRESSION_STORAGE_KEY = "msos.expression.preview.v1";

export const EXPRESSION_PERSISTENCE_LABEL =
  "Paper trade plan saved to your workspace — no order was sent.";

export const defaultExpressionRecord: ExpressionRecord = {
  familyId: "range",
  planHeadline: optimizedPlan.headline,
  planSummary: optimizedPlan.summary,
  legs: planLegs,
  lifecycle: "planned",
  updatedAt: "2026-06-11T00:00:00.000Z",
};

function isPlanLeg(value: unknown): value is PlanLeg {
  if (!value || typeof value !== "object") {
    return false;
  }
  const row = value as Record<string, unknown>;
  return (
    (row.side === "BUY" || row.side === "SELL") &&
    typeof row.instrument === "string" &&
    typeof row.strike === "string" &&
    typeof row.tenor === "string"
  );
}

function isExpressionRecord(value: unknown): value is ExpressionRecord {
  if (!value || typeof value !== "object") {
    return false;
  }
  const row = value as Record<string, unknown>;
  return (
    typeof row.familyId === "string" &&
    typeof row.planHeadline === "string" &&
    typeof row.planSummary === "string" &&
    Array.isArray(row.legs) &&
    row.legs.every(isPlanLeg) &&
    (row.lifecycle === "planned" || row.lifecycle === "simulated") &&
    typeof row.updatedAt === "string"
  );
}

export function loadExpressionRecord(fallback: ExpressionRecord): ExpressionRecord {
  if (typeof window === "undefined") {
    return fallback;
  }
  try {
    const raw = window.localStorage.getItem(EXPRESSION_STORAGE_KEY);
    if (!raw) {
      return fallback;
    }
    const parsed: unknown = JSON.parse(raw);
    return isExpressionRecord(parsed) ? parsed : fallback;
  } catch {
    return fallback;
  }
}

export function saveExpressionRecord(record: ExpressionRecord): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.setItem(EXPRESSION_STORAGE_KEY, JSON.stringify(record));
}

export async function fetchExpressionRecord(fallback: ExpressionRecord): Promise<ExpressionRecord> {
  if (typeof window === "undefined") {
    return fallback;
  }
  try {
    const response = await fetch("/api/theses/expression", { cache: "no-store", credentials: "include" });
    if (!response.ok) {
      return loadExpressionRecord(fallback);
    }
    const payload = (await response.json()) as { expression?: ExpressionRecord | null };
    if (payload.expression && isExpressionRecord(payload.expression)) {
      saveExpressionRecord(payload.expression);
      return payload.expression;
    }
    const preview = loadExpressionRecord(fallback);
    if (preview.updatedAt !== fallback.updatedAt) {
      await persistExpressionRecord(preview);
      return preview;
    }
    return fallback;
  } catch {
    return loadExpressionRecord(fallback);
  }
}

export async function persistExpressionRecord(record: ExpressionRecord): Promise<void> {
  saveExpressionRecord(record);
  if (typeof window === "undefined") {
    return;
  }
  try {
    await fetch("/api/theses/expression", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ expression: record }),
    });
  } catch {
    // local preview remains as offline fallback
  }
}

export async function savePaperTrade(record: ExpressionRecord): Promise<{
  expression: ExpressionRecord;
  ok: boolean;
  authRequired?: boolean;
  error?: string;
}> {
  const payload: ExpressionRecord = {
    ...record,
    lifecycle: "simulated",
    paperTradeStatus: "open",
    savedAt: record.savedAt ?? new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  saveExpressionRecord(payload);
  if (typeof window === "undefined") {
    return { expression: payload, ok: true };
  }
  try {
    const response = await fetch("/api/theses/paper-trades", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ expression: payload }),
    });
    if (!response.ok) {
      const body = (await response.json().catch(() => ({}))) as { error?: string };
      if (response.status === 401) {
        return {
          expression: payload,
          ok: false,
          authRequired: true,
          error: "Sign in to save paper trades to your profile.",
        };
      }
      return {
        expression: payload,
        ok: false,
        error: body.error ?? "Could not save paper trade — confirm your view first.",
      };
    }
    const body = (await response.json()) as { expression?: ExpressionRecord };
    if (body.expression && isExpressionRecord(body.expression)) {
      saveExpressionRecord(body.expression);
      return { expression: body.expression, ok: true };
    }
    return { expression: payload, ok: true };
  } catch {
    return {
      expression: payload,
      ok: false,
      error: "Network error — paper trade saved locally only.",
    };
  }
}

export async function deletePaperTradeById(tradeId: string): Promise<boolean> {
  if (typeof window === "undefined") return false;
  try {
    const response = await fetch(`/api/theses/paper-trades/${encodeURIComponent(tradeId)}`, {
      method: "DELETE",
      credentials: "include",
    });
    return response.ok;
  } catch {
    return false;
  }
}

export async function fetchPaperTradeByIdClient(tradeId: string): Promise<StoredExpression | null> {
  if (typeof window === "undefined") return null;
  try {
    const response = await fetch(`/api/theses/paper-trades/${encodeURIComponent(tradeId)}`, {
      cache: "no-store",
      credentials: "include",
    });
    if (!response.ok) return null;
    const body = (await response.json()) as { expression?: StoredExpression };
    return body.expression ?? null;
  } catch {
    return null;
  }
}

export async function deletePaperTradeWithUndo(
  tradeId: string,
): Promise<{ ok: boolean; title?: string }> {
  const trade = await fetchPaperTradeByIdClient(tradeId);
  if (!trade) {
    return { ok: false };
  }
  stashPaperTradeUndo(trade);
  const ok = await deletePaperTradeById(tradeId);
  if (!ok) {
    clearPaperTradeUndo();
    return { ok: false };
  }
  return { ok: true, title: trade.planHeadline };
}

export async function restorePaperTrade(expression: StoredExpression): Promise<boolean> {
  if (typeof window === "undefined") return false;
  try {
    const response = await fetch("/api/theses/paper-trades/restore", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ expression }),
    });
    return response.ok;
  } catch {
    return false;
  }
}

export async function clearAllPaperTrades(): Promise<boolean> {
  if (typeof window === "undefined") return false;
  try {
    const response = await fetch("/api/theses/paper-trades", {
      method: "DELETE",
      credentials: "include",
    });
    return response.ok;
  } catch {
    return false;
  }
}

export async function closePaperTradeById(tradeId: string): Promise<boolean> {
  if (typeof window === "undefined") return false;
  try {
    const response = await fetch(`/api/theses/paper-trades/${encodeURIComponent(tradeId)}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ action: "close" }),
    });
    return response.ok;
  } catch {
    return false;
  }
}

export function withExpressionLifecycle(
  record: ExpressionRecord,
  lifecycle: ExpressionLifecycle,
): ExpressionRecord {
  return {
    ...record,
    lifecycle,
    updatedAt: new Date().toISOString(),
  };
}

export function statusGridForLifecycle(lifecycle: ExpressionLifecycle): StatusCell[] {
  return lifecycle === "simulated"
    ? [
        { label: "Thesis", value: "Confirmed", tone: "teal" },
        { label: "Expression", value: "Simulated", tone: "teal" },
        { label: "Execution", value: "None" },
        { label: "Monitoring", value: "Ready" },
        { label: "Review", value: "Expiry" },
      ]
    : statusGridPlanned;
}
