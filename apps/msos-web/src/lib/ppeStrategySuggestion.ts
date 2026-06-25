/**
 * PPE strategy suggestion boundary — display/proxy only (payoff math in Python).
 */

import type { BeliefTuning } from "@/lib/beliefTuning";
import type { CurveDisplayLabels } from "@/lib/chartCurveLabels";
import type { PlanLeg } from "@/data/expressionPlanningFixtures";

export const PPE_STRATEGY_SUGGESTION_API_URL = (
  process.env.NEXT_PUBLIC_PPE_STRATEGY_SUGGESTION_API_URL ??
  "/ppe-display-api/strategy-suggestion.json"
).trim();

export type StrategySuggestionLeg = PlanLeg;

export type StrategySuggestionSummary = {
  net_cost_usd?: number | null;
  debit_credit?: string | null;
  max_gain_usd?: number | null;
  max_loss_usd?: number | null;
  breakevens_usd?: number[] | null;
  qty?: number | null;
};

export type StrategySuggestionReview = {
  structure_line?: string;
  payoff_line?: string;
  linkage_line?: string;
};

export type TradeReviewBlock = {
  strengths?: string[];
  risks?: string[];
  plain_leg_summary?: string;
};

export type BeliefVsMarketGlance = {
  width_relation_label?: string;
  disagreement_type_line?: string;
  largest_gap_display?: string;
  forward_usd?: number;
  market_modal_usd?: number;
  belief_peak_usd?: number;
  digest_lines?: string[];
  fit_bridge_bullets?: string[];
  shape_gap_strength?: string;
};

export type StrategySuggestionPayload = {
  kind: "strategy_suggestion_boundary" | "strategy_suggestion_error";
  expiry_date?: string;
  spot_usd?: number;
  error?: string;
  market?: {
    prices_usd: number[];
    pdf_pct: number[];
    belief_pdf_pct?: number[];
    curve_labels?: CurveDisplayLabels;
  };
  suggested?: {
    preset_id?: string;
    preset_label?: string;
    name?: string;
    legs?: StrategySuggestionLeg[];
    overlay?: {
      prices_usd: number[];
      payoff_pct: number[];
      payoff_usd?: number[];
    };
    summary?: StrategySuggestionSummary;
    review?: StrategySuggestionReview;
    trade_review?: TradeReviewBlock | null;
    expression_family?: string | null;
    belief_vs_market_glance?: BeliefVsMarketGlance | null;
  };
};

export function buildStrategySuggestionFetchUrl(
  expiry: string,
  tuning: BeliefTuning,
  baseUrl = PPE_STRATEGY_SUGGESTION_API_URL,
): string {
  const params = new URLSearchParams({
    expiry,
    forward_mult: String(tuning.forward_mult),
    vol_mult: String(tuning.vol_mult),
  });
  const separator = baseUrl.includes("?") ? "&" : "?";
  return `${baseUrl}${separator}${params.toString()}`;
}

export async function fetchStrategySuggestion(
  expiry: string,
  tuning: BeliefTuning,
): Promise<StrategySuggestionPayload | null> {
  if (!expiry) return null;
  try {
    const res = await fetch(buildStrategySuggestionFetchUrl(expiry, tuning), {
      cache: "no-store",
      headers: { Accept: "application/json", "User-Agent": "msos-web/1" },
    });
    if (!res.ok) return null;
    const payload = (await res.json()) as StrategySuggestionPayload;
    return payload?.kind === "strategy_suggestion_boundary" ? payload : null;
  } catch {
    return null;
  }
}
