/**
 * Options Horizon region intent — client persistence (simulation only).
 */

export type HorizonRegionBias = "bullish_in_region" | "bearish_in_region" | "neutral";

export type HorizonRegionIntent = {
  schema_version: 1;
  id: string;
  asset_id: string;
  venue: string;
  created_at_utc: string;
  region: {
    time_start_utc: string;
    time_end_utc: string;
    price_min_usd: number;
    price_max_usd: number;
  };
  bias: HorizonRegionBias;
  user_note?: string;
  linked_expiry_ts?: number;
  computed?: {
    implied_mass_pct: number;
    method: string;
    as_of_utc: string;
  };
};

export const HORIZON_REGION_STORAGE_KEY = "msos.horizon.region.v1";

export function newRegionId(): string {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `region-${Date.now()}`;
}

export function saveHorizonRegion(region: HorizonRegionIntent): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(HORIZON_REGION_STORAGE_KEY, JSON.stringify(region));
}

export function loadHorizonRegion(): HorizonRegionIntent | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(HORIZON_REGION_STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as HorizonRegionIntent;
  } catch {
    return null;
  }
}
