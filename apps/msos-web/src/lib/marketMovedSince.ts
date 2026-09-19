/**
 * Market moved since v1 — deterministic last-seen versus now for a saved Region Bet.
 * Paper observation only. Does not invent prices, causality, or a next move.
 */

import type {
  RegionBetContract,
  RegionBetFrozenEntrySnapshot,
  RegionBetObservationQuality,
} from "@/lib/regionBet";
import {
  isRegionBetObservationQuality,
  regionBetHasFrozenEntrySnapshot,
  regionBetHasLastSeenSnapshot,
} from "@/lib/regionBet";

export const MARKET_MOVED_SINCE_KIND = "market_moved_since";

export const MARKET_MOVED_SINCE_STALE_AFTER_MS = 6 * 60 * 60 * 1000;

export const MARKET_MOVED_SINCE_LIMITATION =
  "Paper observation only. Last-seen versus now describes recorded inputs. Not financial advice, not a recommendation, and not order execution.";

export type MarketMovedSinceNowObservation = {
  spot_usd?: number | null;
  observed_at_utc?: string | null;
  compared_at_utc?: string | null;
  stale?: boolean;
  trust_state?: string | null;
  quality?: RegionBetObservationQuality | null;
};

export type MarketMovedSinceLastSeenSource =
  | "last_seen_snapshot"
  | "frozen_entry_snapshot"
  | "saved_entry";

export type MarketMovedSinceResolvedLastSeen = {
  spot_usd: number | null;
  observed_at_utc: string | null;
  viewed_at_utc: string | null;
  quality?: RegionBetObservationQuality | null;
  source: MarketMovedSinceLastSeenSource;
};

export type MarketMovedSinceObservation = {
  label: "last_seen" | "now";
  value_usd: number | null;
  display: string;
  observed_at_utc: string | null;
  observed_at_label: string;
  quality: RegionBetObservationQuality;
  quality_label: string;
};

export type MarketMovedSinceDirection = "up" | "down" | "unchanged" | "unavailable";

export type MarketMovedSinceInputStatus =
  | "comparable"
  | "missing"
  | "incomparable"
  | "stale";

export type MarketMovedSinceVsRegion = "inside" | "below" | "above" | "unavailable";

export type MarketMovedSinceSummary = {
  schema_version: 1;
  kind: typeof MARKET_MOVED_SINCE_KIND;
  region_bet_id: string;
  symbol: string;
  last_seen: MarketMovedSinceObservation;
  now: MarketMovedSinceObservation;
  last_seen_at_utc: string | null;
  last_seen_at_label: string;
  now_at_utc: string | null;
  now_at_label: string;
  last_seen_source: MarketMovedSinceLastSeenSource;
  change: {
    direction: MarketMovedSinceDirection;
    direction_label: string;
    delta_usd: number | null;
    delta_display: string;
    delta_pct: number | null;
  };
  input_status: MarketMovedSinceInputStatus;
  input_status_label: string;
  vs_region_last_seen: MarketMovedSinceVsRegion;
  vs_region_now: MarketMovedSinceVsRegion;
  notes: string[];
  limitation: string;
  paper_only: true;
};

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function dollars(value: number): string {
  const rounded = Number.isInteger(value) ? String(value) : value.toFixed(2);
  return `$${rounded}`;
}

function observationDisplay(value: number | null): string {
  return value == null ? "—" : dollars(value);
}

function formatObservedAt(raw: string | null | undefined): string {
  if (typeof raw !== "string") return "unavailable";
  const trimmed = raw.trim();
  if (!trimmed) return "unavailable";
  const parsed = Date.parse(trimmed);
  if (Number.isNaN(parsed)) return trimmed;
  return `${new Date(parsed).toISOString().slice(0, 16).replace("T", " ")} UTC`;
}

function parseUtcMs(raw: string | null | undefined): number | null {
  if (typeof raw !== "string") return null;
  const trimmed = raw.trim();
  if (!trimmed) return null;
  const parsed = Date.parse(trimmed);
  return Number.isNaN(parsed) ? null : parsed;
}

export function labelMarketMovedSinceQuality(
  quality: RegionBetObservationQuality,
): string {
  if (quality === "observed") return "Observed";
  if (quality === "estimated") return "Estimated";
  if (quality === "stale") return "Stale";
  return "Unavailable";
}

export function labelMarketMovedSinceDirection(
  direction: MarketMovedSinceDirection,
): string {
  if (direction === "up") return "Underlying is higher than last seen";
  if (direction === "down") return "Underlying is lower than last seen";
  if (direction === "unchanged") return "Underlying is unchanged versus last seen";
  return "Underlying change is unavailable";
}

export function labelMarketMovedSinceInputStatus(
  status: MarketMovedSinceInputStatus,
): string {
  if (status === "missing") return "Missing input";
  if (status === "incomparable") return "Incomparable inputs";
  if (status === "stale") return "Stale input";
  return "Comparable";
}

function trustHint(trustState: string | null | undefined): RegionBetObservationQuality | null {
  const trust = (trustState ?? "").trim().toLowerCase();
  if (!trust || trust === "ok") return null;
  if (trust === "thin_chain") return "estimated";
  if (trust === "degraded" || trust === "error" || trust === "fail") return "estimated";
  return null;
}

function isStaleByAge(
  observedAtUtc: string | null,
  comparedAtUtc: string | null,
): boolean {
  if (!observedAtUtc || !comparedAtUtc) return false;
  const observed = parseUtcMs(observedAtUtc);
  const compared = parseUtcMs(comparedAtUtc);
  if (observed == null || compared == null) return false;
  return compared - observed >= MARKET_MOVED_SINCE_STALE_AFTER_MS;
}

export function qualifyMarketMovedSinceObservation(input: {
  value_usd?: number | null;
  observed_at_utc?: string | null;
  compared_at_utc?: string | null;
  stale?: boolean;
  trust_state?: string | null;
  quality?: RegionBetObservationQuality | null;
}): {
  value_usd: number | null;
  observed_at_utc: string | null;
  quality: RegionBetObservationQuality;
} {
  const valueUsd = isFiniteNumber(input.value_usd) ? input.value_usd : null;
  const observedAt =
    typeof input.observed_at_utc === "string" && input.observed_at_utc.trim()
      ? input.observed_at_utc.trim()
      : null;
  if (valueUsd == null) {
    return { value_usd: null, observed_at_utc: observedAt, quality: "unavailable" };
  }
  if (input.stale === true || isStaleByAge(observedAt, input.compared_at_utc ?? null)) {
    return { value_usd: valueUsd, observed_at_utc: observedAt, quality: "stale" };
  }
  if (input.quality === "unavailable") {
    return { value_usd: null, observed_at_utc: observedAt, quality: "unavailable" };
  }
  if (isRegionBetObservationQuality(input.quality) && input.quality !== "observed") {
    return { value_usd: valueUsd, observed_at_utc: observedAt, quality: input.quality };
  }
  const hinted = trustHint(input.trust_state);
  if (hinted) {
    return { value_usd: valueUsd, observed_at_utc: observedAt, quality: hinted };
  }
  if (!observedAt) {
    return { value_usd: valueUsd, observed_at_utc: null, quality: "estimated" };
  }
  return { value_usd: valueUsd, observed_at_utc: observedAt, quality: "observed" };
}

function labeledObservation(input: {
  label: "last_seen" | "now";
  value_usd?: number | null;
  observed_at_utc?: string | null;
  compared_at_utc?: string | null;
  stale?: boolean;
  trust_state?: string | null;
  quality?: RegionBetObservationQuality | null;
}): MarketMovedSinceObservation {
  const qualified = qualifyMarketMovedSinceObservation(input);
  return {
    label: input.label,
    value_usd: qualified.value_usd,
    display: observationDisplay(qualified.value_usd),
    observed_at_utc: qualified.observed_at_utc,
    observed_at_label: formatObservedAt(qualified.observed_at_utc),
    quality: qualified.quality,
    quality_label: labelMarketMovedSinceQuality(qualified.quality),
  };
}

export function underlyingVsSelectedRegion(
  spotUsd: number | null,
  regionMinUsd: number,
  regionMaxUsd: number,
): MarketMovedSinceVsRegion {
  if (spotUsd == null || !isFiniteNumber(regionMinUsd) || !isFiniteNumber(regionMaxUsd)) {
    return "unavailable";
  }
  if (spotUsd < regionMinUsd) return "below";
  if (spotUsd > regionMaxUsd) return "above";
  return "inside";
}

export function resolveRegionBetLastSeenSnapshot(
  regionBet: RegionBetContract,
): MarketMovedSinceResolvedLastSeen {
  if (regionBetHasLastSeenSnapshot(regionBet) && regionBet.last_seen_snapshot) {
    const last = regionBet.last_seen_snapshot;
    return {
      spot_usd: isFiniteNumber(last.spot_usd) ? last.spot_usd : null,
      observed_at_utc: last.observed_at_utc?.trim() || last.viewed_at_utc.trim() || null,
      viewed_at_utc: last.viewed_at_utc.trim() || null,
      quality: last.quality,
      source: "last_seen_snapshot",
    };
  }
  if (regionBetHasFrozenEntrySnapshot(regionBet) && regionBet.frozen_entry_snapshot) {
    const frozen = regionBet.frozen_entry_snapshot as RegionBetFrozenEntrySnapshot;
    return {
      spot_usd: isFiniteNumber(frozen.entry.spot_usd) ? frozen.entry.spot_usd : null,
      observed_at_utc: frozen.entry.timestamp_utc,
      viewed_at_utc: frozen.confirmed_at_utc,
      source: "frozen_entry_snapshot",
    };
  }
  return {
    spot_usd: isFiniteNumber(regionBet.entry.spot_usd) ? regionBet.entry.spot_usd : null,
    observed_at_utc: regionBet.entry.timestamp_utc || regionBet.market_snapshot.as_of_utc || null,
    viewed_at_utc: regionBet.lifecycle.updated_at_utc,
    source: "saved_entry",
  };
}

export function mapMarketMovedSinceChange(input: {
  last_seen_usd: number | null;
  now_usd: number | null;
  last_seen_at_utc: string | null;
  now_at_utc: string | null;
  now_quality: RegionBetObservationQuality;
}): {
  direction: MarketMovedSinceDirection;
  delta_usd: number | null;
  delta_pct: number | null;
  input_status: MarketMovedSinceInputStatus;
} {
  if (input.last_seen_usd == null || input.now_usd == null) {
    return {
      direction: "unavailable",
      delta_usd: null,
      delta_pct: null,
      input_status: "missing",
    };
  }
  const lastMs = parseUtcMs(input.last_seen_at_utc);
  const nowMs = parseUtcMs(input.now_at_utc);
  const lastRaw = input.last_seen_at_utc?.trim() ?? "";
  const nowRaw = input.now_at_utc?.trim() ?? "";
  const lastUnparseable = lastRaw.length > 0 && lastMs == null;
  const nowUnparseable = nowRaw.length > 0 && nowMs == null;
  if (lastUnparseable || nowUnparseable || (lastMs != null && nowMs != null && nowMs < lastMs)) {
    return {
      direction: "unavailable",
      delta_usd: null,
      delta_pct: null,
      input_status: "incomparable",
    };
  }
  const deltaUsd = input.now_usd - input.last_seen_usd;
  const deltaPct = input.last_seen_usd === 0 ? null : (deltaUsd / input.last_seen_usd) * 100;
  const direction: MarketMovedSinceDirection =
    deltaUsd > 0 ? "up" : deltaUsd < 0 ? "down" : "unchanged";
  if (input.now_quality === "stale") {
    return {
      direction,
      delta_usd: deltaUsd,
      delta_pct: deltaPct,
      input_status: "stale",
    };
  }
  return {
    direction,
    delta_usd: deltaUsd,
    delta_pct: deltaPct,
    input_status: "comparable",
  };
}

function signedDollars(value: number): string {
  const abs = dollars(Math.abs(value));
  if (value > 0) return `+${abs}`;
  if (value < 0) return `-${abs}`;
  return abs;
}

function deltaDisplay(deltaUsd: number | null): string {
  return deltaUsd == null ? "—" : signedDollars(deltaUsd);
}

function driverForObservation(
  noun: string,
  observation: MarketMovedSinceObservation,
): string {
  if (observation.quality === "unavailable") {
    return `${noun} is unavailable; nothing was fabricated.`;
  }
  return `${noun} is ${observation.display} as of ${observation.observed_at_label} (${observation.quality_label}).`;
}

export function explainMarketMovedSince(value: {
  symbol: string;
  last_seen: MarketMovedSinceObservation;
  now: MarketMovedSinceObservation;
  change: {
    direction: MarketMovedSinceDirection;
    direction_label: string;
    delta_display: string;
  };
  input_status: MarketMovedSinceInputStatus;
  input_status_label: string;
}): string[] {
  return [
    driverForObservation(`Last-seen ${value.symbol} underlying`, value.last_seen),
    driverForObservation(`Now ${value.symbol} underlying`, value.now),
    `Change mapping: ${value.change.direction_label} (${value.change.delta_display}).`,
    `Input status: ${value.input_status_label}.`,
    "These labels describe recorded inputs only; they do not claim causality or recommend an action.",
  ];
}

export function buildMarketMovedSinceNowObservation(
  input: MarketMovedSinceNowObservation,
): MarketMovedSinceNowObservation {
  return {
    spot_usd: isFiniteNumber(input.spot_usd) ? input.spot_usd : null,
    observed_at_utc: input.observed_at_utc?.trim() || null,
    compared_at_utc: input.compared_at_utc?.trim() || null,
    stale: input.stale === true,
    trust_state: input.trust_state?.trim() || null,
    quality: isRegionBetObservationQuality(input.quality) ? input.quality : null,
  };
}

export function buildMarketMovedSinceSummary(
  regionBet: RegionBetContract,
  nowObservation: MarketMovedSinceNowObservation,
): MarketMovedSinceSummary {
  const lastSeen = resolveRegionBetLastSeenSnapshot(regionBet);
  const later = buildMarketMovedSinceNowObservation(nowObservation);
  const symbol = regionBet.asset.symbol ?? regionBet.asset.asset_id;
  const lastSeenObservation = labeledObservation({
    label: "last_seen",
    value_usd: lastSeen.spot_usd,
    observed_at_utc: lastSeen.observed_at_utc,
    quality: lastSeen.quality,
  });
  const nowLabeled = labeledObservation({
    label: "now",
    value_usd: later.spot_usd,
    observed_at_utc: later.observed_at_utc,
    compared_at_utc: later.compared_at_utc,
    stale: later.stale,
    trust_state: later.trust_state,
    quality: later.quality,
  });
  const mapped = mapMarketMovedSinceChange({
    last_seen_usd: lastSeenObservation.value_usd,
    now_usd: nowLabeled.value_usd,
    last_seen_at_utc: lastSeenObservation.observed_at_utc,
    now_at_utc: nowLabeled.observed_at_utc,
    now_quality: nowLabeled.quality,
  });
  const directionLabel = labelMarketMovedSinceDirection(mapped.direction);
  const inputStatusLabel = labelMarketMovedSinceInputStatus(mapped.input_status);
  const change = {
    direction: mapped.direction,
    direction_label: directionLabel,
    delta_usd: mapped.delta_usd,
    delta_display: deltaDisplay(mapped.delta_usd),
    delta_pct: mapped.delta_pct,
  };
  return {
    schema_version: 1,
    kind: MARKET_MOVED_SINCE_KIND,
    region_bet_id: regionBet.id,
    symbol,
    last_seen: lastSeenObservation,
    now: nowLabeled,
    last_seen_at_utc: lastSeenObservation.observed_at_utc,
    last_seen_at_label: lastSeenObservation.observed_at_label,
    now_at_utc: nowLabeled.observed_at_utc,
    now_at_label: nowLabeled.observed_at_label,
    last_seen_source: lastSeen.source,
    change,
    input_status: mapped.input_status,
    input_status_label: inputStatusLabel,
    vs_region_last_seen: underlyingVsSelectedRegion(
      lastSeenObservation.value_usd,
      regionBet.selected_region.price_min_usd,
      regionBet.selected_region.price_max_usd,
    ),
    vs_region_now: underlyingVsSelectedRegion(
      nowLabeled.value_usd,
      regionBet.selected_region.price_min_usd,
      regionBet.selected_region.price_max_usd,
    ),
    notes: explainMarketMovedSince({
      symbol,
      last_seen: lastSeenObservation,
      now: nowLabeled,
      change,
      input_status: mapped.input_status,
      input_status_label: inputStatusLabel,
    }),
    limitation: MARKET_MOVED_SINCE_LIMITATION,
    paper_only: true,
  };
}
