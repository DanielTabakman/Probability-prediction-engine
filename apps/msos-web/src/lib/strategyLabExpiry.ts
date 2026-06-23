/** Persist Strategy Lab expiry selection for expression planning (display only). */

export const STRATEGY_LAB_EXPIRY_STORAGE_KEY = "msos.strategy_lab.expiry.v1";

export function loadStoredStrategyLabExpiry(): string | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(STRATEGY_LAB_EXPIRY_STORAGE_KEY);
    return raw?.trim() || null;
  } catch {
    return null;
  }
}

export function saveStrategyLabExpiry(expiry: string): void {
  if (typeof window === "undefined" || !expiry.trim()) return;
  window.localStorage.setItem(STRATEGY_LAB_EXPIRY_STORAGE_KEY, expiry.trim());
}
