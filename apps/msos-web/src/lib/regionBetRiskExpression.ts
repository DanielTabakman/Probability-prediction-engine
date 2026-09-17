import {
  buildCandidateFromStrategySuggestion,
  buildCandidatesFromExposureMenu,
  rankOptionsExpressionFit,
  type ExpressionFitCandidate,
  type ExpressionFitDirection,
  type ExpressionFitPreferences,
  type ExpressionFitRankedCandidate,
  type ExpressionFitRankingPayload,
  type PayoffPreference,
} from "@/lib/optionsExpressionFitRanking";
import type { ExposureMenuPayload, HorizonChip } from "@/lib/ppeExposureMenu";
import type { StrategySuggestionPayload } from "@/lib/ppeStrategySuggestion";
import type { RegionBetContract } from "@/lib/regionBet";

export const REGION_BET_RISK_EXPRESSION_KIND = "region_bet_risk_expression";

export const REGION_BET_RISK_EXPRESSION_LIMITATION =
  "Paper expression choices only. They map your stated max-loss, premium, and payoff preference onto existing educational fit ranking. Not financial advice, not a recommendation, not expected-return, and not order execution.";

export const REGION_BET_PAYOFF_PREFERENCES: { id: PayoffPreference; label: string }[] = [
  { id: "defined_risk", label: "Defined max loss" },
  { id: "capital_light", label: "Light capital" },
  { id: "upside_leverage", label: "Upside leverage" },
  { id: "income_style", label: "Income-style" },
  { id: "watch_only", label: "Watch only" },
];

export type RegionBetExpressionLaneId = "safer" | "best_fit" | "convex";

export type RegionBetExpressionChoice = {
  lane: RegionBetExpressionLaneId;
  label: string;
  explanation: string;
  ranked: ExpressionFitRankedCandidate;
};

export type RegionBetRiskExpressionStatus = "ready" | "invalid_constraints" | "empty_candidates";

export type RegionBetRiskExpressionPayload = {
  schema_version: 1;
  kind: typeof REGION_BET_RISK_EXPRESSION_KIND;
  status: RegionBetRiskExpressionStatus;
  preferences: ExpressionFitPreferences | null;
  ranking: ExpressionFitRankingPayload | null;
  choices: RegionBetExpressionChoice[];
  selected_expression_ref: RegionBetContract["selected_expression_ref"];
  limitation: string;
};

const LANE_LABEL: Record<RegionBetExpressionLaneId, string> = {
  safer: "Safer / more likely",
  best_fit: "Best fit",
  convex: "Higher payout / convex",
};

export function isRegionBetPayoffPreference(value: unknown): value is PayoffPreference {
  return REGION_BET_PAYOFF_PREFERENCES.some((item) => item.id === value);
}

function finitePositive(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value) && value > 0;
}

export function regionBetRiskConstraintIssues(
  constraints: RegionBetContract["risk_constraints"] | null | undefined,
): string[] {
  const issues: string[] = [];
  if (!constraints) {
    return ["max-loss, premium, and payoff preference are required"];
  }
  if (!finitePositive(constraints.max_loss_usd)) {
    issues.push("max-loss must be a finite amount above zero");
  }
  if (!finitePositive(constraints.max_premium_usd)) {
    issues.push("premium must be a finite amount above zero");
  }
  if (!isRegionBetPayoffPreference(constraints.payoff_preference)) {
    issues.push("payoff preference must be one of the listed paper choices");
  }
  if (
    finitePositive(constraints.max_loss_usd) &&
    finitePositive(constraints.max_premium_usd) &&
    constraints.max_premium_usd > constraints.max_loss_usd
  ) {
    issues.push("premium cannot exceed the stated max-loss");
  }
  return issues;
}

export function isRegionBetRiskExpressionReady(
  regionBet: Pick<RegionBetContract, "risk_constraints">,
): boolean {
  return regionBetRiskConstraintIssues(regionBet.risk_constraints).length === 0;
}

export function inferRegionBetExpressionDirection(
  regionBet: Pick<RegionBetContract, "entry" | "selected_region">,
): ExpressionFitDirection {
  const spot = regionBet.entry.spot_usd;
  const min = regionBet.selected_region.price_min_usd;
  const max = regionBet.selected_region.price_max_usd;
  if (!(Number.isFinite(spot) && Number.isFinite(min) && Number.isFinite(max))) {
    return "neutral";
  }
  if (min >= spot) return "long";
  if (max <= spot) return "short";
  return "neutral";
}

export function regionBetTargetHorizonDays(
  regionBet: Pick<RegionBetContract, "entry" | "target">,
): number {
  const start = Date.parse(regionBet.entry.timestamp_utc);
  const end = Date.parse(regionBet.target.expiry_utc);
  if (Number.isNaN(start) || Number.isNaN(end) || end <= start) {
    return 30;
  }
  return Math.max(1, Math.round((end - start) / 86_400_000));
}

export function regionBetHorizonChip(horizonDays: number): HorizonChip {
  if (horizonDays <= 120) return "3m";
  return "12m";
}

export function mapRegionBetToExpressionFitPreferences(
  regionBet: RegionBetContract,
): ExpressionFitPreferences | null {
  if (!isRegionBetRiskExpressionReady(regionBet)) return null;
  const maxLoss = regionBet.risk_constraints.max_loss_usd as number;
  const maxPremium = regionBet.risk_constraints.max_premium_usd as number;
  return {
    direction: inferRegionBetExpressionDirection(regionBet),
    belief: regionBet.user_note,
    target_horizon_days: regionBetTargetHorizonDays(regionBet),
    max_loss_usd: Math.min(maxLoss, maxPremium),
    payoff_preference: regionBet.risk_constraints.payoff_preference as PayoffPreference,
  };
}

export function filterRegionBetExpressionCandidatesByPremium(
  candidates: ExpressionFitCandidate[],
  maxPremiumUsd: number,
): ExpressionFitCandidate[] {
  return candidates.filter((candidate) => {
    const cost = candidate.cost_hint_usd ?? candidate.max_loss_usd;
    if (typeof cost !== "number" || !Number.isFinite(cost)) return true;
    return Math.abs(cost) <= maxPremiumUsd;
  });
}

export function collectRegionBetExpressionCandidates(
  exposureMenu: ExposureMenuPayload | null | undefined,
  strategySuggestion: StrategySuggestionPayload | null | undefined,
  targetHorizonDays?: number | null,
): ExpressionFitCandidate[] {
  const exposureCandidates = buildCandidatesFromExposureMenu(exposureMenu);
  const strategyCandidate = buildCandidateFromStrategySuggestion(
    strategySuggestion ?? null,
    targetHorizonDays,
  );
  if (strategyCandidate) {
    strategyCandidate.source_order = exposureCandidates.length;
  }
  return [...exposureCandidates, ...(strategyCandidate ? [strategyCandidate] : [])];
}

function lossOf(row: ExpressionFitRankedCandidate): number {
  const value = row.candidate.max_loss_usd ?? row.candidate.cost_hint_usd;
  return typeof value === "number" && Number.isFinite(value)
    ? Math.abs(value)
    : Number.POSITIVE_INFINITY;
}

function isConvexCandidate(row: ExpressionFitRankedCandidate): boolean {
  const lenses = row.candidate.fit_lenses ?? [];
  return lenses.includes("upside_leverage") || row.candidate.leverage === "high";
}

export function explainRegionBetExpressionLane(
  lane: RegionBetExpressionLaneId,
  ranked: ExpressionFitRankedCandidate,
): string {
  if (lane === "safer") {
    return `${ranked.label} stays closer to your stated max-loss and premium limits. ${ranked.components.max_loss_fit.reason}. Paper comparison only.`;
  }
  if (lane === "convex") {
    return `${ranked.label} is the more convex or payout-seeking paper structure among these candidates. Not an expected-return claim.`;
  }
  return `${ranked.label} is the best-fit paper structure against your Region Bet and stated limits. ${ranked.why}`;
}

export function assignRegionBetExpressionLanes(
  ranked: ExpressionFitRankedCandidate[],
): Record<RegionBetExpressionLaneId, ExpressionFitRankedCandidate | null> {
  if (!ranked.length) {
    return { safer: null, best_fit: null, convex: null };
  }
  const safer = [...ranked].sort((a, b) => {
    const lossDelta = lossOf(a) - lossOf(b);
    if (lossDelta !== 0) return lossDelta;
    return b.components.max_loss_fit.score - a.components.max_loss_fit.score;
  })[0];
  const convex =
    ranked.find((row) => isConvexCandidate(row)) ??
    [...ranked].sort((a, b) => lossOf(b) - lossOf(a))[0];
  return {
    safer,
    best_fit: ranked[0],
    convex,
  };
}

export function buildRegionBetExpressionChoices(
  ranked: ExpressionFitRankedCandidate[],
): RegionBetExpressionChoice[] {
  const lanes = assignRegionBetExpressionLanes(ranked);
  return (Object.keys(LANE_LABEL) as RegionBetExpressionLaneId[])
    .map((lane) => {
      const row = lanes[lane];
      if (!row) return null;
      return {
        lane,
        label: LANE_LABEL[lane],
        explanation: explainRegionBetExpressionLane(lane, row),
        ranked: row,
      };
    })
    .filter((item): item is RegionBetExpressionChoice => item !== null);
}

export function selectedRegionBetExpressionRef(
  choice: RegionBetExpressionChoice | ExpressionFitRankedCandidate | null,
): RegionBetContract["selected_expression_ref"] {
  if (!choice) return null;
  const ranked = "ranked" in choice ? choice.ranked : choice;
  return {
    expression_id: ranked.candidate_id,
    source: ranked.candidate.source,
  };
}

export function buildRegionBetRiskExpression(
  regionBet: RegionBetContract,
  exposureMenu: ExposureMenuPayload | null | undefined,
  strategySuggestion: StrategySuggestionPayload | null | undefined,
): RegionBetRiskExpressionPayload {
  const limitation = REGION_BET_RISK_EXPRESSION_LIMITATION;
  if (!isRegionBetRiskExpressionReady(regionBet)) {
    return {
      schema_version: 1,
      kind: REGION_BET_RISK_EXPRESSION_KIND,
      status: "invalid_constraints",
      preferences: null,
      ranking: null,
      choices: [],
      selected_expression_ref: regionBet.selected_expression_ref,
      limitation,
    };
  }

  const preferences = mapRegionBetToExpressionFitPreferences(regionBet);
  if (!preferences) {
    return {
      schema_version: 1,
      kind: REGION_BET_RISK_EXPRESSION_KIND,
      status: "invalid_constraints",
      preferences: null,
      ranking: null,
      choices: [],
      selected_expression_ref: regionBet.selected_expression_ref,
      limitation,
    };
  }

  const maxPremium = regionBet.risk_constraints.max_premium_usd as number;
  const candidates = filterRegionBetExpressionCandidatesByPremium(
    collectRegionBetExpressionCandidates(
      exposureMenu,
      strategySuggestion,
      preferences.target_horizon_days,
    ),
    maxPremium,
  );
  if (!candidates.length) {
    return {
      schema_version: 1,
      kind: REGION_BET_RISK_EXPRESSION_KIND,
      status: "empty_candidates",
      preferences,
      ranking: rankOptionsExpressionFit([], preferences),
      choices: [],
      selected_expression_ref: regionBet.selected_expression_ref,
      limitation,
    };
  }

  const ranking = rankOptionsExpressionFit(candidates, preferences);
  return {
    schema_version: 1,
    kind: REGION_BET_RISK_EXPRESSION_KIND,
    status: ranking.ranked.length ? "ready" : "empty_candidates",
    preferences,
    ranking,
    choices: buildRegionBetExpressionChoices(ranking.ranked),
    selected_expression_ref: regionBet.selected_expression_ref,
    limitation,
  };
}
