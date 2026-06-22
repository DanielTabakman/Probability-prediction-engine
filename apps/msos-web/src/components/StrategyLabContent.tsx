import Link from "next/link";

import { StrategyLabInteractivePanel } from "@/components/StrategyLabInteractivePanel";
import { strategyLabDefaultOutcome, strategyLabPageHeader } from "@/content/strategyLab";
import { strategyLabMetrics } from "@/data/strategyLabFixtures";
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
          <div className="crumb">{strategyLabPageHeader.crumb}</div>
          <h1 className="title">{strategyLabPageHeader.title}</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot" aria-hidden="true" />
            {live ? strategyLabPageHeader.liveDataPill : strategyLabPageHeader.demoDataPill}
          </span>
          <span className="btn slim">{strategyLabPageHeader.shareButton}</span>
          <Link href="/strategy-lab/confirm" className="btn slim primary">
            {strategyLabPageHeader.saveViewCta}
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
          defaultOutcome={strategyLabDefaultOutcome}
        />
      </section>

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
