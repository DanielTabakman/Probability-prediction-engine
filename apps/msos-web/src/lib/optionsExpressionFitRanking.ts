import type { ExposurePathRecord } from "@/lib/ppeExposureMenu";
import type { StrategySuggestionPayload, StrategySuggestionSummary } from "@/lib/ppeStrategySuggestion";

export const EXPRESSION_FIT_RECOMMENDATION_STATUS = "educational_fit_not_recommendation";

export const EXPRESSION_FIT_WEIGHTS = {
  direction_fit: 30,
  horizon_fit: 20,
  max_loss_fit: 20,
  payoff_fit: 15,
  trust_fit: 15,
} as const;

export type ExpressionFitDirection = "long" | "short" | "neutral";
export type PayoffPreference =
  | "defined_risk"
  | "capital_light"
  | "upside_leverage"
  | "income_style"
  | "watch_only";

export type ExpressionFitCandidate = Omit<Partial<ExposurePathRecord>, "legs"> & {
  candidate_id: string;
  source: "exposure_menu" | "strategy_suggestion" | "fallback";
  source_order?: number;
  name?: string;
  horizon_days?: number;
  max_loss_usd?: number | null;
  summary?: StrategySuggestionSummary | null;
  legs?: Array<{ side: string; instrument: string; strike: string; tenor: string }>;
  expression_family?: string | null;
};

export type ExpressionFitPreferences = {
  direction: ExpressionFitDirection;
  belief?: string;
  target_horizon_days?: number | null;
  max_loss_usd?: number | null;
  payoff_preference: PayoffPreference;
};

export type ExpressionFitComponent = {
  score: number;
  weight: number;
  reason: string;
};

export type ExpressionFitRankedCandidate = {
  candidate_id: string;
  label: string;
  rank: number;
  score: number;
  components: Record<keyof typeof EXPRESSION_FIT_WEIGHTS, ExpressionFitComponent>;
  why: string;
  why_lower: string[];
  candidate: ExpressionFitCandidate;
};

export type ExpressionFitRankingPayload = {
  kind: "options_expression_fit_ranking";
  recommendation_status: typeof EXPRESSION_FIT_RECOMMENDATION_STATUS;
  weights: typeof EXPRESSION_FIT_WEIGHTS;
  preferences: ExpressionFitPreferences;
  ranked: ExpressionFitRankedCandidate[];
  top_fit: ExpressionFitRankedCandidate | null;
  limitation: string;
};

export const EXPRESSION_FIT_LIMITATION =
  "Educational fit ranking only. It compares paper candidates against stated constraints; it is not financial advice, a recommendation, expected-profit optimization, or an order ticket.";

const payoffLens: Record<PayoffPreference, string[]> = {
  defined_risk: ["defined_risk"],
  capital_light: ["capital_light"],
  upside_leverage: ["upside_leverage"],
  income_style: ["income_style"],
  watch_only: ["simplest", "liquid"],
};

function bounded(value: number): number {
  return Math.max(0, Math.min(1, value));
}

function labelFor(candidate: ExpressionFitCandidate): string {
  return candidate.label ?? candidate.name ?? candidate.path_id ?? candidate.candidate_id;
}

function inferDirection(candidate: ExpressionFitCandidate): ExpressionFitDirection {
  if (
    candidate.direction === "long" ||
    candidate.direction === "short" ||
    candidate.direction === "neutral"
  ) {
    return candidate.direction;
  }
  const text = [
    candidate.label,
    candidate.headline,
    candidate.capital_shape,
    candidate.sort_group,
    candidate.expression_family,
    ...(candidate.pros ?? []),
    ...(candidate.cons ?? []),
  ]
    .join(" ")
    .toLowerCase();
  if (text.includes("range") || text.includes("iron fly") || text.includes("neutral")) return "neutral";
  if (text.includes("put") || text.includes("bear") || text.includes("downside")) return "short";
  return "long";
}

function component(score: number, key: keyof typeof EXPRESSION_FIT_WEIGHTS, reason: string): ExpressionFitComponent {
  return {
    score: Number((bounded(score) * EXPRESSION_FIT_WEIGHTS[key]).toFixed(4)),
    weight: EXPRESSION_FIT_WEIGHTS[key],
    reason,
  };
}

function lossValue(candidate: ExpressionFitCandidate): number | null {
  const summaryLoss = candidate.summary?.max_loss_usd;
  const value = summaryLoss ?? candidate.max_loss_usd ?? candidate.cost_hint_usd;
  return typeof value === "number" && Number.isFinite(value) ? Math.abs(value) : null;
}

function horizonScore(candidate: ExpressionFitCandidate, prefs: ExpressionFitPreferences): [number, string] {
  const target = prefs.target_horizon_days;
  if (!target) return [1, "no target horizon constraint supplied"];
  if (candidate.time_bound === "none") return [0.85, "no-expiry exposure can be held across the target horizon"];
  const days = candidate.horizon_days;
  if (typeof days !== "number") return [0.5, "dated candidate has no precise horizon metadata"];
  const diff = Math.abs(days - target);
  if (diff <= 14) return [1, `horizon is within 14 days of ${target}d`];
  if (diff <= 45) return [0.75, `horizon is close to ${target}d`];
  if (diff <= 120) return [0.45, `horizon is meaningfully away from ${target}d`];
  return [0.15, `horizon is far from ${target}d`];
}

export function buildCandidateFromStrategySuggestion(
  payload: StrategySuggestionPayload | null,
  targetHorizonDays?: number | null,
): ExpressionFitCandidate | null {
  const suggested = payload?.suggested;
  if (!suggested) return null;
  const presetId = suggested.preset_id ?? "strategy_suggestion";
  const expressionFamily = suggested.expression_family ?? null;
  return {
    candidate_id: `strategy:${presetId}`,
    source: "strategy_suggestion",
    source_order: 0,
    label: suggested.name ?? suggested.preset_label ?? "Strategy Lab structure",
    direction: expressionFamily === "range" || presetId === "short_iron_fly" ? "neutral" : undefined,
    leverage: "defined",
    time_bound: "dated",
    liquidity: "medium",
    trust_badge: "Live",
    sort_group: "strategy_suggestion",
    fit_lenses: ["defined_risk", "capital_light"],
    horizon_days: targetHorizonDays ?? undefined,
    max_loss_usd: suggested.summary?.max_loss_usd ?? null,
    summary: suggested.summary ?? null,
    legs: suggested.legs,
    expression_family: expressionFamily,
  };
}

export function scoreExpressionCandidate(
  candidate: ExpressionFitCandidate,
  prefs: ExpressionFitPreferences,
): ExpressionFitRankedCandidate {
  const label = labelFor(candidate);
  const candidateDirection = inferDirection(candidate);
  const direction =
    candidateDirection === prefs.direction
      ? component(1, "direction_fit", `direction matches ${prefs.direction}`)
      : prefs.direction === "neutral" && candidate.leverage === "defined"
        ? component(0.65, "direction_fit", "defined-risk structure can express a range view, but direction is imperfect")
        : candidateDirection === "neutral"
          ? component(0.45, "direction_fit", `neutral payoff only partly matches a ${prefs.direction} view`)
          : component(0, "direction_fit", `direction is ${candidateDirection}, not ${prefs.direction}`);
  const [horizonRaw, horizonReason] = horizonScore(candidate, prefs);
  const loss = lossValue(candidate);
  const cap = prefs.max_loss_usd;
  const maxLoss =
    candidate.trust_badge === "Planned"
      ? component(0.2, "max_loss_fit", "planned rail lacks live max-loss evidence")
      : cap == null
        ? component(candidate.leverage === "defined" ? 1 : 0.65, "max_loss_fit", "no max-loss cap supplied")
        : loss == null
          ? component(candidate.leverage === "none" ? 0.55 : 0.25, "max_loss_fit", "candidate lacks a comparable max-loss estimate")
          : loss <= cap
            ? component(1, "max_loss_fit", `max loss $${loss.toFixed(0)} is inside the $${cap.toFixed(0)} cap`)
            : loss <= cap * 1.25
              ? component(0.55, "max_loss_fit", `max loss $${loss.toFixed(0)} is slightly above the $${cap.toFixed(0)} cap`)
              : component(0, "max_loss_fit", `max loss $${loss.toFixed(0)} exceeds the $${cap.toFixed(0)} cap`);
  const lenses = new Set(candidate.fit_lenses ?? []);
  const payoffMatch = payoffLens[prefs.payoff_preference].some((lens) => lenses.has(lens));
  const payoff = component(
    payoffMatch ? 1 : 0.25,
    "payoff_fit",
    payoffMatch
      ? `payoff preference matches ${prefs.payoff_preference}`
      : `payoff preference is a weak match for ${prefs.payoff_preference}`,
  );
  const trust =
    candidate.trust_badge === "Live"
      ? component(1, "trust_fit", "live data available")
      : candidate.trust_badge === "Thin chain"
        ? component(0.55, "trust_fit", "thin-chain data lowers confidence")
        : component(0.15, "trust_fit", "planned rail is context only");
  const components = {
    direction_fit: direction,
    horizon_fit: component(horizonRaw, "horizon_fit", horizonReason),
    max_loss_fit: maxLoss,
    payoff_fit: payoff,
    trust_fit: trust,
  };
  const score = Number(Object.values(components).reduce((sum, row) => sum + row.score, 0).toFixed(4));
  const strong = Object.values(components).filter((row) => row.score >= row.weight * 0.8);
  const weak = Object.values(components).filter((row) => row.score < row.weight * 0.8);
  return {
    candidate_id: candidate.candidate_id,
    label,
    rank: 0,
    score,
    components,
    why: `${label} scores ${score.toFixed(1)}/100 because ${strong.map((row) => row.reason).join("; ")}`,
    why_lower: weak.slice(0, 3).map((row) => row.reason),
    candidate,
  };
}

export function rankOptionsExpressionFit(
  candidates: ExpressionFitCandidate[],
  preferences: ExpressionFitPreferences,
): ExpressionFitRankingPayload {
  const ranked = candidates
    .map((candidate) => scoreExpressionCandidate(candidate, preferences))
    .sort((a, b) => {
      if (b.score !== a.score) return b.score - a.score;
      const trustRank = (value?: string) => (value === "Live" ? 0 : value === "Thin chain" ? 1 : value === "Planned" ? 2 : 3);
      const trust = trustRank(a.candidate.trust_badge) - trustRank(b.candidate.trust_badge);
      if (trust !== 0) return trust;
      return (a.candidate.source_order ?? 0) - (b.candidate.source_order ?? 0) || a.candidate_id.localeCompare(b.candidate_id);
    })
    .map((row, index) => ({ ...row, rank: index + 1 }));
  return {
    kind: "options_expression_fit_ranking",
    recommendation_status: EXPRESSION_FIT_RECOMMENDATION_STATUS,
    weights: EXPRESSION_FIT_WEIGHTS,
    preferences,
    ranked,
    top_fit: ranked[0] ?? null,
    limitation: EXPRESSION_FIT_LIMITATION,
  };
}
