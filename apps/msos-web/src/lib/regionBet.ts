/**
 * Region Bet contract v1 - durable workspace object (simulation only).
 */

export type RegionBetStatus = "draft" | "active" | "monitoring" | "closed" | "archived";

export type RegionBetContract = {
  schema_version: 1;
  id: string;
  asset: {
    asset_id: string;
    symbol?: string;
    venue?: string;
  };
  entry: {
    spot_usd: number;
    timestamp_utc: string;
  };
  selected_region: {
    time_start_utc: string;
    time_end_utc: string;
    price_min_usd: number;
    price_max_usd: number;
  };
  target: {
    expiry_utc: string;
    window_start_utc?: string;
    window_end_utc?: string;
  };
  market_snapshot: {
    as_of_utc: string;
    source?: string;
    method?: string;
    implied_probability_pct?: number;
    implied_move_pct?: number;
  };
  risk_constraints: {
    max_loss_usd?: number;
    max_premium_usd?: number;
    position_size_usd?: number;
    payoff_preference?: string;
    notes?: string;
  };
  selected_expression_ref: {
    expression_id: string;
    source?: string;
  } | null;
  frozen_entry_snapshot?: {
    confirmed_at_utc: string;
    entry: {
      spot_usd: number;
      timestamp_utc: string;
    };
    market_snapshot: {
      as_of_utc: string;
      source?: string;
      method?: string;
      implied_probability_pct?: number;
      implied_move_pct?: number;
    };
    risk_constraints: {
      max_loss_usd?: number;
      max_premium_usd?: number;
      position_size_usd?: number;
      payoff_preference?: string;
      notes?: string;
    };
    selected_region: {
      time_start_utc: string;
      time_end_utc: string;
      price_min_usd: number;
      price_max_usd: number;
    };
    selected_expression_ref: {
      expression_id: string;
      source?: string;
    };
  };
  last_seen_snapshot?: {
    viewed_at_utc: string;
    spot_usd?: number;
    observed_at_utc?: string;
    quality?: RegionBetObservationQuality;
    source?: string;
    implied_probability_pct?: number;
    implied_move_pct?: number;
  };
  lifecycle: {
    status: RegionBetStatus;
    created_at_utc: string;
    updated_at_utc: string;
    closed_at_utc?: string;
  };
  user_note?: string;
  guided_step?: "asset" | "window" | "region" | "compare" | "review";
};

export type PersistRegionBetOptions = {
  confirmPayoff?: boolean;
};

export type RegionBetFrozenEntrySnapshot = NonNullable<
  RegionBetContract["frozen_entry_snapshot"]
>;

export type RegionBetLastSeenSnapshot = NonNullable<
  RegionBetContract["last_seen_snapshot"]
>;

export const REGION_BET_OBSERVATION_QUALITIES = [
  "observed",
  "estimated",
  "stale",
  "unavailable",
] as const;

export type RegionBetObservationQuality =
  (typeof REGION_BET_OBSERVATION_QUALITIES)[number];

export function isRegionBetObservationQuality(
  value: unknown,
): value is RegionBetObservationQuality {
  return (
    value === "observed" ||
    value === "estimated" ||
    value === "stale" ||
    value === "unavailable"
  );
}

export function regionBetHasFrozenEntrySnapshot(
  regionBet: Pick<RegionBetContract, "frozen_entry_snapshot">,
): boolean {
  return regionBet.frozen_entry_snapshot !== undefined;
}

export function regionBetHasLastSeenSnapshot(
  regionBet: Pick<RegionBetContract, "last_seen_snapshot">,
): boolean {
  return regionBet.last_seen_snapshot !== undefined;
}

export function buildRegionBetLastSeenSnapshot(input: {
  viewed_at_utc: string;
  spot_usd?: number | null;
  observed_at_utc?: string | null;
  quality?: RegionBetObservationQuality | null;
  source?: string | null;
  implied_probability_pct?: number | null;
  implied_move_pct?: number | null;
}): RegionBetLastSeenSnapshot | null {
  const viewedAt = input.viewed_at_utc.trim();
  if (!viewedAt) return null;
  const snapshot: RegionBetLastSeenSnapshot = { viewed_at_utc: viewedAt };
  if (isFiniteNumber(input.spot_usd)) snapshot.spot_usd = input.spot_usd;
  if (typeof input.observed_at_utc === "string" && input.observed_at_utc.trim()) {
    snapshot.observed_at_utc = input.observed_at_utc.trim();
  }
  if (isRegionBetObservationQuality(input.quality)) snapshot.quality = input.quality;
  if (typeof input.source === "string" && input.source.trim()) {
    snapshot.source = input.source.trim();
  }
  if (isFiniteNumber(input.implied_probability_pct)) {
    snapshot.implied_probability_pct = input.implied_probability_pct;
  }
  if (isFiniteNumber(input.implied_move_pct)) {
    snapshot.implied_move_pct = input.implied_move_pct;
  }
  return snapshot;
}

export const REGION_BET_STORAGE_KEY = "msos.region.bet.v1";

export const REGION_BET_PERSISTENCE_LABEL =
  "Saved to your workspace - simulation only, not order execution.";

export function newRegionBetId(): string {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `region-bet-${Date.now()}`;
}

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function isOptionalFiniteNumber(value: unknown): value is number | undefined {
  return value === undefined || isFiniteNumber(value);
}

function isOptionalString(value: unknown): value is string | undefined {
  return value === undefined || typeof value === "string";
}

function isRegionBetStatus(value: unknown): value is RegionBetStatus {
  return (
    value === "draft" ||
    value === "active" ||
    value === "monitoring" ||
    value === "closed" ||
    value === "archived"
  );
}

function isRegionBetLastSeenSnapshot(
  value: unknown,
): value is RegionBetLastSeenSnapshot {
  if (!value || typeof value !== "object") return false;
  const row = value as Record<string, unknown>;
  return (
    typeof row.viewed_at_utc === "string" &&
    isOptionalFiniteNumber(row.spot_usd) &&
    isOptionalString(row.observed_at_utc) &&
    (row.quality === undefined || isRegionBetObservationQuality(row.quality)) &&
    isOptionalString(row.source) &&
    isOptionalFiniteNumber(row.implied_probability_pct) &&
    isOptionalFiniteNumber(row.implied_move_pct)
  );
}

function isRegionBetFrozenEntrySnapshot(
  value: unknown,
): value is RegionBetFrozenEntrySnapshot {
  if (!value || typeof value !== "object") return false;
  const row = value as Record<string, unknown>;
  const entry = row.entry;
  const marketSnapshot = row.market_snapshot;
  const riskConstraints = row.risk_constraints;
  const selectedRegion = row.selected_region;
  const expressionRef = row.selected_expression_ref;
  if (
    !entry ||
    typeof entry !== "object" ||
    !marketSnapshot ||
    typeof marketSnapshot !== "object" ||
    !riskConstraints ||
    typeof riskConstraints !== "object" ||
    !selectedRegion ||
    typeof selectedRegion !== "object" ||
    !expressionRef ||
    typeof expressionRef !== "object"
  ) {
    return false;
  }
  const entryRow = entry as Record<string, unknown>;
  const marketSnapshotRow = marketSnapshot as Record<string, unknown>;
  const riskRow = riskConstraints as Record<string, unknown>;
  const selectedRegionRow = selectedRegion as Record<string, unknown>;
  const expressionRow = expressionRef as Record<string, unknown>;
  return (
    typeof row.confirmed_at_utc === "string" &&
    isFiniteNumber(entryRow.spot_usd) &&
    typeof entryRow.timestamp_utc === "string" &&
    typeof marketSnapshotRow.as_of_utc === "string" &&
    isOptionalString(marketSnapshotRow.source) &&
    isOptionalString(marketSnapshotRow.method) &&
    isOptionalFiniteNumber(marketSnapshotRow.implied_probability_pct) &&
    isOptionalFiniteNumber(marketSnapshotRow.implied_move_pct) &&
    isOptionalFiniteNumber(riskRow.max_loss_usd) &&
    isOptionalFiniteNumber(riskRow.max_premium_usd) &&
    isOptionalFiniteNumber(riskRow.position_size_usd) &&
    isOptionalString(riskRow.payoff_preference) &&
    isOptionalString(riskRow.notes) &&
    typeof selectedRegionRow.time_start_utc === "string" &&
    typeof selectedRegionRow.time_end_utc === "string" &&
    isFiniteNumber(selectedRegionRow.price_min_usd) &&
    isFiniteNumber(selectedRegionRow.price_max_usd) &&
    typeof expressionRow.expression_id === "string" &&
    isOptionalString(expressionRow.source)
  );
}

export function isRegionBetContract(value: unknown): value is RegionBetContract {
  if (!value || typeof value !== "object") return false;
  const row = value as Record<string, unknown>;
  const asset = row.asset;
  const entry = row.entry;
  const selectedRegion = row.selected_region;
  const target = row.target;
  const marketSnapshot = row.market_snapshot;
  const riskConstraints = row.risk_constraints;
  const expressionRef = row.selected_expression_ref;
  const lifecycle = row.lifecycle;
  if (
    !asset ||
    typeof asset !== "object" ||
    !entry ||
    typeof entry !== "object" ||
    !selectedRegion ||
    typeof selectedRegion !== "object" ||
    !target ||
    typeof target !== "object" ||
    !marketSnapshot ||
    typeof marketSnapshot !== "object" ||
    !riskConstraints ||
    typeof riskConstraints !== "object" ||
    !lifecycle ||
    typeof lifecycle !== "object"
  ) {
    return false;
  }
  const assetRow = asset as Record<string, unknown>;
  const entryRow = entry as Record<string, unknown>;
  const selectedRegionRow = selectedRegion as Record<string, unknown>;
  const targetRow = target as Record<string, unknown>;
  const marketSnapshotRow = marketSnapshot as Record<string, unknown>;
  const riskRow = riskConstraints as Record<string, unknown>;
  const lifecycleRow = lifecycle as Record<string, unknown>;

  const expressionRefValid =
    expressionRef === null ||
    (!!expressionRef &&
      typeof expressionRef === "object" &&
      typeof (expressionRef as Record<string, unknown>).expression_id === "string" &&
      isOptionalString((expressionRef as Record<string, unknown>).source));

  return (
    row.schema_version === 1 &&
    typeof row.id === "string" &&
    typeof assetRow.asset_id === "string" &&
    isOptionalString(assetRow.symbol) &&
    isOptionalString(assetRow.venue) &&
    isFiniteNumber(entryRow.spot_usd) &&
    typeof entryRow.timestamp_utc === "string" &&
    typeof selectedRegionRow.time_start_utc === "string" &&
    typeof selectedRegionRow.time_end_utc === "string" &&
    isFiniteNumber(selectedRegionRow.price_min_usd) &&
    isFiniteNumber(selectedRegionRow.price_max_usd) &&
    typeof targetRow.expiry_utc === "string" &&
    isOptionalString(targetRow.window_start_utc) &&
    isOptionalString(targetRow.window_end_utc) &&
    typeof marketSnapshotRow.as_of_utc === "string" &&
    isOptionalString(marketSnapshotRow.source) &&
    isOptionalString(marketSnapshotRow.method) &&
    isOptionalFiniteNumber(marketSnapshotRow.implied_probability_pct) &&
    isOptionalFiniteNumber(marketSnapshotRow.implied_move_pct) &&
    isOptionalFiniteNumber(riskRow.max_loss_usd) &&
    isOptionalFiniteNumber(riskRow.max_premium_usd) &&
    isOptionalFiniteNumber(riskRow.position_size_usd) &&
    isOptionalString(riskRow.payoff_preference) &&
    isOptionalString(riskRow.notes) &&
    expressionRefValid &&
    (row.frozen_entry_snapshot === undefined ||
      isRegionBetFrozenEntrySnapshot(row.frozen_entry_snapshot)) &&
    (row.last_seen_snapshot === undefined ||
      isRegionBetLastSeenSnapshot(row.last_seen_snapshot)) &&
    isRegionBetStatus(lifecycleRow.status) &&
    typeof lifecycleRow.created_at_utc === "string" &&
    typeof lifecycleRow.updated_at_utc === "string" &&
    isOptionalString(lifecycleRow.closed_at_utc) &&
    isOptionalString(row.user_note)
  );
}

export function saveRegionBet(regionBet: RegionBetContract): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(REGION_BET_STORAGE_KEY, JSON.stringify(regionBet));
}

export function loadRegionBet(): RegionBetContract | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(REGION_BET_STORAGE_KEY);
    if (!raw) return null;
    const parsed: unknown = JSON.parse(raw);
    return isRegionBetContract(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

export async function fetchRegionBet(): Promise<RegionBetContract | null> {
  if (typeof window === "undefined") return null;
  try {
    const response = await fetch("/api/theses/region-bet", {
      cache: "no-store",
      credentials: "include",
    });
    if (!response.ok) {
      return loadRegionBet();
    }
    const payload = (await response.json()) as { regionBet?: RegionBetContract | null };
    if (payload.regionBet && isRegionBetContract(payload.regionBet)) {
      saveRegionBet(payload.regionBet);
      return payload.regionBet;
    }
    const local = loadRegionBet();
    if (local) {
      await persistRegionBet(local);
      return local;
    }
    return null;
  } catch {
    return loadRegionBet();
  }
}

export async function persistRegionBet(
  regionBet: RegionBetContract,
  options: PersistRegionBetOptions = {},
): Promise<boolean> {
  saveRegionBet(regionBet);
  if (typeof window === "undefined") return true;
  try {
    const response = await fetch("/api/theses/region-bet", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ regionBet, confirmPayoff: options.confirmPayoff === true }),
    });
    return response.ok;
  } catch {
    return false;
  }
}
