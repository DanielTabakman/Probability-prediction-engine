import Link from "next/link";

import {
  conclusionHeadline,
  conclusionNarrative,
  learnLoopSteps,
  nextSelectionRecommendation,
  testerMetricsTemplate,
} from "@/data/conclusionFixtures";

export function ConclusionContent() {
  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Conclusion / Learn loop</div>
          <h1 className="title">Tester release — learn loop</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot" aria-hidden="true" />
            Usable demo preview
          </span>
          <Link href="/command-center" className="btn slim">
            Command Center
          </Link>
        </div>
      </header>

      <section className="panel conclusion-hero">
        <div className="panel-sub">Storyboard 09_conclusion</div>
        <h2 className="conclusion-question">{conclusionHeadline}</h2>
        <p className="conclusion-lead">{conclusionNarrative.lead}</p>
        <p className="bodycopy">{conclusionNarrative.body}</p>
      </section>

      <section className="learn-loop-strip" aria-label="Learn loop steps">
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

      <section className="work conclusion-layout">
        <div className="panel">
          <div className="panel-head">
            <h2>Tester metrics template</h2>
            <div className="panel-sub">
              Copy rows into{" "}
              <code className="inline-code">docs/SOP/VALIDATION_REALITY_CHECKS.md</code> after sessions.
            </div>
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

      <p className="footer-note">
        Research demo — validation signals are manual; commercial Streamlit outreach runs in parallel
      </p>
    </>
  );
}
