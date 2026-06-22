import Link from "next/link";

import {
  commandCenterCalibrationLinks,
  commandCenterContextPanel,
  commandCenterPageHeader,
  commandCenterRecentWork,
  commandCenterStartHere,
  commandCenterStatusPills,
  commandCenterThesisPrompt,
} from "@/content/commandCenter";
import type { CommandCenterSummary } from "@/lib/commandCenterSummary";
import { labTiles, headlines } from "@/data/commandCenterFixtures";
import { buildCalibrationStrip, buildReviewEvents } from "@/lib/monitorHistoryFeed";
import { DEMO_FOOTER, friendlySnapshotFeedMessage } from "@/lib/publicCopy";

type Props = {
  summary: CommandCenterSummary;
};

function statusPill(summary: CommandCenterSummary): string {
  if (summary.status === "live") return commandCenterStatusPills.live;
  if (summary.status === "empty") return commandCenterStatusPills.empty;
  return commandCenterStatusPills.degraded;
}

export function CommandCenterContent({ summary }: Props) {
  const hasLiveData = summary.status === "live" && summary.currentWork.length > 0;
  const calibrationStrip = buildCalibrationStrip(summary);
  const reviewEvents = buildReviewEvents(summary);

  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">{commandCenterPageHeader.crumb}</div>
          <h1 className="title">{commandCenterPageHeader.title}</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot" aria-hidden="true" />
            {statusPill(summary)}
          </span>
          <span className="btn slim">{commandCenterPageHeader.shareButton}</span>
          <Link href="/strategy-lab/confirm" className="btn slim primary">
            {commandCenterPageHeader.primaryCta}
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
            {commandCenterCalibrationLinks.history}
          </Link>
          <Link href="/learn" className="btn slim">
            {commandCenterCalibrationLinks.learn}
          </Link>
        </div>
      </section>

      <section className="kpi-row" aria-label="Key metrics">
        {summary.kpis.map((kpi) => (
          <div key={kpi.label} className="kpi">
            <div className="label">{kpi.label}</div>
            <div className={`num ${kpi.tone ?? ""}`.trim()}>{kpi.value}</div>
            <div className="sub">{kpi.sub}</div>
          </div>
        ))}
      </section>
      <p className="panel-sub workflow-source-label">{summary.sourceLabel}</p>
      {summary.status === "degraded" ? (
        <p className="panel-sub degraded-feed-note" role="status">
          {friendlySnapshotFeedMessage(summary.degradedReason)}
        </p>
      ) : null}

      <section className="grid command-layout">
        <div className="panel">
          <div className="panel-head">
            <div>
              <h2>{commandCenterStartHere.title}</h2>
              <div className="panel-sub">{commandCenterStartHere.subtitle}</div>
            </div>
            <span className="tag">{commandCenterStartHere.tag}</span>
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
            <h3>{commandCenterThesisPrompt.title}</h3>
            <p>{commandCenterThesisPrompt.body}</p>
            <Link href="/strategy-lab/confirm" className="btn slim primary">
              {commandCenterThesisPrompt.cta}
            </Link>
          </div>
          <div className="panel-head">
            <div>
              <h2>{commandCenterRecentWork.title}</h2>
              <div className="panel-sub">{commandCenterRecentWork.subtitle}</div>
            </div>
          </div>
          {summary.status === "degraded" ? (
            <p className="panel-sub">{commandCenterRecentWork.degradedNote}</p>
          ) : null}
          {summary.status !== "degraded" && !hasLiveData ? (
            <p className="panel-sub">{commandCenterRecentWork.emptyNote}</p>
          ) : null}
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
              <h2>{commandCenterContextPanel.title}</h2>
              <div className="panel-sub">{commandCenterContextPanel.subtitle}</div>
            </div>
          </div>
          {headlines.map((item) => (
            <div key={item.title} className="headline">
              <h4>{item.title}</h4>
              <p>{item.body}</p>
            </div>
          ))}
          <div className="side-label inline">{commandCenterContextPanel.reviewLabel}</div>
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
