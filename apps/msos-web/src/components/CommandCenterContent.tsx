import Link from "next/link";

import type { CommandCenterSummary } from "@/lib/commandCenterSummary";
import { buildCalibrationStrip, buildReviewEvents } from "@/lib/monitorHistoryFeed";
import type { WorkflowSummary } from "@/lib/msosWorkflowStore";
import { headlines, labTiles } from "@/data/commandCenterFixtures";
import { DEMO_FOOTER, friendlySnapshotFeedMessage } from "@/lib/publicCopy";

type Props = {
  summary: CommandCenterSummary;
  workflow: WorkflowSummary;
};

function statusPill(summary: CommandCenterSummary, workflow: WorkflowSummary): string {
  const hasWorkflow = workflow.currentWork.length > 0 || workflow.kpis.some((k) => k.value !== "0");
  if (hasWorkflow) return "Workspace connected";
  if (summary.status === "live") return "Saved reads connected";
  if (summary.status === "empty") return "No saved reads yet";
  return "History offline";
}

export function CommandCenterContent({ summary, workflow }: Props) {
  const hasSnapshotWork = summary.status === "live" && summary.currentWork.length > 0;
  const hasWorkflowWork = workflow.currentWork.length > 0;
  const hasLiveData = hasSnapshotWork || hasWorkflowWork;
  const calibrationStrip = buildCalibrationStrip(summary);
  const reviewEvents = buildReviewEvents(summary);
  const mergedKpis = [...workflow.kpis, ...summary.kpis.filter((k) => !workflow.kpis.some((w) => w.label === k.label))];

  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Home</div>
          <h1 className="title">Command Center</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot" aria-hidden="true" />
            {statusPill(summary, workflow)}
          </span>
          <Link href="/strategy-lab/confirm" className="btn slim primary">
            New view
          </Link>
          <span className="avatar" aria-hidden="true">
            DT
          </span>
        </div>
      </header>

      <section className="calibration-strip panel compact" aria-label="Review loop">
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
            Learn
          </Link>
        </div>
      </section>

      <section className="kpi-row" aria-label="Key metrics">
        {mergedKpis.map((kpi) => (
          <div key={kpi.label} className="kpi">
            <div className="label">{kpi.label}</div>
            <div className={`num ${kpi.tone ?? ""}`.trim()}>{kpi.value}</div>
            <div className="sub">{kpi.sub}</div>
          </div>
        ))}
      </section>
      <p className="panel-sub workflow-source-label">
        {workflow.sourceLabel}
        {summary.status === "live" ? ` · ${summary.sourceLabel}` : ""}
      </p>
      {summary.status === "degraded" ? (
        <p className="panel-sub degraded-feed-note" role="status">
          {friendlySnapshotFeedMessage(summary.degradedReason)}
        </p>
      ) : null}

      <section className="grid command-layout">
        <div className="panel">
          <div className="panel-head">
            <div>
              <h2>Start here</h2>
              <div className="panel-sub">Open a market and compare it to your view.</div>
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
            <h3>Have a view?</h3>
            <p>
              Say what you think is mispriced. We&apos;ll keep your idea on file so you can plan and review
              later.
            </p>
            <Link href="/strategy-lab/confirm" className="btn slim primary">
              Save a view →
            </Link>
          </div>
          <div className="panel-head">
            <div>
              <h2>Recent work</h2>
              <div className="panel-sub">Confirmed views, paper trades, and saved market reads.</div>
            </div>
          </div>
          {summary.status === "degraded" && !hasWorkflowWork ? (
            <p className="panel-sub">Saved history isn&apos;t loading yet. Strategy Lab still has live data.</p>
          ) : null}
          {!hasLiveData ? (
            <p className="panel-sub">Nothing saved yet — start in Strategy Lab.</p>
          ) : null}
          {workflow.currentWork.map((item, index) => (
            <div key={`wf-${item.name}-${index}`} className="strategy">
              <div className="row">
                <span className="name">{item.name}</span>
                <span className={`tag${item.tagTone ? ` ${item.tagTone}` : ""}`}>{item.tag}</span>
              </div>
              <p>{item.detail}</p>
            </div>
          ))}
          {summary.currentWork.map((item) => (
            <div key={item.snapshotId} className="strategy">
              <div className="row">
                <span className="name">{item.name}</span>
                <span className={`tag${item.tagTone ? ` ${item.tagTone}` : ""}`}>{item.tag}</span>
              </div>
              <p>{item.detail}</p>
            </div>
          ))}
        </div>

        <div className="panel">
          <div className="panel-head">
            <div>
              <h2>Context &amp; alerts</h2>
              <div className="panel-sub">News and reminders that might change your view.</div>
            </div>
          </div>
          {headlines.map((item) => (
            <div key={item.title} className="headline">
              <h4>{item.title}</h4>
              <p>{item.body}</p>
            </div>
          ))}
          <div className="side-label inline">To review</div>
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

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
