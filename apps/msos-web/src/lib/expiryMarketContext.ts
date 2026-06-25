/**
 * Plain-language market context for a selected expiry (display/proxy only).
 */

import {
  findSeriesByExpiry,
  listExpiryDates,
  type DisplayPayload,
} from "@/lib/ppeDisplayPayload";

export type ExpiryMarketContext = {
  expiryDate: string;
  spotUsd: number;
  marketBestGuessUsd: number | null;
  /** Pre-formatted fallback when numeric median unavailable (from Python summary row). */
  marketBestGuessFallback: string;
  typicalRangeUsd: { q1: number; q3: number } | null;
  /** Pre-formatted fallback when q1/q3 unavailable. */
  typicalRangeFallback: string;
  dataLabel: string;
};

function summaryRowForExpiry(
  payload: DisplayPayload,
  expiryDate: string,
): Record<string, string> | undefined {
  const rows = payload.summary?.table_rows ?? [];
  return rows.find((row) => {
    const method = (row.Method ?? row.method ?? "").toLowerCase();
    const expiry = row.Expiry ?? row.expiry_date ?? row.expiry ?? "";
    const isLognormal = method.includes("lognormal") || method.includes("reference");
    return isLognormal && String(expiry).startsWith(expiryDate.slice(0, 10));
  });
}

function parseUsdish(value: string | number | undefined): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value !== "string") {
    return null;
  }
  const digits = value.replace(/[^0-9.-]/g, "");
  const parsed = Number.parseFloat(digits);
  return Number.isFinite(parsed) ? parsed : null;
}

export function buildExpiryMarketContext(
  payload: DisplayPayload,
  expiryDate?: string,
): ExpiryMarketContext | null {
  const dates = listExpiryDates(payload);
  const resolvedExpiry =
    expiryDate && dates.includes(expiryDate) ? expiryDate : dates[0];
  if (!resolvedExpiry) {
    return null;
  }

  const series = findSeriesByExpiry(payload, resolvedExpiry);
  const lognormal = summaryRowForExpiry(payload, resolvedExpiry);
  const medianFromSeries = series?.quartiles_usd?.median_usd ?? series?.mean_usd ?? null;
  const medianFromRow = parseUsdish(lognormal?.["Median terminal price (50th %)"]);
  const marketBestGuessUsd = medianFromSeries ?? medianFromRow;

  const q1 = series?.quartiles_usd?.q1_usd;
  const q3 = series?.quartiles_usd?.q3_usd;
  const typicalRangeUsd =
    typeof q1 === "number" && typeof q3 === "number" ? { q1, q3 } : null;

  return {
    expiryDate: resolvedExpiry,
    spotUsd: payload.spot_usd,
    marketBestGuessUsd,
    marketBestGuessFallback: lognormal?.["Median terminal price (50th %)"] ?? "—",
    typicalRangeUsd,
    typicalRangeFallback: lognormal?.["Implied range width (IQR)"] ?? "—",
    dataLabel: "Live · Deribit",
  };
}
