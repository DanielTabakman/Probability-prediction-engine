/**
 * Curve legend labels — display copy from Python SSOT (curve_display_labels.py).
 */

export type CurveDisplayLabels = {
  market_legend: string;
  belief_legend: string;
  payoff_legend: string;
  market_method?: string;
  belief_method?: string;
  payoff_method?: string;
};

export const DEFAULT_CURVE_LABELS: CurveDisplayLabels = {
  market_legend: "Market view [Black–Scholes lognormal]",
  belief_legend: "Your view [Belief lognormal]",
  payoff_legend: "Payoff at expiry [Structure P&L]",
  market_method: "Black–Scholes lognormal",
  belief_method: "Belief lognormal",
  payoff_method: "Structure P&L",
};

function isCurveDisplayLabels(value: unknown): value is CurveDisplayLabels {
  if (!value || typeof value !== "object") return false;
  const row = value as Partial<CurveDisplayLabels>;
  return (
    typeof row.market_legend === "string" &&
    typeof row.belief_legend === "string" &&
    typeof row.payoff_legend === "string"
  );
}

export function resolveCurveLabels(source?: unknown): CurveDisplayLabels {
  if (isCurveDisplayLabels(source)) {
    return { ...DEFAULT_CURVE_LABELS, ...source };
  }
  return DEFAULT_CURVE_LABELS;
}
