/**
 * Display currency for MSOS shell — Deribit/PPE math stays USD; other fiat is display-only.
 */

export type DisplayCurrency = "USD" | "CAD" | "EUR" | "GBP" | "AUD" | "CHF";

export const DISPLAY_CURRENCY_STORAGE_KEY = "msos.display.currency.v1";
export const DISPLAY_CURRENCY_COOKIE = "msos_currency";

const ENV_FX_KEYS: Record<Exclude<DisplayCurrency, "USD">, string> = {
  CAD: "NEXT_PUBLIC_MSOS_CAD_PER_USD",
  EUR: "NEXT_PUBLIC_MSOS_EUR_PER_USD",
  GBP: "NEXT_PUBLIC_MSOS_GBP_PER_USD",
  AUD: "NEXT_PUBLIC_MSOS_AUD_PER_USD",
  CHF: "NEXT_PUBLIC_MSOS_CHF_PER_USD",
};

/** Approximate FX for display — not live quotes. Override per currency via env on deploy. */
const DEFAULT_FX_PER_USD: Record<DisplayCurrency, number> = {
  USD: 1,
  CAD: 1.36,
  EUR: 0.92,
  GBP: 0.79,
  AUD: 1.53,
  CHF: 0.88,
};

const LOCALE_BY_CURRENCY: Record<DisplayCurrency, string> = {
  USD: "en-US",
  CAD: "en-CA",
  EUR: "de-DE",
  GBP: "en-GB",
  AUD: "en-AU",
  CHF: "de-CH",
};

export const DISPLAY_CURRENCY_OPTIONS: { id: DisplayCurrency; label: string }[] = [
  { id: "USD", label: "USD" },
  { id: "CAD", label: "CAD ($)" },
  { id: "EUR", label: "EUR (€)" },
  { id: "GBP", label: "GBP (£)" },
  { id: "AUD", label: "AUD ($)" },
  { id: "CHF", label: "CHF" },
];

/** @deprecated Use fxPerUsd(currency) — kept for existing env/docs references. */
export const CAD_PER_USD = fxPerUsd("CAD");

export function fxPerUsd(currency: DisplayCurrency): number {
  if (currency === "USD") return 1;
  const envKey = ENV_FX_KEYS[currency];
  const raw = process.env[envKey];
  if (raw != null && raw.trim() !== "") {
    const parsed = Number(raw);
    if (Number.isFinite(parsed) && parsed > 0) return parsed;
  }
  return DEFAULT_FX_PER_USD[currency];
}

export function isDisplayCurrency(value: string): value is DisplayCurrency {
  return DISPLAY_CURRENCY_OPTIONS.some((opt) => opt.id === value);
}

export function parseDisplayCurrency(value: string | null | undefined): DisplayCurrency {
  const raw = (value ?? "").trim();
  return raw && isDisplayCurrency(raw) ? raw : "USD";
}

export function parseDisplayCurrencyFromCookie(
  cookieValue: string | null | undefined,
): DisplayCurrency {
  return parseDisplayCurrency(cookieValue);
}

export function loadStoredDisplayCurrency(): DisplayCurrency {
  if (typeof window === "undefined") return "USD";
  try {
    const raw = window.localStorage.getItem(DISPLAY_CURRENCY_STORAGE_KEY);
    return parseDisplayCurrency(raw);
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
  return usd * fxPerUsd(currency);
}

function localeFor(currency: DisplayCurrency): string {
  return LOCALE_BY_CURRENCY[currency];
}

function currencySymbol(currency: DisplayCurrency): string {
  const parts = new Intl.NumberFormat(localeFor(currency), {
    style: "currency",
    currency,
    currencyDisplay: "narrowSymbol",
    maximumFractionDigits: 0,
  }).formatToParts(0);
  return parts.find((part) => part.type === "currency")?.value ?? currency;
}

export function formatMoney(usd: number, currency: DisplayCurrency = "USD"): string {
  const amount = usdToDisplayAmount(usd, currency);
  return new Intl.NumberFormat(localeFor(currency), {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(amount);
}

/** Compact axis labels — converts USD canonical values to display currency. */
export function formatAxisAmount(usd: number, currency: DisplayCurrency = "USD"): string {
  const value = usdToDisplayAmount(usd, currency);
  const abs = Math.abs(value);
  const symbol = currencySymbol(currency);
  if (abs >= 1_000_000) {
    return `${symbol}${(value / 1_000_000).toFixed(1)}M`;
  }
  if (abs >= 10_000) {
    return `${symbol}${Math.round(value / 1000)}k`;
  }
  if (abs >= 1000) {
    return `${symbol}${(value / 1000).toFixed(1)}k`;
  }
  return formatMoney(usd, currency);
}

export function currencyHint(currency: DisplayCurrency): string {
  if (currency === "USD") {
    return "USD — Deribit BTC options are quoted in USD";
  }
  const rate = fxPerUsd(currency);
  return `${currency} display only (≈ USD × ${rate}) — Deribit quotes and settlement stay USD`;
}

export function displayCurrencyDisclaimer(currency: DisplayCurrency): string {
  if (currency === "USD") {
    return "Amounts shown in USD — same as Deribit BTC option quotes.";
  }
  return `Amounts shown in ${currency} for convenience. BTC options on Deribit are quoted and settled in USD; conversion is approximate, not a live FX feed.`;
}
