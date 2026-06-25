/** Client-side workflow identity checks (display boundary — no auth logic). */

const PENDING_PAPER_TRADE_KEY = "msos.pendingPaperTrade.v1";

export async function hasWorkflowIdentity(): Promise<boolean> {
  if (typeof window === "undefined") {
    return false;
  }
  try {
    const response = await fetch("/api/entitlements/me", {
      cache: "no-store",
      credentials: "include",
    });
    return response.ok;
  } catch {
    return false;
  }
}

export function stashPendingPaperTrade(payload: unknown): void {
  if (typeof window === "undefined") return;
  try {
    window.sessionStorage.setItem(PENDING_PAPER_TRADE_KEY, JSON.stringify(payload));
  } catch {
    /* ignore quota */
  }
}

export function takePendingPaperTrade<T>(): T | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.sessionStorage.getItem(PENDING_PAPER_TRADE_KEY);
    if (!raw) return null;
    window.sessionStorage.removeItem(PENDING_PAPER_TRADE_KEY);
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}
