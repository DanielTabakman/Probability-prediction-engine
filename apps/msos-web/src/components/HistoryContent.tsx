import Link from "next/link";

import type { HistoryFeed, HistoryState } from "@/lib/monitorHistoryFeed";

const stateLabels: Record<HistoryState, string> = {
  observed: "Observed",
  saved: "Saved",
  simulated: "Simulated",
  reviewed: "Reviewed",
};

type Props = {
  feed: HistoryFeed;
};

function statusPill(feed: HistoryFeed): string {
  if (feed.status === "live") return "Live timeline";
  if (feed.status === "empty") return "No history rows yet";
  return "History feed degraded";
}

export function HistoryContent({ feed }: Props) {
  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">History / Lifecycle trail</div>
          <h1 className="title">History</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot" aria-hidden="true" />
            {statusPill(feed)}
          </span>
          <Link href="/monitor" className="btn slim">
            Monitor
          </Link>
        </div>
      </header>

      <section className="panel history-panel">
        <div className="panel-head">
          <div>
            <h2>Observed → reviewed</h2>
            <div className="panel-sub">{feed.intro}</div>
            <div className="panel-sub">{feed.sourceLabel}</div>
          </div>
          <span className="tag">07_history</span>
        </div>

        {feed.status === "degraded" && feed.degradedReason ? (
          <p className="panel-sub degraded-feed-note" role="status">
            {feed.degradedReason}
          </p>
        ) : null}

        {feed.status === "empty" ? (
          <p className="panel-sub">No workflow or snapshot history rows yet.</p>
        ) : null}

        <div className="history-list">
          {feed.entries.map((entry) => (
            <div key={entry.id} className={`history-row state-${entry.state}`}>
              <div className="history-meta">
                <span className={`tag history-state ${entry.state}`}>{stateLabels[entry.state]}</span>
                <span className="history-ts">{entry.timestamp}</span>
              </div>
              <h3>{entry.title}</h3>
              <p>{entry.detail}</p>
            </div>
          ))}
        </div>

        <div className="history-empty-note">
          <strong>Executed</strong> — no live positions connected; preview routing only.
        </div>
      </section>

      <p className="footer-note">Research demo — live workflow + snapshot history; no live order transmitted</p>
    </>
  );
}
