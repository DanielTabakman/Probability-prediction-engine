import { NextResponse } from "next/server";

import {
  directionFromForwardMult,
  isMarketThesisDocument,
  uncertaintyFromVolMult,
  type MarketThesisDocument,
} from "@/lib/marketThesis";
import { requireProtectedIdentity } from "@/lib/msosIdentity";
import {
  getCurrentMarketThesis,
  getCurrentThesis,
  upsertCurrentMarketThesis,
} from "@/lib/msosWorkflowStore";

export const runtime = "nodejs";

const PUBLIC_APPLY_PATH =
  process.env.NEXT_PUBLIC_PPE_MARKET_THESIS_APPLY_URL?.trim() ||
  "/ppe-display-api/market-thesis/apply.json";

function applyUpstreamUrl(): string {
  const serverUrl = process.env.PPE_DISPLAY_API_SERVER_URL?.trim();
  if (serverUrl) {
    const base = serverUrl.replace(/\/display\.json(\?.*)?$/i, "");
    return `${base}/market-thesis/apply.json`;
  }
  return PUBLIC_APPLY_PATH;
}

type ApplyResult =
  | { ok: true; document: MarketThesisDocument; workflow_state: string }
  | { ok: false; status: number; code?: string; error: string };

async function applyMarketThesisEvent(body: Record<string, unknown>): Promise<ApplyResult> {
  const response = await fetch(applyUpstreamUrl(), {
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
