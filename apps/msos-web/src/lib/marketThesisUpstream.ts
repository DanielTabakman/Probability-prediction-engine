/**
 * Server-side upstreams for market thesis evidence and ranking.
 * Display/proxy only — no TS scoring.
 */

function displayApiBase(): string | null {
  const serverUrl = process.env.PPE_DISPLAY_API_SERVER_URL?.trim();
  if (!serverUrl) return null;
  return serverUrl.replace(/\/display\.json(\?.*)?$/i, "");
}

export function marketThesisApplyUrl(): string {
  const base = displayApiBase();
  if (base) return `${base}/market-thesis/apply.json`;
  return (
    process.env.NEXT_PUBLIC_PPE_MARKET_THESIS_APPLY_URL?.trim() ||
    "/ppe-display-api/market-thesis/apply.json"
  );
}

export function optionsMarketReadUrl(assetId: string, targetDate?: string | null): string {
  const params = new URLSearchParams({ asset: assetId.toUpperCase() });
  if (targetDate) params.set("target_date", targetDate.slice(0, 10));
  const base = displayApiBase();
  if (base) return `${base}/v1/options-market-read?${params.toString()}`;
  return `/v1/options-market-read?${params.toString()}`;
}

export function expressionFitRankingUrl(query: {
  assetId: string;
  direction: string;
  belief?: string;
  targetHorizonDays?: number | null;
  maxLossUsd?: number | null;
  payoffPreference?: string;
  expiry?: string | null;
  horizon?: string;
}): string {
  const params = new URLSearchParams({
    asset: query.assetId.toUpperCase(),
    direction: query.direction,
    payoff_preference: query.payoffPreference || "defined_risk",
    horizon: query.horizon || "any",
  });
  if (query.belief) params.set("belief", query.belief);
  if (typeof query.targetHorizonDays === "number") {
    params.set("target_horizon_days", String(query.targetHorizonDays));
  }
  if (typeof query.maxLossUsd === "number") {
    params.set("max_loss_usd", String(query.maxLossUsd));
  }
  if (query.expiry) params.set("expiry", query.expiry.slice(0, 10));
  const base = displayApiBase();
  if (base) {
    return `${base}/options-expression-fit-ranking.json?${params.toString()}`;
  }
  return `/ppe-display-api/options-expression-fit-ranking.json?${params.toString()}`;
}

export async function fetchOptionsMarketReadPayload(
  assetId: string,
  targetDate?: string | null,
): Promise<Record<string, unknown> | null> {
  if (assetId.toUpperCase() !== "BTC") return null;
  try {
    const response = await fetch(optionsMarketReadUrl(assetId, targetDate), {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!response.ok) return null;
    const payload = (await response.json()) as Record<string, unknown>;
    if (!payload || typeof payload !== "object") return null;
    return payload;
  } catch {
    return null;
  }
}

export async function fetchExpressionFitRankingPayload(query: {
  assetId: string;
  direction: string;
  belief?: string;
  targetHorizonDays?: number | null;
  maxLossUsd?: number | null;
  payoffPreference?: string;
  expiry?: string | null;
  horizon?: string;
}): Promise<Record<string, unknown> | null> {
  try {
    const response = await fetch(expressionFitRankingUrl(query), {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (!response.ok) return null;
    const payload = (await response.json()) as Record<string, unknown>;
    if (payload.kind !== "options_expression_fit_ranking") return null;
    return payload;
  } catch {
    return null;
  }
}

export function comparisonRowsFromRanking(
  ranking: Record<string, unknown>,
): Array<Record<string, unknown>> {
  const ranked = Array.isArray(ranking.ranked) ? ranking.ranked : [];
  const prefs =
    ranking.preferences && typeof ranking.preferences === "object"
      ? (ranking.preferences as Record<string, unknown>)
      : {};
  const fallbackDays =
    typeof prefs.target_horizon_days === "number" ? prefs.target_horizon_days : null;

  return ranked.map((raw) => {
    const row = raw as Record<string, unknown>;
    const candidate =
      row.candidate && typeof row.candidate === "object"
        ? (row.candidate as Record<string, unknown>)
        : {};
    const summary =
      candidate.summary && typeof candidate.summary === "object"
        ? (candidate.summary as Record<string, unknown>)
        : {};
    const costUsd =
      typeof candidate.cost_hint_usd === "number"
        ? candidate.cost_hint_usd
        : typeof summary.net_cost_usd === "number"
          ? summary.net_cost_usd
          : null;
    const maxLossUsd =
      typeof candidate.max_loss_usd === "number"
        ? candidate.max_loss_usd
        : typeof summary.max_loss_usd === "number"
          ? summary.max_loss_usd
          : null;
    const days =
      typeof candidate.horizon_days === "number" ? candidate.horizon_days : fallbackDays;
    const whyLower = Array.isArray(row.why_lower)
      ? row.why_lower.map((item) => String(item)).filter(Boolean)
      : [];
    const cons = Array.isArray(candidate.cons)
      ? candidate.cons.map((item) => String(item)).filter(Boolean)
      : [];
    const failureModes = [...whyLower, ...cons].slice(0, 3);
    const candidateId = String(row.candidate_id || candidate.candidate_id || "unknown");
    return {
      candidate_id: candidateId,
      label: String(row.label || candidate.label || candidateId),
      source_primitive: candidateId.startsWith("strategy:")
        ? "strategy_suggestion"
        : "exposure_paths",
      rank: typeof row.rank === "number" ? row.rank : undefined,
      score: typeof row.score === "number" ? row.score : undefined,
      cost:
        costUsd === null
          ? { status: "unavailable", amount_usd: null, bounded: false }
          : { status: "estimated", amount_usd: costUsd },
      max_loss:
        maxLossUsd === null
          ? {
              status: "unavailable",
              amount_usd: null,
              bounded: false,
              label: "Maximum loss unavailable for this candidate",
            }
          : { status: "estimated", amount_usd: maxLossUsd, bounded: true },
      time_horizon: {
        days,
        label: days === null ? "Horizon from thesis" : `about ${days} days`,
      },
      payoff_shape: String(
        candidate.headline ||
          candidate.capital_shape ||
          candidate.structure ||
          row.why ||
          "Educational structure comparison",
      ),
      failure_modes:
        failureModes.length > 0
          ? failureModes
          : ["Educational fit only — not a recommendation or order ticket."],
      recommendation_status: "educational_fit_not_recommendation",
    };
  });
}
