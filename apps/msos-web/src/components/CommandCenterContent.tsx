import Link from "next/link";

import {
  calibrationStrip,
  currentWork,
  headlines,
  kpis,
  labTiles,
  reviewEvents,
} from "@/data/commandCenterFixtures";

export function CommandCenterContent() {
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
            Preview data healthy
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
        </div>
      </section>

      <section className="kpi-row" aria-label="Key metrics">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="kpi">
            <div className="label">{kpi.label}</div>
            <div className={`num ${kpi.tone ?? ""}`.trim()}>{kpi.value}</div>
            <div className="sub">{kpi.sub}</div>
          </div>
        ))}
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
              <div className="panel-sub">Lifecycle states stay explicit.</div>
            </div>
          </div>
          {currentWork.map((item) => (
            <div key={item.name} className="strategy">
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

      <p className="footer-note">Illustrative product preview — no live order transmitted</p>
    </>
  );
}
