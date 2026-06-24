/**
 * Display currency for MSOS shell — Deribit/PPE math stays USD; CAD is converted for display only.
 */

export type DisplayCurrency = "USD" | "CAD";

export const DISPLAY_CURRENCY_STORAGE_KEY = "msos.display.currency.v1";
export const DISPLAY_CURRENCY_COOKIE = "msos_currency";

/** Approximate FX for display — not a live quote. Override via env on deploy. */
export const CAD_PER_USD = Number(process.env.NEXT_PUBLIC_MSOS_CAD_PER_USD ?? "1.36");

export const DISPLAY_CURRENCY_OPTIONS: { id: DisplayCurrency; label: string }[] = [
  { id: "USD", label: "USD" },
  { id: "CAD", label: "CAD" },
];

export function isDisplayCurrency(value: string): value is DisplayCurrency {
  return value === "USD" || value === "CAD";
}

export function loadStoredDisplayCurrency(): DisplayCurrency {
  if (typeof window === "undefined") return "USD";
  try {
    const raw = window.localStorage.getItem(DISPLAY_CURRENCY_STORAGE_KEY);
    return raw && isDisplayCurrency(raw) ? raw : "USD";
  } catch {
    return "USD";
  }
}

export function saveDisplayCurrency(currency: DisplayCurrency): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(DISPLAY_CURRENCY_STORAGE_KEY, currency);
  document.cookie = `${DISPLAY_CURRENCY_COOKIE}=${currency};path=/;max-age=31536000;samesite=lax`;
}

export function usdToDisplayAmount(usd: number, currency: DisplayCurrency): number {
  if (!Number.isFinite(usd)) return usd;
  return currency === "CAD" ? usd * CAD_PER_USD : usd;
}

export function formatMoney(usd: number, currency: DisplayCurrency = "USD"): string {
  const amount = usdToDisplayAmount(usd, currency);
  return new Intl.NumberFormat(currency === "CAD" ? "en-CA" : "en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function currencyHint(currency: DisplayCurrency): string {
  if (currency === "CAD") {
    return `CAD (≈ USD × ${CAD_PER_USD}) — Deribit quotes are USD`;
  }
  return "USD — Deribit BTC options";
}
