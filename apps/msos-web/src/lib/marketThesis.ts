/**
 * Market thesis document (market-thesis.v1) — display and persist only.
 * State transitions and validation stay in Python (`src/engine/market_thesis.py`).
 */

export type MarketThesisWorkflowState =
  | "draft"
  | "belief_captured"
  | "horizon_bound"
  | "evidence_attached"
  | "disagreement_recorded"
  | "expressions_ranked"
  | "artifact_saved";

export type MarketThesisDocument = {
  schema_version: "market-thesis.v1";
  kind: "market_thesis";
  id: string;
  revision: number;
  workflow_state: MarketThesisWorkflowState;
  asset: { asset_id: string; symbol?: string; venue?: string };
  user_belief: Record<string, unknown> | null;
  horizon: Record<string, unknown> | null;
  market_evidence: { citations: unknown[] };
  disagreement: Record<string, unknown> | null;
  expression_comparison: Record<string, unknown> | null;
  artifact: Record<string, unknown> | null;
  prior_artifacts: unknown[];
  links: {
    thesis_record_id?: string;
    horizon_region_id?: string;
    region_bet_id?: string;
    expression_record_id?: string;
  };
  authority: {
    execution: "out_of_scope";
    recommendation_status: "educational_comparison_not_recommendation";
  };
};

export const MARKET_THESIS_PERSISTENCE_LABEL =
  "Market thesis saved beside your Strategy Lab view — paper comparison only, not a brokerage record.";

export function isMarketThesisDocument(value: unknown): value is MarketThesisDocument {
  if (!value || typeof value !== "object") return false;
  const row = value as Record<string, unknown>;
  return (
    row.schema_version === "market-thesis.v1" &&
    row.kind === "market_thesis" &&
    typeof row.id === "string" &&
    typeof row.revision === "number" &&
    typeof row.workflow_state === "string" &&
    typeof row.asset === "object" &&
    row.asset !== null
  );
}

export async function fetchMarketThesisDocument(): Promise<MarketThesisDocument | null> {
  if (typeof window === "undefined") return null;
  try {
    const response = await fetch("/api/theses/market-thesis", {
      cache: "no-store",
      credentials: "include",
    });
    if (!response.ok) return null;
    const payload = (await response.json()) as { document?: MarketThesisDocument | null };
    return payload.document && isMarketThesisDocument(payload.document) ? payload.document : null;
  } catch {
    return null;
  }
}

export async function syncMarketThesisFromConfirm(input: {
  thesisRecordId?: string | null;
  assetId: string;
  symbol?: string;
  statement: string;
  direction: "long" | "short" | "neutral";
  magnitudePercent: number;
  uncertaintyKind:
    | "wider_than_market"
    | "narrower_than_market"
    | "similar_to_market"
    | "unspecified";
  expiryDate?: string | null;
  horizonDays?: number | null;
  forwardMult?: number;
  volMult?: number;
  thesisRangePct?: number;
}): Promise<{ ok: boolean; document?: MarketThesisDocument; error?: string }> {
  if (typeof window === "undefined") {
    return { ok: false, error: "browser only" };
  }
  try {
    const response = await fetch("/api/theses/market-thesis", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ action: "sync_from_confirm", ...input }),
    });
    const payload = (await response.json()) as {
      document?: MarketThesisDocument;
      error?: string;
      code?: string;
    };
    if (!response.ok || !payload.document) {
      return {
        ok: false,
        error: payload.error || payload.code || "failed to sync market thesis",
      };
    }
    return { ok: true, document: payload.document };
  } catch {
    return { ok: false, error: "failed to sync market thesis" };
  }
}

export async function attachMarketThesisExpressionComparison(input: {
  expressionRecordId?: string | null;
  expiryDate?: string | null;
  horizonDays?: number | null;
  maxLossUsd?: number | null;
  payoffPreference?: string;
}): Promise<{ ok: boolean; document?: MarketThesisDocument; error?: string }> {
  if (typeof window === "undefined") {
    return { ok: false, error: "browser only" };
  }
  try {
    const response = await fetch("/api/theses/market-thesis", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ action: "attach_expression_comparison", ...input }),
    });
    const payload = (await response.json()) as {
      document?: MarketThesisDocument;
      error?: string;
      code?: string;
    };
    if (!response.ok || !payload.document) {
      return {
        ok: false,
        error: payload.error || payload.code || "failed to attach expression comparison",
        document: payload.document,
      };
    }
    return { ok: true, document: payload.document };
  } catch {
    return { ok: false, error: "failed to attach expression comparison" };
  }
}

export function directionFromForwardMult(forwardMult: number): "long" | "short" | "neutral" {
  if (forwardMult > 1.002) return "long";
  if (forwardMult < 0.998) return "short";
  return "neutral";
}

export function uncertaintyFromVolMult(
  volMult: number,
): "wider_than_market" | "narrower_than_market" | "similar_to_market" {
  if (volMult > 1.02) return "wider_than_market";
  if (volMult < 0.98) return "narrower_than_market";
  return "similar_to_market";
}
