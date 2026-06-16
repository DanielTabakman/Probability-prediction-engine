import Link from "next/link";

import type { CommandCenterSummary } from "@/lib/commandCenterSummary";
import {
  calibrationStrip,
  headlines,
  labTiles,
  reviewEvents,
} from "@/data/commandCenterFixtures";

type Props = {
  summary: CommandCenterSummary;
};

export function CommandCenterContent({ summary }: Props) {
  const isLive = summary.status === "live";
  const kpis = isLive ? summary.kpis : [];
  const currentWork = isLive ? summary.currentWork : [];

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
            {isLive ? "Snapshot feed live" : "Snapshot feed unavailable"}
          </span>
          <span className="btn slim">Share view</span>
          <span className="btn slim primary">Create thesis</span>
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

      {!isLive ? (
        <section className="panel compact command-center-degraded" aria-live="polite">
          <span className="tag amber">Snapshot feed unavailable</span>
          <p>{summary.reason ?? "PPE snapshot database is not reachable from msos_web."}</p>
          <p className="panel-sub">
            KPI and current-work panels stay empty until <code>PPE_SNAPSHOT_DB_PATH</code> is wired
            (platform slice). Preview tiles below remain illustrative only.
          </p>
        </section>
      ) : null}

      <section className="kpi-row" aria-label="Key metrics">
        {kpis.length === 0 ? (
          <div className="kpi muted">
            <div className="label">Snapshot KPIs</div>
            <div className="num">—</div>
            <div className="sub">{isLive ? "No snapshots yet" : "Awaiting PPE snapshot DB"}</div>
          </div>
        ) : (
          kpis.map((kpi) => (
            <div key={kpi.label} className="kpi">
              <div className="label">{kpi.label}</div>
              <div className={`num ${kpi.tone ?? ""}`.trim()}>{kpi.value}</div>
              <div className="sub">{kpi.sub}</div>
            </div>
          ))
        )}
      </section>

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
            <span className="btn slim primary">Create new thesis →</span>
          </div>
          <div className="panel-head">
            <div>
              <h2>Current work</h2>
              <div className="panel-sub">{summary.sourceLabel} — read-only activity from frozen evaluations.</div>
            </div>
          </div>
          {currentWork.length === 0 ? (
            <p className="panel-sub">No recent snapshot rows to display.</p>
          ) : (
            currentWork.map((item) => (
              <div key={`${item.name}-${item.detail}`} className="strategy">
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

      <p className="footer-note">
        {isLive
          ? "Snapshot-sourced KPIs and current work — illustrative tiles and headlines remain preview-only."
          : "Snapshot feed degraded — no fixture KPI fallback. Illustrative preview tiles only."}
      </p>
    </>
  );
}
