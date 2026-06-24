"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { resolveCurveLabels } from "@/lib/chartCurveLabels";
import { ExpressionPayoffChartFrame } from "@/components/ExpressionPayoffChartFrame";
import {
  expressionFamilies,
  expressionRiskNote,
  optimizationBasis,
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
  statusGridForLifecycle,
  type BeliefSnapshot,
  type PaperTradeMarkSnapshot,
} from "@/lib/expressionPersistence";
import {
  fetchStrategySuggestion,
  type StrategySuggestionPayload,
} from "@/lib/ppeStrategySuggestion";
import {
  fetchDisplayPayload,
  listExpiryDates,
} from "@/lib/ppeDisplayPayload";
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
    "From your view";
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
      label: "Max gain",
      value: typeof maxGain === "number" ? formatMoney(maxGain) : "—",
      tone: "teal",
    },
    {
      label: "Max loss",
      value: typeof maxLoss === "number" ? formatMoney(Math.abs(maxLoss)) : "Capped",
      tone: "amber",
    },
    { label: "Breakevens", value: beText },
    { label: "Venue", value: "Deribit" },
    { label: "Profit guarantee", value: "None", tone: "red" },
  ];
}

export function ExpressionPlanningPanel() {
  const [record, setRecord] = useState(defaultExpressionRecord);
  const [thesis, setThesis] = useState<ThesisRecord>(defaultThesisRecord);
  const [thesisConfirmed, setThesisConfirmed] = useState(false);
  const [hydrated, setHydrated] = useState(false);
  const [suggestion, setSuggestion] = useState<StrategySuggestionPayload | null>(null);
  const [suggestionLoading, setSuggestionLoading] = useState(false);
  const [suggestionError, setSuggestionError] = useState<string | null>(null);
  const [expiry, setExpiry] = useState<string | null>(null);
  const [savePending, setSavePending] = useState(false);
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

    let cancelled = false;
    async function loadSuggestion() {
      setSuggestionLoading(true);
      setSuggestionError(null);
      const tuning = loadStoredBeliefTuning();
      const storedExpiry = loadStoredStrategyLabExpiry();
      const display = await fetchDisplayPayload();
      const expiryOptions = display ? listExpiryDates(display) : [];
      const resolvedExpiry =
        (storedExpiry && expiryOptions.includes(storedExpiry) && storedExpiry) ||
        expiryOptions[0] ||
        storedExpiry;
      if (!resolvedExpiry) {
        if (!cancelled) {
          setSuggestionError("Pick an expiry in Strategy Lab first.");
          setSuggestionLoading(false);
        }
        return;
      }
      if (!cancelled) setExpiry(resolvedExpiry);

      const payload = await fetchStrategySuggestion(resolvedExpiry, tuning);
      if (cancelled) return;
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
      cancelled = true;
    };
  }, [hydrated, thesisConfirmed]);

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
    setSavePending(true);
    const saved = await savePaperTrade(next);
    setRecord(saved);
    setLastSavedAt(saved.savedAt ?? saved.updatedAt);
    setSavePending(false);
  }

  const families = familiesWithSelection(livePlan.familyId);
  const optimizationLines = suggestion?.suggested
    ? optimizationFromSuggestion(suggestion, formatMoney)
    : optimizationBasis;
  const statusGrid = statusGridForLifecycle(lastSavedAt ? "simulated" : record.lifecycle);
  const market = suggestion?.market;
  const overlay = suggestion?.suggested?.overlay;

  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Plan a trade</div>
          <h1 className="title">Paper trade planner</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot amber" aria-hidden="true" />
            Paper only — no orders sent
          </span>
          <Link href="/strategy-lab/confirm" className="btn slim">
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
          <Link href="/strategy-lab/confirm" className="btn slim primary">
            Confirm view
          </Link>
        </div>
      ) : (
        <section className="exec-layout" aria-label="Expression planning layout">
          <div className="panel">
            <div className="panel-head">
              <div>
                <h2>Structure types</h2>
                <div className="panel-sub">Which trade shapes fit your view — and which don&apos;t.</div>
              </div>
            </div>
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
            <div className="side-label rails-label">Where to trade</div>
            {venueRails.map((venue) => (
              <div key={venue.id} className={`venue${venue.dimmed ? " dimmed" : ""}`}>
                <div>
                  <h3>{venue.title}</h3>
                  <p>{venue.description}</p>
                </div>
                <span className="tag">{venue.tag}</span>
              </div>
            ))}
          </div>

          <div className="panel ticket">
            <ExpressionPayoffChartFrame
              pricesUsd={market?.prices_usd ?? overlay?.prices_usd ?? []}
              marketPdfPct={market?.pdf_pct ?? []}
              beliefPdfPct={market?.belief_pdf_pct}
              payoffPct={overlay?.payoff_pct ?? []}
              payoffUsd={overlay?.payoff_usd}
              spotUsd={suggestion?.spot_usd ?? 0}
              expiryLabel={expiry ?? suggestion?.expiry_date ?? "selected expiry"}
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
                  <div key={`${leg.side}-${leg.strike}-${leg.instrument}`} className="leg">
                    <span className={leg.side === "BUY" ? "buy" : "sell"}>{leg.side}</span>
                    <span>{leg.instrument}</span>
                    <span>{leg.strike}</span>
                    <span>{leg.tenor}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="status-grid" aria-label="Lifecycle status">
              {statusGrid.map((cell) => (
                <div key={cell.label} className="status-cell">
                  <div className="k">{cell.label}</div>
                  <div className={`v${cell.tone ? ` ${cell.tone}` : ""}`.trim()}>{cell.value}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="panel execution-metrics">
            <div className="panel-head">
              <div>
                <h2>Why this structure</h2>
                <div className="panel-sub">How well it matches your view and risk limits.</div>
              </div>
            </div>
            {(optimizationLines).map((line) => (
              <div key={line.label} className="line">
                <span>{line.label}</span>
                <strong className={line.tone ?? ""}>{line.value}</strong>
              </div>
            ))}
            {suggestion?.suggested?.review?.linkage_line ? (
              <p className="micro">{suggestion.suggested.review.linkage_line}</p>
            ) : null}
            <div className="risk-note">{expressionRiskNote}</div>
            <div className="exec-actions">
              {lastSavedAt ? (
                <>
                  <Link
                    href="/strategy-lab/expression"
                    className="btn slim primary"
                    onClick={() => {
                      setLastSavedAt(null);
                      setRecord(defaultExpressionRecord);
                    }}
                  >
                    Plan another trade
                  </Link>
                  <Link href="/monitor" className="btn slim">
                    Monitor paper trades
                  </Link>
                  <Link href="/history" className="btn slim dark">
                    View history
                  </Link>
                </>
              ) : (
                <>
                  <button type="button" className="btn slim" disabled={!hydrated}>
                    Watch without trading
                  </button>
                  <button
                    type="button"
                    className="btn slim primary"
                    disabled={!hydrated || savePending}
                    onClick={() => void simulateExpression()}
                  >
                    {savePending ? "Saving…" : "Save paper trade"}
                  </button>
                  <button type="button" className="btn slim dark" disabled={!hydrated}>
                    Review order (coming soon)
                  </button>
                </>
              )}
            </div>
            {lastSavedAt ? (
              <p className="micro persistence-note">
                {EXPRESSION_PERSISTENCE_LABEL} Amounts shown in {currency}.
              </p>
            ) : null}
          </div>
        </section>
      )}

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
