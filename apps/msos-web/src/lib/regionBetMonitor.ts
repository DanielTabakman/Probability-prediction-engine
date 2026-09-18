/**
 * Region Bet monitor value v1 — honest then/now mapping for Monitor.
 * Paper observation only. Does not invent marks, timestamps, or advice.
 */

import type {
  RegionBetContract,
  RegionBetFrozenEntrySnapshot,
  RegionBetObservationQuality,
} from "@/lib/regionBet";
import {
  isRegionBetObservationQuality,
  regionBetHasFrozenEntrySnapshot,
} from "@/lib/regionBet";
import { isRegionBetMonitorable } from "@/lib/regionBetPayoff";

export const REGION_BET_MONITOR_KIND = "region_bet_monitor_value";

export const REGION_BET_MONITOR_STALE_AFTER_MS = 6 * 60 * 60 * 1000;

export const REGION_BET_MONITOR_LIMITATION =
  "Paper observation only. Underlying then/now is separate from paper-expression then/now. Not financial advice, not a recommendation, and not order execution.";

export type RegionBetLaterObservation = {
  spot_usd?: number | null;
  observed_at_utc?: string | null;
  compared_at_utc?: string | null;
  stale?: boolean;
  trust_state?: string | null;
  quality?: RegionBetObservationQuality | null;
  expression_value_usd?: number | null;
  expression_observed_at_utc?: string | null;
  entry_expression_value_usd?: number | null;
  entry_expression_observed_at_utc?: string | null;
};

export type RegionBetLabeledObservation = {
  label: "entry" | "current";
  kind: "underlying" | "paper_expression";
  value_usd: number | null;
  display: string;
  observed_at_utc: string | null;
  observed_at_label: string;
  quality: RegionBetObservationQuality;
  quality_label: string;
};

export type RegionBetMonitorVsRegion = "inside" | "below" | "above" | "unavailable";

export type RegionBetMonitorValue = {
  schema_version: 1;
  kind: typeof REGION_BET_MONITOR_KIND;
  region_bet_id: string;
  symbol: string;
  expression_id: string | null;
  underlying: {
    entry: RegionBetLabeledObservation;
    current: RegionBetLabeledObservation;
    vs_region: RegionBetMonitorVsRegion;
    vs_region_label: string;
    region_min_usd: number;
    region_max_usd: number;
  };
  expression: {
    entry: RegionBetLabeledObservation;
    current: RegionBetLabeledObservation;
  };
  value_drivers: string[];
  limitation: string;
};

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function dollars(value: number): string {
  const rounded = Number.isInteger(value) ? String(value) : value.toFixed(2);
  return `$${rounded}`;
}

function formatObservedAt(raw: string | null | undefined): string {
  if (typeof raw !== "string") return "unavailable";
  const trimmed = raw.trim();
  if (!trimmed) return "unavailable";
  const parsed = Date.parse(trimmed);
  if (Number.isNaN(parsed)) return trimmed;
  return `${new Date(parsed).toISOString().slice(0, 16).replace("T", " ")} UTC`;
}

export function labelRegionBetObservationQuality(
  quality: RegionBetObservationQuality,
): string {
  if (quality === "observed") return "Observed";
  if (quality === "estimated") return "Estimated";
  if (quality === "stale") return "Stale";
  return "Unavailable";
}

function observationDisplay(value: number | null): string {
  return value == null ? "—" : dollars(value);
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
  const observed = Date.parse(observedAtUtc);
  const compared = Date.parse(comparedAtUtc);
  if (Number.isNaN(observed) || Number.isNaN(compared)) return false;
  return compared - observed >= REGION_BET_MONITOR_STALE_AFTER_MS;
}

export function qualifyRegionBetObservation(input: {
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
  label: "entry" | "current";
  kind: "underlying" | "paper_expression";
  value_usd?: number | null;
  observed_at_utc?: string | null;
  compared_at_utc?: string | null;
  stale?: boolean;
  trust_state?: string | null;
  quality?: RegionBetObservationQuality | null;
}): RegionBetLabeledObservation {
  const qualified = qualifyRegionBetObservation(input);
  return {
    label: input.label,
    kind: input.kind,
    value_usd: qualified.value_usd,
    display: observationDisplay(qualified.value_usd),
    observed_at_utc: qualified.observed_at_utc,
    observed_at_label: formatObservedAt(qualified.observed_at_utc),
    quality: qualified.quality,
    quality_label: labelRegionBetObservationQuality(qualified.quality),
  };
}

export function underlyingVsSelectedRegion(
  spotUsd: number | null,
  regionMinUsd: number,
  regionMaxUsd: number,
): RegionBetMonitorVsRegion {
  if (spotUsd == null || !isFiniteNumber(regionMinUsd) || !isFiniteNumber(regionMaxUsd)) {
    return "unavailable";
  }
  if (spotUsd < regionMinUsd) return "below";
  if (spotUsd > regionMaxUsd) return "above";
  return "inside";
}

function vsRegionLabel(status: RegionBetMonitorVsRegion): string {
  if (status === "inside") return "Inside selected region";
  if (status === "below") return "Below selected region";
  if (status === "above") return "Above selected region";
  return "Region position unavailable";
}

function driverForObservation(
  noun: string,
  observation: RegionBetLabeledObservation,
): string {
  if (observation.quality === "unavailable") {
    return `${noun} is unavailable; nothing was fabricated.`;
  }
  return `${noun} is ${observation.display} as of ${observation.observed_at_label} (${observation.quality_label}).`;
}

export function explainRegionBetValueDrivers(value: {
  symbol: string;
  expression_id: string | null;
  underlying: {
    entry: RegionBetLabeledObservation;
    current: RegionBetLabeledObservation;
    vs_region: RegionBetMonitorVsRegion;
    region_min_usd: number;
    region_max_usd: number;
  };
  expression: {
    entry: RegionBetLabeledObservation;
    current: RegionBetLabeledObservation;
  };
}): string[] {
  const range = `${dollars(value.underlying.region_min_usd)} to ${dollars(value.underlying.region_max_usd)}`;
  const vsRegion =
    value.underlying.vs_region === "unavailable"
      ? "Current underlying cannot be placed against the selected paper region because that observation is unavailable."
      : `Current ${value.symbol} is ${value.underlying.vs_region} the selected paper region ${range}.`;
  const expressionId = value.expression_id?.trim() || "the selected paper expression";
  return [
    driverForObservation(`Entry ${value.symbol} underlying`, value.underlying.entry),
    driverForObservation(`Current ${value.symbol} underlying`, value.underlying.current),
    vsRegion,
    driverForObservation(`Entry value for ${expressionId}`, value.expression.entry),
    driverForObservation(`Current value for ${expressionId}`, value.expression.current),
    "A matching underlying path and a paper-expression money outcome are separate observations.",
    "These labels describe recorded inputs only; they do not claim causality or recommend an action.",
  ];
}

export function buildRegionBetLaterObservation(
  input: RegionBetLaterObservation,
): RegionBetLaterObservation {
  return {
    spot_usd: isFiniteNumber(input.spot_usd) ? input.spot_usd : null,
    observed_at_utc: input.observed_at_utc?.trim() || null,
    compared_at_utc: input.compared_at_utc?.trim() || null,
    stale: input.stale === true,
    trust_state: input.trust_state?.trim() || null,
    quality: isRegionBetObservationQuality(input.quality) ? input.quality : null,
    expression_value_usd: isFiniteNumber(input.expression_value_usd)
      ? input.expression_value_usd
      : null,
    expression_observed_at_utc: input.expression_observed_at_utc?.trim() || null,
    entry_expression_value_usd: isFiniteNumber(input.entry_expression_value_usd)
      ? input.entry_expression_value_usd
      : null,
    entry_expression_observed_at_utc: input.entry_expression_observed_at_utc?.trim() || null,
  };
}

export function buildRegionBetMonitorValue(
  regionBet: RegionBetContract,
  laterObservation: RegionBetLaterObservation,
): RegionBetMonitorValue | null {
  if (!isRegionBetMonitorable(regionBet) || !regionBetHasFrozenEntrySnapshot(regionBet)) {
    return null;
  }
  const frozen = regionBet.frozen_entry_snapshot as RegionBetFrozenEntrySnapshot;
  const later = buildRegionBetLaterObservation(laterObservation);
  const symbol = regionBet.asset.symbol ?? regionBet.asset.asset_id;
  const expressionId = frozen.selected_expression_ref.expression_id.trim() || null;
  const underlyingEntry = labeledObservation({
    label: "entry",
    kind: "underlying",
    value_usd: frozen.entry.spot_usd,
    observed_at_utc: frozen.entry.timestamp_utc,
  });
  const underlyingCurrent = labeledObservation({
    label: "current",
    kind: "underlying",
    value_usd: later.spot_usd,
    observed_at_utc: later.observed_at_utc,
    compared_at_utc: later.compared_at_utc,
    stale: later.stale,
    trust_state: later.trust_state,
    quality: later.quality,
  });
  const expressionEntry = labeledObservation({
    label: "entry",
    kind: "paper_expression",
    value_usd: later.entry_expression_value_usd,
    observed_at_utc: later.entry_expression_observed_at_utc,
  });
  const expressionCurrent = labeledObservation({
    label: "current",
    kind: "paper_expression",
    value_usd: later.expression_value_usd,
    observed_at_utc: later.expression_observed_at_utc,
    compared_at_utc: later.compared_at_utc,
    stale: later.stale,
    quality: later.quality,
  });
  const vsRegion = underlyingVsSelectedRegion(
    underlyingCurrent.value_usd,
    frozen.selected_region.price_min_usd,
    frozen.selected_region.price_max_usd,
  );
  const value = {
    symbol,
    expression_id: expressionId,
    underlying: {
      entry: underlyingEntry,
      current: underlyingCurrent,
      vs_region: vsRegion,
      region_min_usd: frozen.selected_region.price_min_usd,
      region_max_usd: frozen.selected_region.price_max_usd,
    },
    expression: {
      entry: expressionEntry,
      current: expressionCurrent,
    },
  };
  return {
    schema_version: 1,
    kind: REGION_BET_MONITOR_KIND,
    region_bet_id: regionBet.id,
    symbol,
    expression_id: expressionId,
    underlying: {
      ...value.underlying,
      vs_region_label: vsRegionLabel(vsRegion),
    },
    expression: value.expression,
    value_drivers: explainRegionBetValueDrivers(value),
    limitation: REGION_BET_MONITOR_LIMITATION,
  };
}
