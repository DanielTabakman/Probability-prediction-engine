import Link from "next/link";

import type { WorkflowSummary } from "@/lib/msosWorkflowStore";
import {
  calibrationStrip,
  headlines,
  labTiles,
  reviewEvents,
} from "@/data/commandCenterFixtures";

type Props = {
  workflow: WorkflowSummary;
};

export function CommandCenterContent({ workflow }: Props) {
  const hasWorkflow = workflow.kpis.some((kpi) => kpi.value !== "0") || workflow.currentWork.length > 0;

  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Workspace / Overview</div>
          <h1 className="title">Command Center</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot" aria-hidden="true" />
            {hasWorkflow ? "MSOS workflow live" : "MSOS workflow empty"}
          </span>
          <span className="btn slim">Share view</span>
          <Link href="/strategy-lab/confirm" className="btn slim primary">
            Create thesis
          </Link>
          <span className="avatar" aria-hidden="true">
            DT
          </span>
        </div>
      </header>

      <section className="calibration-strip panel compact" aria-label="Calibration loop">
        <div>
          <h2>{calibrationStrip.title}</h2>
          <p>{calibrationStrip.body}</p>
        </div>
        <div className="calibration-actions">
          <Link href={calibrationStrip.href} className="btn slim primary">
            {calibrationStrip.cta}
          </Link>
          <Link href="/history" className="btn slim">
            History
          </Link>
          <Link href="/learn" className="btn slim">
            Learn loop
          </Link>
        </div>
      </section>

      <section className="kpi-row" aria-label="Key metrics">
        {workflow.kpis.map((kpi) => (
          <div key={kpi.label} className="kpi">
            <div className="label">{kpi.label}</div>
            <div className={`num ${kpi.tone ?? ""}`.trim()}>{kpi.value}</div>
            <div className="sub">{kpi.sub}</div>
          </div>
        ))}
      </section>
      <p className="panel-sub workflow-source-label">{workflow.sourceLabel}</p>

      <section className="grid command-layout">
        <div className="panel">
          <div className="panel-head">
            <div>
              <h2>Strategy Lab &amp; market lenses</h2>
              <div className="panel-sub">Open a surface and interrogate what is currently priced.</div>
            </div>
            <span className="tag">Explore</span>
          </div>
          <div className="lab-list">
            {labTiles.map((tile) => (
              <div key={tile.title} className={`lab-tile${tile.enabled ? "" : " muted"}`}>
                <div className="lab-mark">{tile.mark}</div>
                <div>
                  <h3>{tile.title}</h3>
                  <p>{tile.description}</p>
                </div>
                {tile.enabled ? (
                  <Link href="/strategy-lab" className="btn slim primary">
                    {tile.cta}
                  </Link>
                ) : (
                  <span className="tag muted">{tile.tag}</span>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <div className="new-thesis">
            <h3>Start with a belief</h3>
            <p>
              Describe what you think is mispriced. MSOS routes the idea to the right lens and preserves the state of
              the thesis.
            </p>
            <Link href="/strategy-lab/confirm" className="btn slim primary">
              Create new thesis →
            </Link>
          </div>
          <div className="panel-head">
            <div>
              <h2>Current work</h2>
              <div className="panel-sub">Lifecycle states stay explicit — sim-only expression.</div>
            </div>
          </div>
          {workflow.currentWork.length === 0 ? (
            <p className="panel-sub">No thesis or expression saved in the MSOS workflow store yet.</p>
          ) : (
            workflow.currentWork.map((item) => (
              <div key={`${item.name}-${item.tag}`} className="strategy">
                <div className="row">
                  <span className="name">{item.name}</span>
                  <span className={`tag${item.tagTone ? ` ${item.tagTone}` : ""}`}>{item.tag}</span>
                </div>
                <p>{item.detail}</p>
              </div>
            ))
          )}
        </div>

        <div className="panel">
          <div className="panel-head">
            <div>
              <h2>Context, news &amp; alerts</h2>
              <div className="panel-sub">What could change a thesis today.</div>
            </div>
          </div>
          {headlines.map((item) => (
            <div key={item.title} className="headline">
              <h4>{item.title}</h4>
              <p>{item.body}</p>
            </div>
          ))}
          <div className="side-label inline">Review queue</div>
          <div className="timeline">
            {reviewEvents.map((event) => (
              <div key={event.title} className="event">
                <span className={`spot ${event.tone}`} aria-hidden="true" />
                <div>
                  <h4>{event.title}</h4>
                  <p>{event.body}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <p className="footer-note">Research demo — workflow store is sim-only; no live order transmitted</p>
    </>
  );
}
