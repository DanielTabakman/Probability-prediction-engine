/**
 * Expression persistence boundary (P6).
 * Preview: browser localStorage only — sim-only save, no order transmission.
 */

import {
  optimizedPlan,
  planLegs,
  statusGridPlanned,
  type PlanLeg,
  type StatusCell,
} from "@/data/expressionPlanningFixtures";

export type ExpressionLifecycle = "planned" | "simulated";

export type ExpressionRecord = {
  familyId: string;
  planHeadline: string;
  planSummary: string;
  legs: PlanLeg[];
  lifecycle: ExpressionLifecycle;
  updatedAt: string;
};

export const EXPRESSION_STORAGE_KEY = "msos.expression.preview.v1";

export const EXPRESSION_PERSISTENCE_LABEL =
  "Preview persistence — simulated expression saved in this browser only; no live order transmitted.";

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
