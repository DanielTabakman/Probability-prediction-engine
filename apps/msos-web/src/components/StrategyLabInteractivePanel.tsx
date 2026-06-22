"use client";

import Link from "next/link";
import { useCallback, useMemo, useState } from "react";

import { BeliefBuilder } from "@/components/BeliefBuilder";
import { PpeEmbedBoundary } from "@/components/PpeEmbedBoundary";
import {
  strategyLabChartPanel,
  strategyLabLensSection,
  strategyLabLensTiles,
  strategyLabOutcomePanel,
} from "@/content/strategyLab";
import {
  buildOutcomeFromBelief,
  findBeliefPreset,
  type BeliefPreset,
  type BeliefPresetId,
} from "@/lib/beliefPresets";
import {
  buildOutcomeFromPayload,
  type DisplayPayload,
  type LabOutcomeSummary,
} from "@/lib/ppeDisplayPayload";

type StrategyLabInteractivePanelProps = {
  displayPayload: DisplayPayload | null;
  live: boolean;
  defaultOutcome: LabOutcomeSummary;
};

function expiryLabel(payload: DisplayPayload | null): string {
  return payload?.series_by_expiry?.[0]?.expiry_date ?? "the selected expiry";
}

export function StrategyLabInteractivePanel({
  displayPayload,
  live,
  defaultOutcome,
}: StrategyLabInteractivePanelProps) {
  const [selectedPresetId, setSelectedPresetId] = useState<BeliefPresetId | null>(null);

  const handleSelect = useCallback((preset: BeliefPreset) => {
    setSelectedPresetId(preset.id);
  }, []);

  const outcome = useMemo(() => {
    if (!selectedPresetId) {
      return live && displayPayload ? buildOutcomeFromPayload(displayPayload) : defaultOutcome;
    }
    return buildOutcomeFromBelief(selectedPresetId, displayPayload, live);
  }, [selectedPresetId, displayPayload, live, defaultOutcome]);

  const selectedPreset = findBeliefPreset(selectedPresetId);

  return (
    <>
      <div className="panel chart">
        <BeliefBuilder
          expiryLabel={expiryLabel(displayPayload)}
          selectedId={selectedPresetId}
          onSelect={handleSelect}
        />

        <div className="panel-head">
          <div>
            <h2>{strategyLabChartPanel.title}</h2>
            <div className="panel-sub">{strategyLabChartPanel.subtitle}</div>
          </div>
          <span className="tag">{strategyLabChartPanel.tag}</span>
        </div>

        {selectedPreset ? (
          <p className="belief-active-banner" role="status">
            {strategyLabChartPanel.beliefBannerPrefix}{" "}
            <strong>{selectedPreset.label}</strong> {strategyLabChartPanel.beliefBannerSuffix}
          </p>
        ) : null}

        <PpeEmbedBoundary payload={displayPayload} />

        <div className="legend" aria-label="Chart legend">
          <span>
            <i className="swatch market" aria-hidden="true" />
            {strategyLabChartPanel.legendMarket}
          </span>
          <span>
            <i className="swatch reference" aria-hidden="true" />
            {strategyLabChartPanel.legendReference}
          </span>
          <span className={selectedPresetId ? "legend-active" : undefined}>
            <i className="swatch belief" aria-hidden="true" />
            {strategyLabChartPanel.legendBeliefPrefix}
            {selectedPreset ? `: ${selectedPreset.label}` : ""}
          </span>
        </div>

        <div className="controls" aria-label={strategyLabChartPanel.controlsAriaLabel}>
          <div className="control">
            <div className="control-label">{strategyLabChartPanel.rangeWidthLabel}</div>
            <div className="slider preview" aria-hidden="true" />
          </div>
          <div className="control muted">
            <div className="control-label">{strategyLabChartPanel.tailWeightLabel}</div>
            <div className="slider preview muted" aria-hidden="true" />
          </div>
        </div>

        <div className="panel-head compact">
          <div>
            <h2>{strategyLabLensSection.title}</h2>
            <div className="panel-sub">{strategyLabLensSection.subtitle}</div>
          </div>
        </div>
        <div className="lab-list compact">
          {strategyLabLensTiles.map((tile) =>
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
            <h2>{strategyLabOutcomePanel.title}</h2>
            <div className="panel-sub">{strategyLabOutcomePanel.subtitle}</div>
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
              {selectedPreset
                ? strategyLabOutcomePanel.decisionNextWithPreset(selectedPreset.label)
                : strategyLabOutcomePanel.decisionNextDefault}
            </strong>
            <p>{strategyLabOutcomePanel.decisionBody}</p>
          </div>
          <Link href="/strategy-lab/confirm" className="btn slim primary">
            {strategyLabOutcomePanel.confirmCta}
          </Link>
        </div>
      </div>
    </>
  );
}
