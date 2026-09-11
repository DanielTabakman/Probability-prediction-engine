import type { HorizonChartPayload } from "@/lib/horizonChartPayload";
import {
  buildOptionsHorizonComparisonFromChart,
  type OptionsHorizonComparisonPayload,
} from "@/lib/optionsHorizonComparison";
import type { RegionBetGuidedShellSnapshot } from "@/lib/regionBetGuidedShell";

export type RegionBetMarketComparePayload = {
  schema_version: 1;
  kind: "region_bet_market_compare";
  region_context: {
    asset_id: string;
    symbol?: string;
    venue?: string;
    expiry_utc: string;
    window_start_utc?: string;
    window_end_utc?: string;
    price_min_usd: number;
    price_max_usd: number;
  };
  comparison: OptionsHorizonComparisonPayload;
};

function validDate(value: string | undefined): value is string {
  return typeof value === "string" && !Number.isNaN(Date.parse(value));
}

function validNumber(value: number): boolean {
  return Number.isFinite(value);
}

export function isRegionBetMarketCompareReady(
  snapshot: RegionBetGuidedShellSnapshot,
): boolean {
  const region = snapshot.selected_region;
  return (
    snapshot.asset_id.trim().length > 0 &&
    validDate(snapshot.expiry_utc) &&
    validDate(region.time_start_utc) &&
    validDate(region.time_end_utc) &&
    validNumber(region.price_min_usd) &&
    validNumber(region.price_max_usd) &&
    region.price_min_usd < region.price_max_usd &&
    Date.parse(region.time_start_utc) <= Date.parse(region.time_end_utc)
  );
}

export function regionBetMarketCompareFetchParams(
  snapshot: RegionBetGuidedShellSnapshot,
): { expiryTs: number } | null {
  if (!isRegionBetMarketCompareReady(snapshot)) return null;
  const expiryTs = Math.floor(new Date(snapshot.expiry_utc).getTime() / 1000);
  return Number.isFinite(expiryTs) ? { expiryTs } : null;
}

export function buildRegionBetMarketCompareFromChart(
  snapshot: RegionBetGuidedShellSnapshot,
  chartPayload: HorizonChartPayload | null,
): RegionBetMarketComparePayload | null {
  if (!chartPayload || !isRegionBetMarketCompareReady(snapshot)) return null;

  const mappedPayload: HorizonChartPayload = {
    ...chartPayload,
    asset_id: snapshot.asset_id,
    meta: {
      ...chartPayload.meta,
      read_only: true,
      simulation_only: true,
    },
  };

  return {
    schema_version: 1,
    kind: "region_bet_market_compare",
    region_context: {
      asset_id: snapshot.asset_id,
      symbol: snapshot.symbol,
      venue: snapshot.venue,
      expiry_utc: snapshot.expiry_utc,
      window_start_utc: snapshot.window_start_utc,
      window_end_utc: snapshot.window_end_utc,
      price_min_usd: snapshot.selected_region.price_min_usd,
      price_max_usd: snapshot.selected_region.price_max_usd,
    },
    comparison: buildOptionsHorizonComparisonFromChart(mappedPayload),
  };
}
