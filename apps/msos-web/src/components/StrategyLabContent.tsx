import Link from "next/link";

import { PpeEmbedBoundary } from "@/components/PpeEmbedBoundary";
import { StrategyLabInteractivePanel } from "@/components/StrategyLabInteractivePanel";
import { outcomeSummary, strategyLabMetrics } from "@/data/strategyLabFixtures";
import { DEMO_FOOTER } from "@/lib/publicCopy";
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
          <div className="crumb">Strategy Lab · BTC options</div>
          <h1 className="title">Strategy Lab</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot" aria-hidden="true" />
            {live ? "Live market data" : "Demo data"}
          </span>
          <span className="btn slim">Share</span>
          <Link href="/strategy-lab/confirm" className="btn slim primary">
            Save your view
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
          chartRegion={<PpeEmbedBoundary payload={displayPayload} />}
        />
      </section>

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
