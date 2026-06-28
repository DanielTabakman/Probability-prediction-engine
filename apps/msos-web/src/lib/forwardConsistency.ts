/**
 * Forward consistency boundary — display/proxy only (parity math in Python).
 */

import type { LabAssetId } from "@/lib/ppeDisplayPayload";

export const PPE_FORWARD_CONSISTENCY_API_URL = (
  process.env.NEXT_PUBLIC_PPE_FORWARD_CONSISTENCY_API_URL ??
  "/ppe-display-api/forward-consistency.json"
).trim();

export type ForwardConsistencyStatus =
  | "NO_ARB"
  | "WATCH"
  | "POSSIBLE_ARB"
  | "BAD_DATA"
  | "NOT_COMPARABLE";

export type ForwardConsistencyLeg = {
  side: "buy" | "sell";
  instrument_type: "future" | "call" | "put";
  label: string;
};

export type ForwardConsistencyPayload = {
  kind: "forward_consistency_boundary" | "forward_consistency_error";
  schema_version?: number;
  asset_id?: string;
  expiry_date?: string;
  as_of_utc?: string;
  spot_usd?: number;
  forward_usd?: number;
  comparable?: boolean;
  venue?: string;
  status?: ForwardConsistencyStatus;
  direction?: "SELL_FUTURE_BUY_SYNTHETIC" | "BUY_FUTURE_SELL_SYNTHETIC";
  best_strike?: number | null;
  synthetic_bid?: number | null;
  synthetic_ask?: number | null;
  synthetic_width_usd?: number | null;
  future_bid?: number | null;
  future_ask?: number | null;
  future_instrument?: string;
  gross_edge_usd?: number | null;
  estimated_cost_usd?: number | null;
  net_edge_usd?: number | null;
  legs?: ForwardConsistencyLeg[];
  detail?: string;
  copy_note?: string;
  research_only?: boolean;
  error?: string;
};

export function buildForwardConsistencyFetchUrl(
  expiry: string,
  assetId: LabAssetId = "BTC",
): string {
  const base = PPE_FORWARD_CONSISTENCY_API_URL;
  const separator = base.includes("?") ? "&" : "?";
  const params = new URLSearchParams({
    expiry,
    asset: assetId,
  });
  return `${base}${separator}${params.toString()}`;
}

export function isForwardConsistencyPayload(
  value: unknown,
): value is ForwardConsistencyPayload {
  if (!value || typeof value !== "object") {
    return false;
  }
  const payload = value as Partial<ForwardConsistencyPayload>;
  return (
    payload.kind === "forward_consistency_boundary" ||
    payload.kind === "forward_consistency_error"
  );
}

export function statusBadgeLabel(status: ForwardConsistencyStatus | undefined): string {
  switch (status) {
    case "NO_ARB":
      return "No arb";
    case "WATCH":
      return "Watch";
    case "POSSIBLE_ARB":
      return "Possible arb";
    case "BAD_DATA":
      return "Bad data";
    case "NOT_COMPARABLE":
      return "Not comparable";
    default:
      return "—";
  }
}

export async function fetchForwardConsistencyPayload(
  expiry: string,
  assetId: LabAssetId = "BTC",
): Promise<ForwardConsistencyPayload | null> {
  const url = buildForwardConsistencyFetchUrl(expiry, assetId);
  try {
    const res = await fetch(url, {
      cache: "no-store",
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(90_000),
    });
    if (!res.ok) {
      return null;
    }
    const data: unknown = await res.json();
    if (!isForwardConsistencyPayload(data)) {
      return null;
    }
    return data;
  } catch {
    return null;
  }
}

/** Sample-mode fixture when live API unavailable. */
export const DEMO_FORWARD_CONSISTENCY: ForwardConsistencyPayload = {
  kind: "forward_consistency_boundary",
  schema_version: 1,
  asset_id: "BTC",
  comparable: true,
  venue: "deribit",
  status: "NO_ARB",
  spot_usd: 98_500,
  forward_usd: 99_100,
  synthetic_bid: 99_050,
  synthetic_ask: 99_180,
  future_bid: 99_080,
  future_ask: 99_150,
  gross_edge_usd: -30,
  estimated_cost_usd: 45,
  net_edge_usd: -75,
  copy_note:
    "Sample data — live check loads when the display API is connected. Spot vs future is not arbitrage.",
  research_only: true,
};
