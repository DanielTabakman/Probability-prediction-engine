import type { StoredExpression } from "@/lib/msosWorkflowStore";

const UNDO_STORAGE_KEY = "msos.paper-trade.undo.v1";

export type PaperTradeUndoSnapshot = {
  expression: StoredExpression;
  deletedAt: string;
};

export function stashPaperTradeUndo(expression: StoredExpression): void {
  if (typeof window === "undefined") return;
  const snapshot: PaperTradeUndoSnapshot = {
    expression,
    deletedAt: new Date().toISOString(),
  };
  window.sessionStorage.setItem(UNDO_STORAGE_KEY, JSON.stringify(snapshot));
}

export function peekPaperTradeUndo(): PaperTradeUndoSnapshot | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(UNDO_STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as PaperTradeUndoSnapshot;
    if (!parsed?.expression?.id || typeof parsed.expression.planHeadline !== "string") {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

export function clearPaperTradeUndo(): void {
  if (typeof window === "undefined") return;
  window.sessionStorage.removeItem(UNDO_STORAGE_KEY);
}
