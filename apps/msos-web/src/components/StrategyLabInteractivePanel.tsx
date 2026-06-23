"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import type { LabDataMode } from "@/lib/strategyLabCopy";
import { BeliefBuilder } from "@/components/BeliefBuilder";
import { BeliefFineTuning } from "@/components/BeliefFineTuning";
import { PpeEmbedBoundary } from "@/components/PpeEmbedBoundary";
import { DEFAULT_CURVE_LABELS } from "@/lib/chartCurveLabels";
import { lensTiles } from "@/data/strategyLabFixtures";
import { buildOutcomeFromTuning } from "@/lib/beliefPresets";
import {
  buildTuningLabel,
  fetchBeliefOverlayPdf,
  isMarketTuning,
  loadStoredBeliefTuning,
  MARKET_TUNING,
  nudgeTuning,
  presetIdForTuning,
  saveBeliefTuning,
  type BeliefNudgeAxis,
  type BeliefTuning,
} from "@/lib/beliefTuning";
import {
  buildOutcomeFromPayload,
  findSeriesByExpiry,
  type DisplayPayload,
  type LabOutcomeSummary,
} from "@/lib/ppeDisplayPayload";

type StrategyLabInteractivePanelProps = {
  displayPayload: DisplayPayload | null;
  live: boolean;
  dataMode: LabDataMode;
  defaultOutcome: LabOutcomeSummary;
  selectedExpiry: string;
  onExpiryChange: (expiry: string) => void;
  expiryOptions: string[];
};

export function StrategyLabInteractivePanel({
  displayPayload,
  live,
  dataMode,
  defaultOutcome,
  selectedExpiry,
  onExpiryChange,
  expiryOptions,
}: StrategyLabInteractivePanelProps) {
  const [tuning, setTuning] = useState<BeliefTuning>(MARKET_TUNING);
  const [beliefPdfPct, setBeliefPdfPct] = useState<number[] | null>(null);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setTuning(loadStoredBeliefTuning());
    setHydrated(true);
  }, []);

  const applyTuning = useCallback((next: BeliefTuning) => {
    setTuning(next);
    saveBeliefTuning(next);
  }, []);

  const handleNudge = useCallback(
    (axis: BeliefNudgeAxis) => {
      setTuning((prev) => {
        const next = nudgeTuning(prev, axis);
        saveBeliefTuning(next);
        return next;
      });
    },
    [],
  );

  const handleReset = useCallback(() => {
    applyTuning(MARKET_TUNING);
    setBeliefPdfPct(null);
  }, [applyTuning]);

  const handleFineTuning = useCallback(
    (next: BeliefTuning) => {
      applyTuning(next);
    },
    [applyTuning],
  );

  const viewLabel = buildTuningLabel(tuning);
  const active = !isMarketTuning(tuning);

  useEffect(() => {
    if (!hydrated || !active || !live || !displayPayload || !selectedExpiry) {
      if (!active) setBeliefPdfPct(null);
      return;
    }

    const cachePresetId = presetIdForTuning(tuning);
    if (cachePresetId) {
      const series = findSeriesByExpiry(displayPayload, selectedExpiry);
      const presetPdf =
        series?.belief_presets?.[cachePresetId]?.pdf_pct ??
        displayPayload.belief_presets?.[cachePresetId]?.pdf_pct ??
        null;
      if (presetPdf) {
        setBeliefPdfPct(presetPdf);
        return;
      }
    }

    let cancelled = false;
    const timer = window.setTimeout(() => {
      void fetchBeliefOverlayPdf(selectedExpiry, tuning).then((pdf) => {
        if (!cancelled) {
          setBeliefPdfPct(pdf);
        }
      });
    }, 120);

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [hydrated, active, tuning, live, displayPayload, selectedExpiry]);

  const outcome = useMemo(() => {
    if (!active) {
      return live && displayPayload ? buildOutcomeFromPayload(displayPayload) : defaultOutcome;
    }
    try {
      return buildOutcomeFromTuning(tuning, displayPayload, live, selectedExpiry);
    } catch {
      return defaultOutcome;
    }
  }, [active, tuning, displayPayload, live, defaultOutcome, selectedExpiry]);

  return (
    <>
      <div className="panel chart">
        <BeliefBuilder
          expiryLabel={selectedExpiry}
          expiryOptions={expiryOptions}
          onExpiryChange={onExpiryChange}
          tuning={tuning}
          onNudge={handleNudge}
          onReset={handleReset}
        />

        <div className="panel-head">
          <div>
            <h2>Market vs your view</h2>
            <div className="panel-sub">
              Purple curve = what BTC options imply today. Teal dashed = your belief when adjusted.
            </div>
          </div>
          <span className="tag">Options</span>
        </div>

        {active ? (
          <p className="belief-active-banner" role="status">
            Your view: <strong>{viewLabel}</strong> — compare to the chart below.
          </p>
        ) : null}

        <PpeEmbedBoundary
          payload={displayPayload}
          live={live}
          dataMode={dataMode}
          selectedExpiry={selectedExpiry}
          beliefLabel={active ? viewLabel : null}
          beliefPdfPct={beliefPdfPct}
        />

        <BeliefFineTuning tuning={tuning} onChange={handleFineTuning} />

        <div className="legend chart-curve-legend" aria-label="Chart legend">
          <span>
            <i className="swatch market" aria-hidden="true" />
            {DEFAULT_CURVE_LABELS.market_legend}
          </span>
          <span className={active ? "legend-active" : undefined}>
            <i className="swatch belief" aria-hidden="true" />
            {DEFAULT_CURVE_LABELS.belief_legend}
            {active ? `: ${viewLabel}` : ""}
          </span>
        </div>

        <div className="panel-head compact">
          <div>
            <h2>Other markets</h2>
            <div className="panel-sub">BTC options are live. More assets coming.</div>
          </div>
        </div>
        <div className="lab-list compact">
          {lensTiles.map((tile) =>
            tile.live && tile.href ? (
              <Link key={tile.title} href={tile.href} className="lab-tile">
                <div className="lab-mark">{tile.mark}</div>
                <div>
                  <h3>{tile.title}</h3>
                  <p>{tile.description}</p>
                </div>
                <span className="tiny-pill">{tile.status}</span>
              </Link>
            ) : (
              <div key={tile.title} className="lab-tile muted">
                <div className="lab-mark">{tile.mark}</div>
                <div>
                  <h3>{tile.title}</h3>
                  <p>{tile.description}</p>
                </div>
                <span className="tag muted">{tile.status}</span>
              </div>
            ),
          )}
        </div>
      </div>

      <div className="panel outcome">
        <div className="panel-head">
          <div>
            <h2>What this means</h2>
            <div className="panel-sub">Decision support — not financial advice.</div>
          </div>
          <span className={`tag ${outcome.tagTone}`}>{outcome.tag}</span>
        </div>
        {outcome.delta !== "—" ? <div className="bigdelta">{outcome.delta}</div> : null}
        <h2 className="outcome-headline">{outcome.headline}</h2>
        <p className="bodycopy">{outcome.body}</p>
        <div className="score">
          {outcome.scores.map((item) => (
            <div key={item.label} className="small-panel">
              <div className="k">{item.label}</div>
              <div className={`v ${item.tone}`}>{item.value}</div>
            </div>
          ))}
        </div>
        <div className="decision-strip">
          <div>
            <strong>
              {active
                ? `Next: confirm your “${viewLabel.toLowerCase()}” view`
                : "Next: pick how you disagree with the market"}
            </strong>
            <p>Then explore trade structures that fit — paper only on this demo.</p>
          </div>
          <Link href="/strategy-lab/confirm" className="btn slim primary">
            Confirm view →
          </Link>
        </div>
      </div>
    </>
  );
}
