"use client";

import Link from "next/link";
import { useCallback, useMemo, useState } from "react";

import { BeliefBuilder } from "@/components/BeliefBuilder";
import { PpeEmbedBoundary } from "@/components/PpeEmbedBoundary";
import { lensTiles } from "@/data/strategyLabFixtures";
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
    try {
      return buildOutcomeFromBelief(selectedPresetId, displayPayload, live);
    } catch {
      return defaultOutcome;
    }
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
            <h2>Market vs your view</h2>
            <div className="panel-sub">
              Purple curve = what BTC options imply today. Teal dashed = your belief when selected.
            </div>
          </div>
          <span className="tag">Options</span>
        </div>

        {selectedPreset ? (
          <p className="belief-active-banner" role="status">
            Your view: <strong>{selectedPreset.label}</strong> — compare to the chart below.
          </p>
        ) : null}

        <PpeEmbedBoundary
          payload={displayPayload}
          beliefPresetId={selectedPresetId}
          beliefLabel={selectedPreset?.label ?? null}
        />

        <div className="legend" aria-label="Chart legend">
          <span>
            <i className="swatch market" aria-hidden="true" />
            Options market
          </span>
          <span>
            <i className="swatch reference" aria-hidden="true" />
            Reference curve
          </span>
          <span className={selectedPresetId ? "legend-active" : undefined}>
            <i className="swatch belief" aria-hidden="true" />
            Your view{selectedPreset ? `: ${selectedPreset.label}` : ""}
          </span>
        </div>

        <div className="controls" aria-label="Fine-tuning (coming soon)">
          <div className="control">
            <div className="control-label">Range width</div>
            <div className="slider preview" aria-hidden="true" />
          </div>
          <div className="control muted">
            <div className="control-label">Tail weight</div>
            <div className="slider preview muted" aria-hidden="true" />
          </div>
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
              {selectedPreset
                ? `Next: confirm your “${selectedPreset.label.toLowerCase()}” view`
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
