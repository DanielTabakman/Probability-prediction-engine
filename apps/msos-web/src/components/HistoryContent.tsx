import Link from "next/link";

import type { HistoryFeed, HistoryState } from "@/lib/monitorHistoryFeed";
import { DEMO_FOOTER, friendlySnapshotFeedMessage } from "@/lib/publicCopy";

const stateLabels: Record<HistoryState, string> = {
  observed: "Looked",
  saved: "Saved",
  simulated: "Paper",
  reviewed: "Reviewed",
};

type Props = {
  feed: HistoryFeed;
};

function statusPill(feed: HistoryFeed): string {
  if (feed.status === "live") return "Timeline active";
  if (feed.status === "empty") return "Nothing saved yet";
  return "Offline";
}

export function HistoryContent({ feed }: Props) {
  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">History</div>
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
            <h2>Your trail</h2>
            <div className="panel-sub">{feed.intro}</div>
            <div className="panel-sub">{feed.sourceLabel}</div>
          </div>
          <span className="tag">History</span>
        </div>

        {feed.status === "degraded" ? (
          <p className="panel-sub degraded-feed-note" role="status">
            {friendlySnapshotFeedMessage(feed.degradedReason)}
          </p>
        ) : null}

        {feed.status === "empty" ? (
          <p className="panel-sub">Save a view in Strategy Lab to start building history.</p>
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
          <strong>Live trades</strong> — not connected on this demo. Paper plans only.
        </div>
      </section>

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
