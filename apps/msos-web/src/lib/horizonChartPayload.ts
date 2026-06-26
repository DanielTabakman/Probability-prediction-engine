/**
 * Options Horizon chart payload — read-only JSON from Python display API.
 */

export const HORIZON_CHART_API_URL = (
  process.env.NEXT_PUBLIC_HORIZON_CHART_API_URL ?? "/ppe-display-api/horizon/chart.json"
).trim();

export const HORIZON_REGION_PREVIEW_API_URL = (
  process.env.NEXT_PUBLIC_HORIZON_REGION_PREVIEW_API_URL ??
  "/ppe-display-api/horizon/region-preview.json"
).trim();

export type HorizonHistoricalPoint = {
  date_utc: string;
  timestamp_utc: string;
  close_usd: number;
  volume: number | null;
};

export type HorizonForwardPoint = {
  expiry_date: string;
  expiry_utc: string;
  mark_price_usd: number;
  instrument_name?: string;
};

export type HorizonImpliedSlice = {
  expiry_ts: number;
  expiry_date: string;
  forward_usd: number;
  atm_iv_annual: number;
  T_years: number;
  prices_usd: number[];
  pdf_pct: number[];
};

export type HorizonChartPayload = {
  schema_version: number;
  kind: string;
  as_of_utc: string;
  asset_id: string;
  spot_usd: number;
  historical: {
    series: HorizonHistoricalPoint[];
    chart_days: number;
    source: string;
  };
  forward: {
    curve: HorizonForwardPoint[];
    source: string;
  };
  implied: HorizonImpliedSlice | null;
  archive: {
    available_days: number;
    earliest_utc: string | null;
    latest_utc: string | null;
    replay_ready: boolean;
    replay_threshold_days: number;
  };
  meta: {
    read_only: boolean;
    simulation_only: boolean;
    http_path: string;
  };
};

export type HorizonRegionPreview = {
  kind: string;
  computed?: {
    implied_mass_pct: number;
    method: string;
    linked_expiry_ts: number;
  };
  error?: string;
};

export async function fetchHorizonChartPayload(
  params?: { expiryTs?: number; chartDays?: number },
): Promise<HorizonChartPayload | null> {
  const url = new URL(
    HORIZON_CHART_API_URL,
    typeof window !== "undefined" ? window.location.origin : "http://localhost",
  );
  if (params?.expiryTs) url.searchParams.set("expiry_ts", String(params.expiryTs));
  if (params?.chartDays) url.searchParams.set("chart_days", String(params.chartDays));
  try {
    const res = await fetch(url.toString(), { cache: "no-store" });
    if (!res.ok) return null;
    return (await res.json()) as HorizonChartPayload;
  } catch {
    return null;
  }
}

export async function fetchHorizonRegionPreview(query: {
  priceMinUsd: number;
  priceMaxUsd: number;
  timeEndUtc: string;
  expiryTs: number;
  forwardUsd: number;
  atmIvAnnual: number;
  tYears: number;
}): Promise<HorizonRegionPreview | null> {
  const url = new URL(
    HORIZON_REGION_PREVIEW_API_URL,
    typeof window !== "undefined" ? window.location.origin : "http://localhost",
  );
  url.searchParams.set("price_min_usd", String(query.priceMinUsd));
  url.searchParams.set("price_max_usd", String(query.priceMaxUsd));
  url.searchParams.set("time_end_utc", query.timeEndUtc);
  url.searchParams.set("expiry_ts", String(query.expiryTs));
  url.searchParams.set("forward_usd", String(query.forwardUsd));
  url.searchParams.set("atm_iv_annual", String(query.atmIvAnnual));
  url.searchParams.set("T_years", String(query.tYears));
  try {
    const res = await fetch(url.toString(), { cache: "no-store" });
    if (!res.ok) return null;
    return (await res.json()) as HorizonRegionPreview;
  } catch {
    return null;
  }
}

export function strategyLabDeepLink(payload: HorizonChartPayload): string {
  const implied = payload.implied;
  const params = new URLSearchParams();
  params.set("asset", payload.asset_id);
  if (implied?.expiry_date) params.set("expiry", implied.expiry_date);
  return `/strategy-lab?${params.toString()}`;
}
