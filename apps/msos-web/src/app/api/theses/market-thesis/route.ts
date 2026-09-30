import { NextResponse } from "next/server";

import {
  directionFromForwardMult,
  isMarketThesisDocument,
  uncertaintyFromVolMult,
  type MarketThesisDocument,
} from "@/lib/marketThesis";
import {
  comparisonRowsFromRanking,
  fetchExpressionFitRankingPayload,
  fetchOptionsMarketReadPayload,
  marketThesisApplyUrl,
} from "@/lib/marketThesisUpstream";
import { requireProtectedIdentity } from "@/lib/msosIdentity";
import {
  getCurrentMarketThesis,
  getCurrentThesis,
  upsertCurrentMarketThesis,
} from "@/lib/msosWorkflowStore";

export const runtime = "nodejs";

type ApplyResult =
  | { ok: true; document: MarketThesisDocument; workflow_state: string }
  | { ok: false; status: number; code?: string; error: string };

async function applyMarketThesisEvent(body: Record<string, unknown>): Promise<ApplyResult> {
  const response = await fetch(marketThesisApplyUrl(), {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  });
  const payload = (await response.json().catch(() => ({}))) as {
    ok?: boolean;
    document?: MarketThesisDocument;
    workflow_state?: string;
    code?: string;
    error?: string;
  };
  if (!response.ok || !payload.ok || !payload.document || !isMarketThesisDocument(payload.document)) {
    return {
      ok: false,
      status: response.status >= 400 ? response.status : 502,
      code: payload.code,
      error: payload.error || "market thesis apply failed",
    };
  }
  return {
    ok: true,
    document: payload.document,
    workflow_state: payload.workflow_state || payload.document.workflow_state,
  };
}

async function attachBtcEvidenceIfPossible(
  document: MarketThesisDocument,
  expiryDate: string | null,
): Promise<MarketThesisDocument> {
  if (document.workflow_state !== "horizon_bound") return document;
  if (document.asset.asset_id.toUpperCase() !== "BTC") return document;
  const omr = await fetchOptionsMarketReadPayload(document.asset.asset_id, expiryDate);
  if (!omr) return document;
  const citation = {
    citation_id: "omr-btc",
    primitive: "options_market_read",
    endpoint: "/v1/options-market-read",
    schema_version: omr.schema_version ?? "1.3",
    ruleset_version: omr.ruleset_version ?? "options-market-read.v1.3",
    as_of_utc: String(omr.as_of || omr.as_of_utc || new Date().toISOString()),
    request: {
      asset_id: "BTC",
      ...(expiryDate ? { expiry_date: expiryDate.slice(0, 10) } : {}),
    },
    payload: omr,
  };
  const attached = await applyMarketThesisEvent({
    document,
    event: "attach_evidence",
    payload: { citations: [citation] },
  });
  if (!attached.ok) return document;
  const disagreed = await applyMarketThesisEvent({
    document: attached.document,
    event: "record_disagreement",
    payload: { citation_id: "omr-btc" },
  });
  return disagreed.ok ? disagreed.document : attached.document;
}

async function attachExpressionComparison(
  document: MarketThesisDocument,
  body: Record<string, unknown>,
): Promise<ApplyResult> {
  let working = document;
  const expiryDate =
    (typeof body.expiryDate === "string" && body.expiryDate) ||
    (typeof working.horizon?.["target_date"] === "string"
      ? String(working.horizon["target_date"])
      : typeof working.horizon?.["expiry_date"] === "string"
        ? String(working.horizon["expiry_date"])
        : null);

  if (working.workflow_state === "horizon_bound") {
    working = await attachBtcEvidenceIfPossible(working, expiryDate);
  }
  if (working.workflow_state !== "disagreement_recorded") {
    return {
      ok: false,
      status: 409,
      code: "illegal_transition",
      error: `expression comparison requires disagreement_recorded (have ${working.workflow_state})`,
    };
  }

  const belief = working.user_belief || {};
  const direction =
    belief.direction === "long" || belief.direction === "short" || belief.direction === "neutral"
      ? belief.direction
      : "long";
  const statement = typeof belief.statement === "string" ? belief.statement : "";
  const horizonDays =
    typeof body.horizonDays === "number"
      ? body.horizonDays
      : typeof working.horizon?.["target_bucket_days"] === "number"
        ? Number(working.horizon["target_bucket_days"])
        : null;
  const ranking = await fetchExpressionFitRankingPayload({
    assetId: working.asset.asset_id,
    direction,
    belief: statement,
    targetHorizonDays: horizonDays,
    maxLossUsd: typeof body.maxLossUsd === "number" ? body.maxLossUsd : null,
    payoffPreference:
      typeof body.payoffPreference === "string" ? body.payoffPreference : "defined_risk",
    expiry: expiryDate,
    horizon: horizonDays !== null && horizonDays >= 270 ? "12m" : horizonDays !== null && horizonDays <= 120 ? "3m" : "any",
  });
  if (!ranking) {
    return {
      ok: false,
      status: 503,
      code: "illegal_transition",
      error: "expression fit ranking upstream unavailable",
    };
  }
  const rows = comparisonRowsFromRanking(ranking);
  const ranked = await applyMarketThesisEvent({
    document: working,
    event: "rank_expressions",
    payload: {
      max_loss_usd: typeof body.maxLossUsd === "number" ? body.maxLossUsd : null,
      payoff_preference:
        typeof body.payoffPreference === "string" ? body.payoffPreference : "defined_risk",
      ranking_payload: ranking,
      rows,
      ...(rows.length === 0
        ? { empty_reason: "No educational fit candidates were available for this thesis." }
        : {}),
    },
  });
  if (!ranked.ok) return ranked;

  const frozenAt =
    (typeof body.frozenAtUtc === "string" && body.frozenAtUtc) || new Date().toISOString();
  return applyMarketThesisEvent({
    document: ranked.document,
    event: "save_artifact",
    payload: { frozen_at_utc: frozenAt },
  });
}

export async function GET(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const document = await getCurrentMarketThesis(identity.email);
    return NextResponse.json({ document });
  } catch (err) {
    console.error("market thesis GET failed", err);
    return NextResponse.json({ error: "failed to load market thesis" }, { status: 500 });
  }
}

export async function PUT(request: Request) {
  const identity = requireProtectedIdentity(request);
  if (!identity.ok) return identity.response;
  try {
    const body = (await request.json()) as Record<string, unknown>;
    const action = typeof body.action === "string" ? body.action : "put_document";

    if (action === "put_document") {
      const document = body.document;
      if (!isMarketThesisDocument(document)) {
        return NextResponse.json({ error: "missing market thesis document" }, { status: 400 });
      }
      const validated = await applyMarketThesisEvent({ document, event: "" });
      if (!validated.ok) {
        return NextResponse.json(
          { error: validated.error, code: validated.code },
          { status: validated.status },
        );
      }
      const saved = await upsertCurrentMarketThesis(
        validated.document,
        identity.email,
        validated.document.links?.thesis_record_id ?? null,
      );
      return NextResponse.json({ document: saved });
    }

    if (action === "attach_expression_comparison") {
      const existing = await getCurrentMarketThesis(identity.email);
      if (!existing) {
        return NextResponse.json({ error: "market thesis not started" }, { status: 404 });
      }
      const attached = await attachExpressionComparison(existing, body);
      if (!attached.ok) {
        return NextResponse.json(
          { error: attached.error, code: attached.code, document: existing },
          { status: attached.status },
        );
      }
      const expressionId =
        typeof body.expressionRecordId === "string" ? body.expressionRecordId : undefined;
      const document = {
        ...attached.document,
        links: {
          ...attached.document.links,
          ...(expressionId ? { expression_record_id: expressionId } : {}),
        },
      };
      const saved = await upsertCurrentMarketThesis(
        document,
        identity.email,
        document.links?.thesis_record_id ?? null,
      );
      return NextResponse.json({ document: saved });
    }

    if (action !== "sync_from_confirm") {
      return NextResponse.json({ error: "unknown action" }, { status: 400 });
    }

    const assetId = String(body.assetId || "").trim().toUpperCase();
    if (!assetId) {
      return NextResponse.json({ error: "assetId is required" }, { status: 400 });
    }
    const existing = await getCurrentMarketThesis(identity.email);
    const currentThesis = await getCurrentThesis(identity.email);
    const thesisRecordId =
      (typeof body.thesisRecordId === "string" && body.thesisRecordId) ||
      currentThesis?.id ||
      null;
    const thesisId = existing?.id || `market-thesis-${assetId.toLowerCase()}-${Date.now()}`;

    let document = existing;
    if (!document) {
      const created = await applyMarketThesisEvent({
        document: null,
        event: "new_draft",
        payload: {
          thesis_id: thesisId,
          asset_id: assetId,
          symbol: typeof body.symbol === "string" ? body.symbol : assetId,
        },
      });
      if (!created.ok) {
        return NextResponse.json(
          { error: created.error, code: created.code },
          { status: created.status },
        );
      }
      document = created.document;
    }

    const forwardMult =
      typeof body.forwardMult === "number" ? body.forwardMult : currentThesis?.beliefSnapshot?.forwardMult;
    const volMult =
      typeof body.volMult === "number" ? body.volMult : currentThesis?.beliefSnapshot?.volMult;
    const direction =
      body.direction === "long" || body.direction === "short" || body.direction === "neutral"
        ? body.direction
        : directionFromForwardMult(typeof forwardMult === "number" ? forwardMult : 1);
    const uncertaintyKind =
      body.uncertaintyKind === "wider_than_market" ||
      body.uncertaintyKind === "narrower_than_market" ||
      body.uncertaintyKind === "similar_to_market" ||
      body.uncertaintyKind === "unspecified"
        ? body.uncertaintyKind
        : uncertaintyFromVolMult(typeof volMult === "number" ? volMult : 1);
    const statement =
      (typeof body.statement === "string" && body.statement.trim()) ||
      currentThesis?.disagreementLine ||
      `Strategy Lab view for ${assetId}`;
    const magnitudePercent =
      typeof body.magnitudePercent === "number"
        ? body.magnitudePercent
        : typeof currentThesis?.thesisRangePct === "number"
          ? currentThesis.thesisRangePct
          : 10;

    const belief = {
      source: "user",
      direction,
      statement,
      magnitude: { kind: "percent_move", percent_move: magnitudePercent },
      uncertainty: { kind: uncertaintyKind },
      assumptions: [],
      legacy_strategy_lab: {
        ...(thesisRecordId ? { thesis_record_id: thesisRecordId } : {}),
        ...(typeof forwardMult === "number" ? { forward_mult: forwardMult } : {}),
        ...(typeof volMult === "number" ? { vol_mult: volMult } : {}),
        ...(typeof body.thesisRangePct === "number"
          ? { thesis_range_pct: body.thesisRangePct }
          : typeof currentThesis?.thesisRangePct === "number"
            ? { thesis_range_pct: currentThesis.thesisRangePct }
            : {}),
      },
    };

    const expiryDate =
      (typeof body.expiryDate === "string" && body.expiryDate) ||
      currentThesis?.expiryDate ||
      null;
    const horizonDays =
      typeof body.horizonDays === "number"
        ? body.horizonDays
        : typeof currentThesis?.horizonDays === "number"
          ? currentThesis.horizonDays
          : null;
    const bucket =
      horizonDays !== null && [30, 60, 90, 180, 365].includes(horizonDays) ? horizonDays : null;

    if (document.workflow_state === "draft") {
      const believed = await applyMarketThesisEvent({
        document,
        event: "set_belief",
        payload: belief,
      });
      if (!believed.ok) {
        return NextResponse.json(
          { error: believed.error, code: believed.code },
          { status: believed.status },
        );
      }
      document = believed.document;
    } else if (document.user_belief) {
      const revised = await applyMarketThesisEvent({
        document,
        event: "revise",
        payload: { section: "user_belief", value: belief },
      });
      if (!revised.ok) {
        return NextResponse.json(
          { error: revised.error, code: revised.code },
          { status: revised.status },
        );
      }
      document = revised.document;
    }

    if (expiryDate || bucket) {
      const horizon = expiryDate
        ? { mode: "listed_expiry", target_date: expiryDate.slice(0, 10) }
        : { mode: "bucket", target_bucket_days: bucket };
      if (document.workflow_state === "belief_captured") {
        const bound = await applyMarketThesisEvent({
          document,
          event: "set_horizon",
          payload: horizon,
        });
        if (!bound.ok) {
          return NextResponse.json(
            { error: bound.error, code: bound.code },
            { status: bound.status },
          );
        }
        document = bound.document;
      } else if (document.horizon) {
        const revisedHorizon = await applyMarketThesisEvent({
          document,
          event: "revise",
          payload: { section: "horizon", value: horizon },
        });
        if (!revisedHorizon.ok) {
          return NextResponse.json(
            { error: revisedHorizon.error, code: revisedHorizon.code },
            { status: revisedHorizon.status },
          );
        }
        document = revisedHorizon.document;
      }
    }

    document = await attachBtcEvidenceIfPossible(document, expiryDate);

    document = {
      ...document,
      links: {
        ...document.links,
        ...(thesisRecordId ? { thesis_record_id: thesisRecordId } : {}),
      },
    };

    const saved = await upsertCurrentMarketThesis(document, identity.email, thesisRecordId);
    return NextResponse.json({ document: saved });
  } catch (err) {
    console.error("market thesis PUT failed", err);
    return NextResponse.json({ error: "failed to save market thesis" }, { status: 500 });
  }
}
