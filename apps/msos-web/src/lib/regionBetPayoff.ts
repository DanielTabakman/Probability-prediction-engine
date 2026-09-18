import type { RegionBetContract } from "@/lib/regionBet";
import { isRegionBetGuidedDraftPersistable } from "@/lib/regionBetGuidedShell";

export const REGION_BET_PAYOFF_LIMITATION =
  "Paper-only Region Bet explanation. This is not financial advice, not a recommendation, and not order execution.";

export type RegionBetPayoffScenario = {
  id: "inside_region" | "below_region" | "above_region";
  label: string;
  copy: string;
};

export type RegionBetPayoffExplanation = {
  schema_version: 1;
  expression_id: string;
  headline: string;
  payoff_copy: string;
  scenario_copy: RegionBetPayoffScenario[];
  limitation: string;
};

export type RegionBetPayoffConfirmation = {
  confirmed: boolean;
};

function dollars(value: number): string {
  return `$${value.toLocaleString("en-US", {
    maximumFractionDigits: 2,
    minimumFractionDigits: Number.isInteger(value) ? 0 : 2,
  })}`;
}

function shortDate(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toISOString().slice(0, 10);
}

function expressionLabel(regionBet: RegionBetContract): string {
  return regionBet.selected_expression_ref?.expression_id.trim() || "unselected expression";
}

export function buildRegionBetPayoffExplanation(
  regionBet: RegionBetContract,
): RegionBetPayoffExplanation | null {
  const expression = regionBet.selected_expression_ref;
  if (!expression?.expression_id.trim()) return null;
  const region = regionBet.selected_region;
  const symbol = regionBet.asset.symbol ?? regionBet.asset.asset_id;
  const range = `${dollars(region.price_min_usd)} to ${dollars(region.price_max_usd)}`;
  const window = `${shortDate(region.time_start_utc)} through ${shortDate(region.time_end_utc)}`;
  const maxLoss = regionBet.risk_constraints.max_loss_usd;
  const premium = regionBet.risk_constraints.max_premium_usd;
  const limits = [
    typeof maxLoss === "number" && Number.isFinite(maxLoss)
      ? `max loss ${dollars(maxLoss)}`
      : null,
    typeof premium === "number" && Number.isFinite(premium)
      ? `premium budget ${dollars(premium)}`
      : null,
    regionBet.risk_constraints.payoff_preference
      ? `preference ${regionBet.risk_constraints.payoff_preference}`
      : null,
  ]
    .filter(Boolean)
    .join(", ");

  return {
    schema_version: 1,
    expression_id: expression.expression_id,
    headline: `${expression.expression_id} maps ${symbol} to the selected paper region.`,
    payoff_copy: `${expression.expression_id} is saved as a paper expression for ${symbol}. The target region is ${range} during ${window}${limits ? ` with ${limits}` : ""}.`,
    scenario_copy: [
      {
        id: "inside_region",
        label: "Inside region",
        copy: `If ${symbol} is inside ${range} during the selected window, this paper expression is the saved monitor object for that thesis.`,
      },
      {
        id: "below_region",
        label: "Below region",
        copy: `If ${symbol} is below ${dollars(region.price_min_usd)}, the monitor records that the market finished outside the lower edge of the selected region.`,
      },
      {
        id: "above_region",
        label: "Above region",
        copy: `If ${symbol} is above ${dollars(region.price_max_usd)}, the monitor records that the market finished outside the upper edge of the selected region.`,
      },
    ],
    limitation: REGION_BET_PAYOFF_LIMITATION,
  };
}

export function buildRegionBetFrozenEntrySnapshot(
  regionBet: RegionBetContract,
  confirmedAtUtc: string,
): NonNullable<RegionBetContract["frozen_entry_snapshot"]> | null {
  const expression = regionBet.selected_expression_ref;
  if (!expression?.expression_id.trim()) return null;
  return {
    confirmed_at_utc: confirmedAtUtc,
    entry: {
      spot_usd: regionBet.entry.spot_usd,
      timestamp_utc: regionBet.entry.timestamp_utc,
    },
    market_snapshot: {
      as_of_utc: regionBet.market_snapshot.as_of_utc,
      source: regionBet.market_snapshot.source,
      method: regionBet.market_snapshot.method,
      implied_probability_pct: regionBet.market_snapshot.implied_probability_pct,
      implied_move_pct: regionBet.market_snapshot.implied_move_pct,
    },
    risk_constraints: {
      max_loss_usd: regionBet.risk_constraints.max_loss_usd,
      max_premium_usd: regionBet.risk_constraints.max_premium_usd,
      position_size_usd: regionBet.risk_constraints.position_size_usd,
      payoff_preference: regionBet.risk_constraints.payoff_preference,
      notes: regionBet.risk_constraints.notes,
    },
    selected_region: {
      time_start_utc: regionBet.selected_region.time_start_utc,
      time_end_utc: regionBet.selected_region.time_end_utc,
      price_min_usd: regionBet.selected_region.price_min_usd,
      price_max_usd: regionBet.selected_region.price_max_usd,
    },
    selected_expression_ref: {
      expression_id: expression.expression_id,
      source: expression.source,
    },
  };
}

export function canConfirmRegionBetPayoff(regionBet: RegionBetContract): boolean {
  const constraints = regionBet.risk_constraints;
  return (
    isRegionBetGuidedDraftPersistable(regionBet) &&
    Boolean(regionBet.selected_expression_ref?.expression_id.trim()) &&
    typeof constraints.max_loss_usd === "number" &&
    Number.isFinite(constraints.max_loss_usd) &&
    constraints.max_loss_usd > 0 &&
    typeof constraints.max_premium_usd === "number" &&
    Number.isFinite(constraints.max_premium_usd) &&
    constraints.max_premium_usd > 0 &&
    constraints.max_premium_usd <= constraints.max_loss_usd &&
    Boolean(constraints.payoff_preference?.trim()) &&
    Boolean(buildRegionBetPayoffExplanation(regionBet))
  );
}

export function confirmRegionBetPayoff(
  regionBet: RegionBetContract,
  confirmation: RegionBetPayoffConfirmation,
  now: Date = new Date(),
): RegionBetContract | null {
  if (!confirmation.confirmed || !canConfirmRegionBetPayoff(regionBet)) return null;
  const confirmedAt = now.toISOString();
  const frozen = buildRegionBetFrozenEntrySnapshot(regionBet, confirmedAt);
  if (!frozen) return null;
  return {
    ...regionBet,
    frozen_entry_snapshot: frozen,
    lifecycle: {
      ...regionBet.lifecycle,
      status: "active",
      updated_at_utc: confirmedAt,
    },
  };
}

export function regionBetFrozenSnapshotKey(
  snapshot: RegionBetContract["frozen_entry_snapshot"],
): string {
  return JSON.stringify(snapshot ?? null);
}
