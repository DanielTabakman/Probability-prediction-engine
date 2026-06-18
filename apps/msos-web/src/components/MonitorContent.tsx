import Link from "next/link";

import type { MonitorFeed } from "@/lib/monitorHistoryFeed";

type Props = {
  feed: MonitorFeed;
};

function statusPill(feed: MonitorFeed): string {
  if (feed.status === "live") return "MSOS + PPE snapshots live";
  if (feed.status === "empty") return "Monitoring ready — add thesis or freeze";
  return "Monitoring feed degraded";
}

export function MonitorContent({ feed }: Props) {
  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Monitor / Thesis &amp; expression watch</div>
          <h1 className="title">Monitor</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className={`dot ${feed.status === "degraded" ? "red" : feed.status === "live" ? "teal" : "amber"}`} aria-hidden="true" />
            {statusPill(feed)}
          </span>
          <Link href="/command-center" className="btn slim">
            Command Center
          </Link>
        </div>
      </header>

      <section className="work monitor-layout">
        <div className="panel">
          <div className="statushero">
            <div>
              <div className="panel-sub">{feed.sourceLabel}</div>
              <h1>{feed.heroTitle}</h1>
              <p>{feed.heroSubtitle}</p>
            </div>
            <span className="tag teal">Watch</span>
          </div>
          {feed.status === "degraded" && feed.degradedReason ? (
            <p className="panel-sub degraded-feed-note" role="status">
              {feed.degradedReason}
            </p>
          ) : null}
          <div className="meter" aria-hidden="true" style={{ ["--meter-pct" as string]: `${feed.healthPct}%` }} />
          <div className="side-label">{feed.healthLabel}</div>

          <div className="watch-grid" aria-label="Monitoring panels">
            {feed.watchPanels.map((panel) => (
              <div key={panel.id} className="watch">
                <span className={`tag ${panel.tone}`}>{panel.id}</span>
                <h3>{panel.title}</h3>
                <p>{panel.body}</p>
              </div>
            ))}
          </div>
        </div>

        <aside className="panel monitor-side">
          <div className="panel-head">
            <h2>Alerts &amp; calibration</h2>
            <div className="panel-sub">From MSOS workflow + PPE review metadata — not trade advice.</div>
          </div>
          {feed.alerts.map((alert) => (
            <div key={alert.title} className="alert">
              <span className={`spot ${alert.tone}`} aria-hidden="true" />
              <div>
                <h4>{alert.title}</h4>
                <p>{alert.body}</p>
              </div>
            </div>
          ))}
          <Link href="/history" className="btn slim primary monitor-history-link">
            View history →
          </Link>
        </aside>
      </section>

      <p className="footer-note">Research demo — live workflow + snapshot monitoring; no live order transmitted</p>
    </>
  );
}
