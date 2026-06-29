import Link from "next/link";
import { Suspense } from "react";

import { MonitorDeleteNotice } from "@/components/MonitorDeleteNotice";
import { MonitorWatchList } from "@/components/MonitorWatchList";
import { MonitorWelcomeCard } from "@/components/MonitorWelcomeCard";
import { MonitorEmptyState } from "@/components/MonitorEmptyState";
import { loadCommandCenterSummary } from "@/lib/commandCenterSummary";
import type { MonitorFeed } from "@/lib/monitorHistoryFeed";
import { resolveWorkflowOwnerId } from "@/lib/msosWorkflowOwner";
import { DEMO_FOOTER, friendlySnapshotFeedMessage } from "@/lib/publicCopy";
import { reviewTagForStatus } from "@/lib/snapshotReview";

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

export async function MonitorContent({ feed }: Props) {
  const ownerId = await resolveWorkflowOwnerId();
  const summary = loadCommandCenterSummary(ownerId);
  const snapshotRows =
    summary.status === "live" ? summary.recentSnapshots.slice(0, 8) : [];

  const watchCount = activeWatchCount(feed.watchPanels);
  const alerts = actionableAlerts(feed);
  const firstTrade = feed.paperTrades[0];
  const firstTradeHref = firstTrade ? `/monitor/paper/${firstTrade.id}` : undefined;

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

        {feed.paperTrades.length > 0 ? (
          <Suspense fallback={null}>
            <MonitorWelcomeCard
              paperTradeCount={feed.paperTrades.length}
              firstTradeHref={firstTradeHref}
              assetTicker={feed.assetTicker}
            />
          </Suspense>
        ) : null}

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

        {snapshotRows.length > 0 ? (
          <div className="monitor-snapshot-list" aria-label="Saved reads">
            <div className="panel-head compact">
              <h2>Saved reads</h2>
              <span className="tag">Snapshots</span>
            </div>
            <p className="panel-sub micro">
              Open a frozen market read to record a post-mortem — paper / research only.
            </p>
            {snapshotRows.map((row) => {
              const { tag, tone } = reviewTagForStatus(row.reviewStatus);
              return (
                <Link
                  key={row.snapshotId}
                  href={`/monitor/snapshot/${row.snapshotId}`}
                  className="monitor-watch-row monitor-watch-link"
                >
                  <div className="monitor-watch-meta">
                    <span className={`tag ${tone ?? "amber"}`}>{tag}</span>
                  </div>
                  <h3>{row.summaryLine}</h3>
                  <p>
                    {row.expiry} · saved {row.createdAt}
                  </p>
                </Link>
              );
            })}
          </div>
        ) : null}

        {feed.paperTrades.length === 0 && feed.status !== "degraded" ? (
          <MonitorEmptyState assetTicker={feed.assetTicker} />
        ) : null}

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
