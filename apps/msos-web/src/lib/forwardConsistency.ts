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

export const PPE_FORWARD_CONSISTENCY_DASHBOARD_API_URL = (
  process.env.NEXT_PUBLIC_PPE_FORWARD_CONSISTENCY_DASHBOARD_API_URL ??
  "/ppe-display-api/forward-consistency/dashboard.json"
).trim();

export type ForwardConsistencyHeatmapCell = {
  asset_id: string;
  expiry_date: string;
  status: ForwardConsistencyStatus;
  net_edge_usd: number | null;
  quality_flags: string[];
  as_of_utc: string;
};

export type ForwardConsistencyDashboardSummary = {
  assets_checked: number;
  expiries_checked: number;
  watch_count: number;
  possible_count: number;
  bad_data_count: number;
};

export type ForwardConsistencyDashboardPayload = {
  kind: "forward_consistency_dashboard" | "forward_consistency_error";
  schema_version?: number;
  summary?: ForwardConsistencyDashboardSummary;
  cells?: ForwardConsistencyHeatmapCell[];
  error?: string;
};

export function isForwardConsistencyDashboardPayload(
  value: unknown,
): value is ForwardConsistencyDashboardPayload {
  if (!value || typeof value !== "object") {
    return false;
  }
  const payload = value as Partial<ForwardConsistencyDashboardPayload>;
  return (
    payload.kind === "forward_consistency_dashboard" ||
    payload.kind === "forward_consistency_error"
  );
}

export async function fetchForwardConsistencyDashboard(): Promise<ForwardConsistencyDashboardPayload | null> {
  try {
    const res = await fetch(PPE_FORWARD_CONSISTENCY_DASHBOARD_API_URL, {
      cache: "no-store",
      headers: { Accept: "application/json" },
      signal: AbortSignal.timeout(90_000),
    });
    if (!res.ok) {
      return null;
    }
    const data: unknown = await res.json();
    if (!isForwardConsistencyDashboardPayload(data)) {
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

export const DEMO_FORWARD_CONSISTENCY_DASHBOARD: ForwardConsistencyDashboardPayload = {
  kind: "forward_consistency_dashboard",
  schema_version: 1,
  summary: {
    assets_checked: 2,
    expiries_checked: 4,
    watch_count: 1,
    possible_count: 0,
    bad_data_count: 1,
  },
  cells: [
    {
      asset_id: "BTC",
      expiry_date: "2026-07-25",
      status: "NO_ARB",
      net_edge_usd: -75,
      quality_flags: [],
      as_of_utc: "2026-06-30T12:00:00Z",
    },
    {
      asset_id: "BTC",
      expiry_date: "2026-08-29",
      status: "WATCH",
      net_edge_usd: -15,
      quality_flags: ["wide_synthetic"],
      as_of_utc: "2026-06-30T12:00:00Z",
    },
    {
      asset_id: "BTC",
      expiry_date: "2026-09-26",
      status: "NO_ARB",
      net_edge_usd: -42,
      quality_flags: [],
      as_of_utc: "2026-06-30T12:00:00Z",
    },
    {
      asset_id: "ETH",
      expiry_date: "2026-07-25",
      status: "BAD_DATA",
      net_edge_usd: null,
      quality_flags: ["missing_future"],
      as_of_utc: "2026-06-30T12:00:00Z",
    },
    {
      asset_id: "ETH",
      expiry_date: "2026-08-29",
      status: "NOT_COMPARABLE",
      net_edge_usd: null,
      quality_flags: [],
      as_of_utc: "2026-06-30T12:00:00Z",
    },
  ],
};
