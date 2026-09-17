import {
  isRegionBetContract,
  newRegionBetId,
  type RegionBetContract,
} from "@/lib/regionBet";

export type RegionBetGuidedShellStep = "asset" | "window" | "region" | "compare" | "review";

export type RegionBetGuidedShellStepDef = {
  id: RegionBetGuidedShellStep;
  label: string;
};

export type RegionBetGuidedShellSnapshot = {
  asset_id: string;
  symbol?: string;
  venue?: string;
  expiry_utc: string;
  window_start_utc?: string;
  window_end_utc?: string;
  selected_region: RegionBetContract["selected_region"];
};

export type RegionBetGuidedShellPatch = {
  asset?: Partial<RegionBetContract["asset"]>;
  entry?: Partial<RegionBetContract["entry"]>;
  target?: Partial<RegionBetContract["target"]>;
  selected_region?: Partial<RegionBetContract["selected_region"]>;
  market_snapshot?: Partial<RegionBetContract["market_snapshot"]>;
  risk_constraints?: Partial<RegionBetContract["risk_constraints"]>;
  selected_expression_ref?: RegionBetContract["selected_expression_ref"];
  user_note?: string;
};

export const REGION_BET_GUIDED_SHELL_STEPS: RegionBetGuidedShellStepDef[] = [
  { id: "asset", label: "Asset" },
  { id: "window", label: "Window" },
  { id: "region", label: "Region" },
  { id: "compare", label: "Compare" },
  { id: "review", label: "Review" },
];

const DEFAULT_ASSET_ID = "ETH";
const DEFAULT_VENUE = "Deribit";
const DEFAULT_SPOT_USD = 3000;
const DEFAULT_REGION_WIDTH_PCT = 0.08;

function isoDaysFrom(now: Date, days: number): string {
  const next = new Date(now);
  next.setUTCDate(next.getUTCDate() + days);
  next.setUTCHours(16, 0, 0, 0);
  return next.toISOString();
}

function finiteOrFallback(value: unknown, fallback: number): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function normalizeDate(value: string | undefined, fallback: string): string {
  if (!value) return fallback;
  return Number.isNaN(Date.parse(value)) ? fallback : new Date(value).toISOString();
}

function normalizeStepIndex(step: RegionBetGuidedShellStep): number {
  const index = REGION_BET_GUIDED_SHELL_STEPS.findIndex((item) => item.id === step);
  return index < 0 ? 0 : index;
}

export function regionBetGuidedShellStepIndex(step: RegionBetGuidedShellStep): number {
  return normalizeStepIndex(step);
}

export function nextRegionBetGuidedShellStep(
  step: RegionBetGuidedShellStep,
): RegionBetGuidedShellStep {
  const nextIndex = Math.min(
    normalizeStepIndex(step) + 1,
    REGION_BET_GUIDED_SHELL_STEPS.length - 1,
  );
  return REGION_BET_GUIDED_SHELL_STEPS[nextIndex].id;
}

export function previousRegionBetGuidedShellStep(
  step: RegionBetGuidedShellStep,
): RegionBetGuidedShellStep {
  const previousIndex = Math.max(normalizeStepIndex(step) - 1, 0);
  return REGION_BET_GUIDED_SHELL_STEPS[previousIndex].id;
}

export function createRegionBetGuidedDraft(
  seed?: Partial<RegionBetContract> | null,
  now: Date = new Date(),
): RegionBetContract {
  const createdAt = normalizeDate(seed?.lifecycle?.created_at_utc, now.toISOString());
  const entryTimestamp = normalizeDate(seed?.entry?.timestamp_utc, now.toISOString());
  const expiry = normalizeDate(seed?.target?.expiry_utc, isoDaysFrom(now, 30));
  const windowStart = normalizeDate(seed?.target?.window_start_utc, expiry);
  const windowEnd = normalizeDate(seed?.target?.window_end_utc, expiry);
  const spot = finiteOrFallback(seed?.entry?.spot_usd, DEFAULT_SPOT_USD);
  const priceMin = finiteOrFallback(
    seed?.selected_region?.price_min_usd,
    Math.round(spot * (1 - DEFAULT_REGION_WIDTH_PCT)),
  );
  const priceMax = finiteOrFallback(
    seed?.selected_region?.price_max_usd,
    Math.round(spot * (1 + DEFAULT_REGION_WIDTH_PCT)),
  );

  return {
    schema_version: 1,
    id: seed?.id ?? newRegionBetId(),
    asset: {
      asset_id: seed?.asset?.asset_id ?? DEFAULT_ASSET_ID,
      symbol: seed?.asset?.symbol ?? seed?.asset?.asset_id ?? DEFAULT_ASSET_ID,
      venue: seed?.asset?.venue ?? DEFAULT_VENUE,
    },
    entry: {
      spot_usd: spot,
      timestamp_utc: entryTimestamp,
    },
    selected_region: {
      time_start_utc: normalizeDate(seed?.selected_region?.time_start_utc, windowStart),
      time_end_utc: normalizeDate(seed?.selected_region?.time_end_utc, windowEnd),
      price_min_usd: Math.min(priceMin, priceMax),
      price_max_usd: Math.max(priceMin, priceMax),
    },
    target: {
      expiry_utc: expiry,
      window_start_utc: windowStart,
      window_end_utc: windowEnd,
    },
    market_snapshot: {
      as_of_utc: normalizeDate(seed?.market_snapshot?.as_of_utc, now.toISOString()),
      source: seed?.market_snapshot?.source ?? "guided_shell",
      method: seed?.market_snapshot?.method ?? "simulation",
      implied_probability_pct: seed?.market_snapshot?.implied_probability_pct,
      implied_move_pct: seed?.market_snapshot?.implied_move_pct,
    },
    risk_constraints: {
      max_loss_usd: seed?.risk_constraints?.max_loss_usd,
      max_premium_usd: seed?.risk_constraints?.max_premium_usd,
      position_size_usd: seed?.risk_constraints?.position_size_usd,
      payoff_preference: seed?.risk_constraints?.payoff_preference,
      notes: seed?.risk_constraints?.notes,
    },
    selected_expression_ref: seed?.selected_expression_ref ?? null,
    lifecycle: {
      status: seed?.lifecycle?.status ?? "draft",
      created_at_utc: createdAt,
      updated_at_utc: normalizeDate(seed?.lifecycle?.updated_at_utc, now.toISOString()),
      closed_at_utc: seed?.lifecycle?.closed_at_utc,
    },
    user_note: seed?.user_note,
  };
}

export function buildRegionBetGuidedShellSnapshot(
  regionBet: RegionBetContract,
): RegionBetGuidedShellSnapshot {
  return {
    asset_id: regionBet.asset.asset_id,
    symbol: regionBet.asset.symbol,
    venue: regionBet.asset.venue,
    expiry_utc: regionBet.target.expiry_utc,
    window_start_utc: regionBet.target.window_start_utc,
    window_end_utc: regionBet.target.window_end_utc,
    selected_region: { ...regionBet.selected_region },
  };
}

export function applyRegionBetGuidedShellPatch(
  regionBet: RegionBetContract,
  patch: RegionBetGuidedShellPatch,
  now: Date = new Date(),
): RegionBetContract {
  const next: RegionBetContract = {
    ...regionBet,
    asset: { ...regionBet.asset, ...patch.asset },
    entry: { ...regionBet.entry, ...patch.entry },
    target: { ...regionBet.target, ...patch.target },
    selected_region: { ...regionBet.selected_region, ...patch.selected_region },
    market_snapshot: { ...regionBet.market_snapshot, ...patch.market_snapshot },
    risk_constraints: { ...regionBet.risk_constraints, ...patch.risk_constraints },
    selected_expression_ref:
      patch.selected_expression_ref !== undefined
        ? patch.selected_expression_ref
        : regionBet.selected_expression_ref,
    lifecycle: {
      ...regionBet.lifecycle,
      status: "draft",
      updated_at_utc: now.toISOString(),
    },
    user_note: patch.user_note ?? regionBet.user_note,
  };
  return next;
}

export function isRegionBetGuidedDraftPersistable(value: unknown): value is RegionBetContract {
  if (!isRegionBetContract(value)) return false;
  const region = value.selected_region;
  const target = value.target;
  const dateValues = [
    value.entry.timestamp_utc,
    region.time_start_utc,
    region.time_end_utc,
    target.expiry_utc,
    target.window_start_utc,
    target.window_end_utc,
    value.market_snapshot.as_of_utc,
  ].filter((item): item is string => typeof item === "string");
  if (dateValues.some((item) => Number.isNaN(Date.parse(item)))) return false;
  if (region.price_min_usd >= region.price_max_usd) return false;
  if (Date.parse(region.time_start_utc) > Date.parse(region.time_end_utc)) return false;
  if (target.window_start_utc && target.window_end_utc) {
    return Date.parse(target.window_start_utc) <= Date.parse(target.window_end_utc);
  }
  return true;
}
