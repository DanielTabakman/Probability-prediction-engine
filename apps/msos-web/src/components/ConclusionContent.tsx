import Link from "next/link";

import { DemoSessionDebrief } from "@/components/DemoSessionDebrief";
import {
  conclusionHeadline,
  conclusionNarrative,
  learnLoopSteps,
  nextSelectionRecommendation,
  testerMetricsTemplate,
} from "@/data/conclusionFixtures";
import { DEMO_FOOTER } from "@/lib/publicCopy";

type ConclusionContentProps = {
  highlightDebrief?: boolean;
};

export function ConclusionContent({ highlightDebrief = false }: ConclusionContentProps) {
  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Learn</div>
          <h1 className="title">Reflect</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot" aria-hidden="true" />
            Research preview
          </span>
          <Link href="/command-center" className="btn slim">
            Command Center
          </Link>
        </div>
      </header>

      <section className="panel conclusion-hero">
        <h2 className="conclusion-question">{conclusionHeadline}</h2>
        <p className="conclusion-lead">{conclusionNarrative.lead}</p>
        <p className="bodycopy">{conclusionNarrative.body}</p>
      </section>

      <section className="learn-loop-strip" aria-label="How a session flows">
        {learnLoopSteps.map((step, index) => (
          <div key={step.id} className="learn-step">
            <span className="learn-index">{index + 1}</span>
            <div>
              <strong>{step.label}</strong>
              <p>{step.detail}</p>
            </div>
          </div>
        ))}
      </section>

      <DemoSessionDebrief highlight={highlightDebrief} />

      <section className="work conclusion-layout">
        <div className="panel">
          <div className="panel-head">
            <h2>Feedback prompts</h2>
            <div className="panel-sub">Optional — helps us improve the demo for new traders.</div>
          </div>
          {testerMetricsTemplate.map((row) => (
            <div key={row.metric} className="metric-row">
              <div className="metric-row-head">
                <span className="tag teal">{row.metric}</span>
                <span className="metric-fixture">{row.fixture}</span>
              </div>
              <p>{row.prompt}</p>
            </div>
          ))}
        </div>

        <aside className="panel conclusion-aside">
          <div className="panel-head">
            <h2>{nextSelectionRecommendation.title}</h2>
          </div>
          <p className="bodycopy">{nextSelectionRecommendation.recommendation}</p>
          <p className="micro aside-warning">{nextSelectionRecommendation.notNow}</p>
          <div className="conclusion-links">
            <Link href="/feedback" className="btn slim primary">
              Share feedback
            </Link>
            <Link href="/strategy-lab" className="btn slim">
              Strategy Lab
            </Link>
            <Link href="/monitor" className="btn slim">
              Monitor
            </Link>
            <Link href="/history" className="btn slim primary">
              History
            </Link>
          </div>
        </aside>
      </section>

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
