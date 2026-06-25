import Link from "next/link";
import { Suspense } from "react";

import { MonitorDeleteNotice } from "@/components/MonitorDeleteNotice";
import { MonitorWatchList } from "@/components/MonitorWatchList";
import type { MonitorFeed, MonitorWatchPanel } from "@/lib/monitorHistoryFeed";
import { DEMO_FOOTER, friendlySnapshotFeedMessage } from "@/lib/publicCopy";

type Props = {
  feed: MonitorFeed;
};

function statusPill(feed: MonitorFeed): string {
  if (feed.status === "live") return "Watching your ideas";
  if (feed.status === "empty") return "Ready when you save a view";
  return "Offline";
}

function activeWatchCount(panels: MonitorWatchPanel[]): number {
  return panels.filter((panel) => panel.id !== "—").length;
}

function actionableAlerts(feed: MonitorFeed) {
  return feed.alerts.filter((alert) => alert.title !== "Monitoring ready");
}

export function MonitorContent({ feed }: Props) {
  const watchCount = activeWatchCount(feed.watchPanels);
  const alerts = actionableAlerts(feed);

  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Monitor</div>
          <h1 className="title">Monitor</h1>
          <p className="monitor-lead">{feed.heroSubtitle}</p>
        </div>
        <div className="tools">
          <span className="pill">
            <span
              className={`dot ${feed.status === "degraded" ? "red" : feed.status === "live" ? "teal" : "amber"}`}
              aria-hidden="true"
            />
            {statusPill(feed)}
          </span>
          <Link href="/history" className="btn slim">
            History
          </Link>
        </div>
      </header>

      <section className="panel monitor-panel">
        <Suspense fallback={null}>
          <MonitorDeleteNotice />
        </Suspense>

        {feed.status === "degraded" ? (
          <p className="panel-sub degraded-feed-note" role="status">
            {friendlySnapshotFeedMessage(feed.degradedReason)}
          </p>
        ) : null}

        <div className="monitor-summary" aria-label="Watch status">
          <span className="monitor-summary-label">{feed.healthLabel}</span>
          <div
            className="meter monitor-meter"
            aria-hidden="true"
            style={{ ["--meter-pct" as string]: `${feed.healthPct}%` }}
          />
        </div>

        <div className="panel-head compact">
          <h2>Watching now</h2>
          {watchCount > 0 ? <span className="tag teal">{watchCount} active</span> : null}
        </div>

        <MonitorWatchList panels={feed.watchPanels} />

        {alerts.length > 0 ? (
          <div className="monitor-alerts" aria-label="Needs attention">
            <div className="side-label inline">Needs attention</div>
            {alerts.map((alert) => (
              <div key={alert.title} className="monitor-alert">
                <span className={`spot ${alert.tone}`} aria-hidden="true" />
                <div>
                  <strong>{alert.title}</strong>
                  <p>{alert.body}</p>
                </div>
              </div>
            ))}
          </div>
        ) : null}
      </section>

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
