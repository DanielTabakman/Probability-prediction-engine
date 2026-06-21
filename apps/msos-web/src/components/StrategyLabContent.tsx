import Link from "next/link";

import { StrategyLabInteractivePanel } from "@/components/StrategyLabInteractivePanel";
import { outcomeSummary, strategyLabMetrics } from "@/data/strategyLabFixtures";
import {
  buildLabMetricsFromPayload,
  type DisplayPayload,
  type LabMetric,
} from "@/lib/ppeDisplayPayload";

type StrategyLabContentProps = {
  displayPayload?: DisplayPayload | null;
};

export function StrategyLabContent({ displayPayload = null }: StrategyLabContentProps) {
  const live = displayPayload != null;
  const metrics: LabMetric[] = live
    ? buildLabMetricsFromPayload(displayPayload)
    : strategyLabMetrics;

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
        <StrategyLabInteractivePanel
          displayPayload={displayPayload}
          live={live}
          defaultOutcome={outcomeSummary}
        />
      </section>

      <p className="footer-note">
        {live
          ? "Live market-implied data from PPE — sim-only; no order transmitted."
          : "Illustrative product storyboard — no live order transmitted"}
      </p>
    </>
  );
}
