import Link from "next/link";

import { lensTiles, outcomeSummary, strategyLabMetrics } from "@/data/strategyLabFixtures";
import { PpeEmbedBoundary } from "@/components/PpeEmbedBoundary";
import {
  buildLabMetricsFromPayload,
  buildOutcomeFromPayload,
  type DisplayPayload,
  type LabMetric,
  type LabOutcomeSummary,
} from "@/lib/ppeDisplayPayload";

type StrategyLabContentProps = {
  displayPayload?: DisplayPayload | null;
};

export function StrategyLabContent({ displayPayload = null }: StrategyLabContentProps) {
  const live = displayPayload != null;
  const metrics: LabMetric[] = live
    ? buildLabMetricsFromPayload(displayPayload)
    : strategyLabMetrics;
  const outcome: LabOutcomeSummary = live
    ? buildOutcomeFromPayload(displayPayload)
    : outcomeSummary;

  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Strategy Lab / PPE / Options Distribution Lens</div>
          <h1 className="title">Strategy Lab — PPE Tool</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot" aria-hidden="true" />
            {live ? "Live PPE data" : "Preview fixtures"}
          </span>
          <span className="btn slim">Share view</span>
          <Link href="/strategy-lab/confirm" className="btn slim primary">
            Save draft thesis
          </Link>
          <span className="avatar" aria-hidden="true">
            DT
          </span>
        </div>
      </header>

      <section className="metrics" aria-label="Lab context">
        {metrics.map((metric) => (
          <div key={metric.label} className="metric">
            <div className="label">{metric.label}</div>
            <div className={`value ${metric.tone ?? ""}`.trim()}>{metric.value}</div>
          </div>
        ))}
      </section>

      <section className="work strategy-lab-work">
        <div className="panel chart">
          <div className="belief-builder">
            <h3>What do you believe?</h3>
            <div className="selectline">
              I believe BTC will <span className="selectchip">remain within a narrower range</span> than the
              market prices over <span className="selectchip">the selected expiry</span>.
            </div>
            <p className="micro">
              {live
                ? "Guided thesis draft — interactive belief controls ship in a follow-on slice."
                : "Natural thesis builder first; curve controls below for precision."}
            </p>
          </div>

          <div className="panel-head">
            <div>
              <h2>Market-implied vs reference vs your belief</h2>
              <div className="panel-sub">
                Reference model: <span className="teal">Lognormal benchmark (PPE)</span> · chart region from
                read-only display payload or chromeless embed — math stays in Python.
              </div>
            </div>
            <span className="tag">PPE</span>
          </div>

          <PpeEmbedBoundary payload={displayPayload} />

          <div className="legend" aria-label="Chart legend">
            <span>
              <i className="swatch market" aria-hidden="true" />
              Market implied
            </span>
            <span>
              <i className="swatch reference" aria-hidden="true" />
              Reference model (PPE)
            </span>
            <span>
              <i className="swatch belief" aria-hidden="true" />
              Your belief
            </span>
          </div>

          <div className="controls" aria-label="Chart controls (preview)">
            <div className="control">
              <div className="control-label">Expected range width</div>
              <div className="slider preview" aria-hidden="true" />
            </div>
            <div className="control muted">
              <div className="control-label">Tail emphasis</div>
              <div className="slider preview muted" aria-hidden="true" />
            </div>
          </div>

          <div className="panel-head compact">
            <div>
              <h2>Market lenses</h2>
              <div className="panel-sub">BTC options live via PPE; other lenses planned or pending.</div>
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
              <h2>What this run is saying</h2>
              <div className="panel-sub">Decision support, not trade advice.</div>
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
              <strong>Candidate: narrower-range disagreement</strong>
              <p>Potential expression families available after thesis confirmation.</p>
            </div>
            <Link href="/strategy-lab/confirm" className="btn slim primary">
              Confirm thesis →
            </Link>
          </div>
        </div>
      </section>

      <p className="footer-note">
        {live
          ? "Live market-implied data from PPE — sim-only; no order transmitted."
          : "Illustrative product storyboard — no live order transmitted"}
      </p>
    </>
  );
}
