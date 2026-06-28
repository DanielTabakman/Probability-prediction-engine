"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { resolveCurveLabels } from "@/lib/chartCurveLabels";
import { ContextRail } from "@/components/ContextRail";
import { ExpressionPayoffChartFrame } from "@/components/ExpressionPayoffChartFrame";
import { TradeProsConsCard } from "@/components/TradeProsConsCard";
import { PendingPaperTradeBanner } from "@/components/PendingPaperTradeBanner";
import { PlanLegRow } from "@/components/PlanLegRow";
import { WorkflowStepper } from "@/components/WorkflowStepper";
import {
  expressionFamilies,
  expressionRiskNote,
  optimizedPlan,
  planLegs,
  type ExpressionFamily,
  type OptimizationLine,
  venueRails,
} from "@/data/expressionPlanningFixtures";
import { defaultThesisRecord } from "@/data/thesisConfirmFixtures";
import { loadStoredBeliefTuning } from "@/lib/beliefTuning";
import { fetchThesisRecord, type ThesisRecord } from "@/lib/thesisPersistence";
import {
  EXPRESSION_PERSISTENCE_LABEL,
  defaultExpressionRecord,
  fetchExpressionRecord,
  savePaperTrade,
  type BeliefSnapshot,
  type ExpressionRecord,
  type PaperTradeMarkSnapshot,
} from "@/lib/expressionPersistence";
import {
  fetchStrategySuggestion,
  type StrategySuggestionPayload,
} from "@/lib/ppeStrategySuggestion";
import {
  buildStrategyLabPath,
  fetchDisplayPayloadClient,
  listExpiryDates,
  resolveDisplayAssetMeta,
} from "@/lib/ppeDisplayPayload";
import { buildWorkflowStepHref } from "@/lib/strategyLabWorkflow";
import { useResolvedLabAssetId } from "@/lib/useResolvedLabAssetId";
import { resolveSignInUrlWithReturn } from "@/lib/msosPublicUrls";
import { stashPostAuthReturnPath } from "@/lib/postAuthReturn";
import {
  hasWorkflowIdentity,
  stashPendingPaperTrade,
  takePendingPaperTrade,
} from "@/lib/msosWorkflowClient";
import { buildPlainLegSummary, buildTradeProsCons } from "@/lib/tradeReviewCopy";
import { displayCurrencyDisclaimer } from "@/lib/displayCurrency";
import { useDisplayCurrency } from "@/lib/useDisplayCurrency";
import { loadStoredStrategyLabExpiry } from "@/lib/strategyLabExpiry";
import { DEMO_FOOTER } from "@/lib/publicCopy";

function familyIdForPreset(presetId?: string): string {
  if (presetId === "bull_call_spread" || presetId === "bear_put_spread") {
    return "perp";
  }
  if (presetId === "short_iron_fly") {
    return "range";
  }
  return "range";
}

function familiesWithSelection(selectedId: string): ExpressionFamily[] {
  return expressionFamilies.map((family) => {
    if (family.id === selectedId) {
      return { ...family, tag: "Best fit", tagTone: "selected", dimmed: false };
    }
    if (family.id === "observe") {
      return { ...family, dimmed: selectedId !== "observe" };
    }
    if (family.tagTone === "excluded") {
      return family;
    }
    return {
      ...family,
      tag: family.id === "perp" ? "Alt" : family.tag,
      tagTone: family.id === "perp" ? "alt" : family.tagTone,
      dimmed: true,
    };
  });
}

function optimizationFromSuggestion(
  payload: StrategySuggestionPayload | null,
  formatMoney: (usd: number) => string,
): OptimizationLine[] {
  const summary = payload?.suggested?.summary;
  const glance = payload?.suggested?.belief_vs_market_glance;
  const fit =
    glance?.width_relation_label?.trim() ||
    glance?.disagreement_type_line?.trim() ||
    "Matches your stated view";
  const maxLoss = summary?.max_loss_usd;
  const maxGain = summary?.max_gain_usd;
  const breakevens = summary?.breakevens_usd ?? [];
  const beText =
    breakevens.length > 0
      ? breakevens.map((value) => formatMoney(value)).join(" · ")
      : "See chart";

  return [
    { label: "Fits your view", value: fit, tone: "teal" },
    {
      label: "Best case",
      value: typeof maxGain === "number" ? formatMoney(maxGain) : "—",
      tone: "teal",
    },
    {
      label: "Worst case",
      value: typeof maxLoss === "number" ? formatMoney(Math.abs(maxLoss)) : "Capped",
      tone: "amber",
    },
    { label: "Break-even prices", value: beText },
  ];
}

export function ExpressionPlanningPanel() {
  const [record, setRecord] = useState(defaultExpressionRecord);
  const [thesis, setThesis] = useState<ThesisRecord>(defaultThesisRecord);
  const assetId = useResolvedLabAssetId({ thesisAssetId: thesis.assetId });
  const [thesisConfirmed, setThesisConfirmed] = useState(false);
  const [hydrated, setHydrated] = useState(false);
  const [suggestion, setSuggestion] = useState<StrategySuggestionPayload | null>(null);
  const [suggestionLoading, setSuggestionLoading] = useState(false);
  const [suggestionError, setSuggestionError] = useState<string | null>(null);
  const [expiry, setExpiry] = useState<string | null>(null);
  const [savePending, setSavePending] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [lastSavedAt, setLastSavedAt] = useState<string | null>(null);
  const { currency, formatMoney } = useDisplayCurrency();

  useEffect(() => {
    void Promise.all([
      fetchThesisRecord(defaultThesisRecord),
      fetchExpressionRecord(defaultExpressionRecord),
    ]).then(([loadedThesis, expression]) => {
      setThesis(loadedThesis);
      setThesisConfirmed(loadedThesis.lifecycle === "confirmed");
      setRecord(expression);
      setHydrated(true);
    });
  }, []);

  useEffect(() => {
    if (!hydrated || !thesisConfirmed) return;

    const abort = { cancelled: false };
    async function resumePendingSave() {
      const pending = takePendingPaperTrade<ExpressionRecord>();
      if (!pending) return;
      const signedIn = await hasWorkflowIdentity();
      if (!signedIn || abort.cancelled) return;
      setSavePending(true);
      const result = await savePaperTrade(pending);
      if (abort.cancelled) return;
      setRecord(result.expression);
      if (result.ok) {
        setLastSavedAt(result.expression.savedAt ?? result.expression.updatedAt);
      } else if (!result.authRequired) {
        setSaveError(result.error ?? "Could not save paper trade.");
      }
      setSavePending(false);
    }

    void resumePendingSave();
    return () => {
      abort.cancelled = true;
    };
  }, [hydrated, thesisConfirmed]);

  useEffect(() => {
    if (!hydrated || !thesisConfirmed) return;

    const abort = { cancelled: false };
    async function loadSuggestion() {
      setSuggestionLoading(true);
      setSuggestionError(null);
      const tuning = loadStoredBeliefTuning();
      const storedExpiry = loadStoredStrategyLabExpiry();
      const display = await fetchDisplayPayloadClient(assetId);
      const expiryOptions = display ? listExpiryDates(display) : [];
      const resolvedExpiry =
        (storedExpiry && expiryOptions.includes(storedExpiry) && storedExpiry) ||
        expiryOptions[0] ||
        storedExpiry;
      if (!resolvedExpiry) {
        if (!abort.cancelled) {
          setSuggestionError("Pick an expiry in Strategy Lab first.");
          setSuggestionLoading(false);
        }
        return;
      }
      if (!abort.cancelled) setExpiry(resolvedExpiry);

      const payload = await fetchStrategySuggestion(resolvedExpiry, tuning);
      if (abort.cancelled) return;
      if (!payload) {
        setSuggestion(null);
        setSuggestionError("Live trade suggestion unavailable — showing demo structure.");
        setSuggestionLoading(false);
        return;
      }
      setSuggestion(payload);
      setSuggestionLoading(false);
    }

    void loadSuggestion();
    return () => {
      abort.cancelled = true;
    };
  }, [hydrated, thesisConfirmed, assetId]);

  const livePlan = useMemo(() => {
    const suggested = suggestion?.suggested;
    if (!suggested?.legs?.length) {
      return {
        headline: record.planHeadline || optimizedPlan.headline,
        summary: record.planSummary || optimizedPlan.summary,
        legs: record.legs.length ? record.legs : planLegs,
        familyId: record.familyId,
      };
    }
    const review = suggested.review;
    const summary =
      review?.payoff_line ||
      review?.structure_line ||
      `Illustrative ${suggested.preset_label ?? suggested.name ?? "structure"} from your belief vs market.`;
    return {
      headline: suggested.name ?? suggested.preset_label ?? optimizedPlan.headline,
      summary,
      legs: suggested.legs,
      familyId: familyIdForPreset(suggested.preset_id),
    };
  }, [suggestion, record]);

  async function simulateExpression() {
    const tuning = loadStoredBeliefTuning();
    const beliefSnapshot: BeliefSnapshot = {
      forwardMult: tuning.forward_mult,
      volMult: tuning.vol_mult,
    };
    const summary = suggestion?.suggested?.summary;
    const markAtSave: PaperTradeMarkSnapshot = {
      spotUsd: suggestion?.spot_usd,
      netCostUsd: summary?.net_cost_usd ?? null,
      maxGainUsd: summary?.max_gain_usd ?? null,
      maxLossUsd: summary?.max_loss_usd ?? null,
      markedAt: new Date().toISOString(),
    };
    const next = {
      familyId: livePlan.familyId,
      planHeadline: livePlan.headline,
      planSummary: livePlan.summary,
      legs: livePlan.legs,
      lifecycle: "simulated" as const,
      updatedAt: new Date().toISOString(),
      savedAt: new Date().toISOString(),
      expiryDate: expiry ?? suggestion?.expiry_date,
      instrument: thesis.instrument,
      beliefSnapshot,
      markAtSave,
    };

    const signedIn = await hasWorkflowIdentity();
    if (!signedIn) {
      stashPendingPaperTrade(next);
      stashPostAuthReturnPath(planPath);
      window.location.assign(resolveSignInUrlWithReturn(planPath));
      return;
    }

    setSavePending(true);
    setSaveError(null);
    const result = await savePaperTrade(next);
    setRecord(result.expression);
    if (result.ok) {
      setLastSavedAt(result.expression.savedAt ?? result.expression.updatedAt);
    } else if (result.authRequired) {
      stashPendingPaperTrade(next);
      stashPostAuthReturnPath(planPath);
      window.location.assign(resolveSignInUrlWithReturn(planPath));
    } else {
      setSaveError(result.error ?? "Could not save paper trade.");
    }
    setSavePending(false);
  }

  const families = familiesWithSelection(livePlan.familyId);
  const optimizationLines = optimizationFromSuggestion(suggestion, formatMoney);
  const market = suggestion?.market;
  const overlay = suggestion?.suggested?.overlay;
  const glance = suggestion?.suggested?.belief_vs_market_glance;
  const marketExpectationUsd =
    glance?.market_modal_usd ?? glance?.forward_usd ?? undefined;
  const assetMeta = useMemo(
    () => resolveDisplayAssetMeta(null, assetId),
    [assetId],
  );
  const planPath = buildWorkflowStepHref("plan", assetId);
  const confirmPath = buildWorkflowStepHref("confirm", assetId);

  const prosCons = buildTradeProsCons(
    glance,
    suggestion?.suggested?.summary ?? null,
    suggestion?.suggested?.review?.payoff_line ?? null,
    formatMoney,
    suggestion?.suggested?.trade_review,
    assetMeta.id,
  );
  const plainLegSummary = buildPlainLegSummary(
    suggestion?.suggested?.trade_review,
    suggestion?.suggested?.review?.payoff_line ?? null,
    suggestion?.suggested?.review?.structure_line ?? null,
  );

  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Plan a trade</div>
          <h1 className="title">Paper trade planner</h1>
          <p className="panel-sub planner-intro">
            Sketch how this trade pays off at expiry — paper only, no orders sent.
          </p>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot amber" aria-hidden="true" />
            Paper only — no orders sent
          </span>
          <Link href={confirmPath} className="btn slim">
            Back to thesis
          </Link>
          <span className="avatar" aria-hidden="true">
            DT
          </span>
        </div>
      </header>

      {!hydrated ? (
        <div className="panel thesis-gate" aria-live="polite">
          <h2>Loading your workspace</h2>
          <p>Pulling your confirmed view and live trade suggestion from Strategy Lab…</p>
        </div>
      ) : !thesisConfirmed ? (
        <div className="panel thesis-gate">
          <h2>Confirm your view first</h2>
          <p>Save and confirm what you believe in Strategy Lab before sketching a trade structure.</p>
          <Link href={confirmPath} className="btn slim primary">
            Confirm view
          </Link>
        </div>
      ) : (
        <>
          <PendingPaperTradeBanner returnPath={planPath} />
          <WorkflowStepper currentStep="plan" assetId={assetId} />
          <section className="work" aria-label="Expression planning layout">
            <div className="panel ticket">
            <ExpressionPayoffChartFrame
              pricesUsd={market?.prices_usd ?? overlay?.prices_usd ?? []}
              marketPdfPct={market?.pdf_pct ?? []}
              beliefPdfPct={market?.belief_pdf_pct}
              payoffPct={overlay?.payoff_pct ?? []}
              payoffUsd={overlay?.payoff_usd}
              spotUsd={suggestion?.spot_usd ?? 0}
              marketExpectationUsd={marketExpectationUsd}
              expiryLabel={expiry ?? suggestion?.expiry_date ?? "selected expiry"}
              priceAxisLabel={assetMeta.price_axis_label ?? `${assetMeta.id} price at expiry`}
              curveLabels={resolveCurveLabels(market?.curve_labels)}
              loading={suggestionLoading}
              error={suggestionError}
            />
            <div className="route">
              <div className="best">Suggested structure</div>
              <h2>{livePlan.headline}</h2>
              <p>{livePlan.summary}</p>
              <div className="legs" aria-label="Expression legs">
                {livePlan.legs.map((leg) => (
                  <PlanLegRow
                    key={`${leg.side}-${leg.strike}-${leg.instrument}`}
                    leg={leg}
                    assetTicker={assetMeta.id}
                  />
                ))}
              </div>
              {plainLegSummary ? (
                <p className="plain-leg-summary" role="note">
                  <strong>In plain terms:</strong> {plainLegSummary}
                </p>
              ) : null}
              <details className="planner-glossary">
                <summary>New to options? Quick glossary</summary>
                <ul className="micro">
                  <li>
                    <strong>Expiry</strong> — the date your options settle; payoff is judged on{" "}
                    {assetMeta.id} price then.
                  </li>
                  <li>
                    <strong>Strike</strong> — the price level each option is tied to.
                  </li>
                  <li>
                    <strong>Spread</strong> — buying and selling legs together to cap risk.
                  </li>
                  <li>
                    <strong>Max loss</strong> — worst case you pay (paper sketch, not a guarantee).
                  </li>
                  <li>
                    <strong>Break-even</strong> — {assetMeta.id} prices where you neither win nor lose
                    net.
                  </li>
                </ul>
              </details>
            </div>
          </div>

          <ContextRail>
            <div className="panel execution-metrics">
              <div className="panel-head">
                <div>
                  <h2>Why this structure</h2>
                  <div className="panel-sub">How it matches your view and risk limits.</div>
                </div>
              </div>
              <TradeProsConsCard strengths={prosCons.strengths} risks={prosCons.risks} />
              {optimizationLines.map((line) => (
                <div key={line.label} className="line">
                  <span>{line.label}</span>
                  <strong className={line.tone ?? ""}>{line.value}</strong>
                </div>
              ))}
              {suggestion?.suggested?.review?.linkage_line ? (
                <p className="micro">{suggestion.suggested.review.linkage_line}</p>
              ) : null}
              <div className="risk-note">{expressionRiskNote}</div>

              <details className="planner-advanced">
                <summary>Structure types (advanced)</summary>
                {families.map((family) => (
                  <div
                    key={family.id}
                    className={`option-row${family.dimmed ? " dimmed" : ""}`}
                  >
                    <div>
                      <h3>{family.title}</h3>
                      <p>{family.description}</p>
                    </div>
                    <span
                      className={`tag${family.tagTone === "selected" ? " amber" : ""}${
                        family.tagTone === "excluded" ? " red" : ""
                      }`}
                    >
                      {family.tag}
                    </span>
                  </div>
                ))}
                <p className="micro side-label rails-label">Where to trade (paper log)</p>
                {venueRails
                  .filter((venue) => venue.id === "deribit")
                  .map((venue) => (
                    <div key={venue.id} className="venue">
                      <div>
                        <h3>{venue.title}</h3>
                        <p>{venue.description}</p>
                      </div>
                      <span className="tag">{venue.tag}</span>
                    </div>
                  ))}
              </details>

              <div className="exec-actions">
                {lastSavedAt ? (
                  <>
                    <div className="save-success-callout" role="status">
                      <strong>Paper trade saved</strong>
                      <p>
                        We&apos;ll track how this sketch would have done versus live {assetMeta.id}{" "}
                        until expiry — no orders were sent.
                      </p>
                    </div>
                    <Link href={buildStrategyLabPath(assetId)} className="btn slim primary">
                      Plan another trade
                    </Link>
                    <Link href="/monitor?welcome=1" className="btn slim">
                      Monitor paper trades
                    </Link>
                    <Link href="/history" className="btn slim dark">
                      View history
                    </Link>
                  </>
                ) : (
                  <button
                    type="button"
                    className="btn slim primary"
                    disabled={!hydrated || savePending}
                    onClick={() => void simulateExpression()}
                  >
                    {savePending ? "Saving…" : "Save paper trade"}
                  </button>
                )}
              </div>
              {saveError ? (
                <p className="micro degraded-feed-note" role="alert">
                  {saveError}
                </p>
              ) : null}
              {!lastSavedAt ? (
                <p className="micro persistence-note">
                  Sign in to save this plan to your profile — no order is sent.
                </p>
              ) : null}
              {lastSavedAt ? (
                <p className="micro persistence-note">
                  {EXPRESSION_PERSISTENCE_LABEL} {displayCurrencyDisclaimer(currency)}
                </p>
              ) : null}
            </div>
          </ContextRail>
        </section>
        </>
      )}

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
