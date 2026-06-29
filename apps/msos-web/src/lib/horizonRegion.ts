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

export const HORIZON_REGION_PERSISTENCE_LABEL =
  "Saved to your workspace — simulation only, not order execution.";

export function newRegionId(): string {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `region-${Date.now()}`;
}

export function isHorizonRegionIntent(value: unknown): value is HorizonRegionIntent {
  if (!value || typeof value !== "object") return false;
  const row = value as Record<string, unknown>;
  const region = row.region;
  if (!region || typeof region !== "object") return false;
  const box = region as Record<string, unknown>;
  return (
    row.schema_version === 1 &&
    typeof row.id === "string" &&
    typeof row.asset_id === "string" &&
    typeof row.venue === "string" &&
    typeof row.created_at_utc === "string" &&
    typeof box.time_start_utc === "string" &&
    typeof box.time_end_utc === "string" &&
    typeof box.price_min_usd === "number" &&
    typeof box.price_max_usd === "number" &&
    (row.bias === "bullish_in_region" ||
      row.bias === "bearish_in_region" ||
      row.bias === "neutral")
  );
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
    const parsed: unknown = JSON.parse(raw);
    return isHorizonRegionIntent(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

export async function fetchHorizonRegion(): Promise<HorizonRegionIntent | null> {
  if (typeof window === "undefined") return null;
  try {
    const response = await fetch("/api/theses/horizon-region", {
      cache: "no-store",
      credentials: "include",
    });
    if (!response.ok) {
      return loadHorizonRegion();
    }
    const payload = (await response.json()) as { region?: HorizonRegionIntent | null };
    if (payload.region && isHorizonRegionIntent(payload.region)) {
      saveHorizonRegion(payload.region);
      return payload.region;
    }
    const local = loadHorizonRegion();
    if (local) {
      await persistHorizonRegion(local);
      return local;
    }
    return null;
  } catch {
    return loadHorizonRegion();
  }
}

export async function persistHorizonRegion(region: HorizonRegionIntent): Promise<boolean> {
  saveHorizonRegion(region);
  if (typeof window === "undefined") return true;
  try {
    const response = await fetch("/api/theses/horizon-region", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ region }),
    });
    return response.ok;
  } catch {
    return false;
  }
}
