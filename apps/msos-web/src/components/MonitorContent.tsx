import Link from "next/link";

import { monitorAlerts, monitorHero, watchPanels } from "@/data/monitoringFixtures";

export function MonitorContent() {
  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Monitor / Thesis &amp; expression watch</div>
          <h1 className="title">Monitor</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot amber" aria-hidden="true" />
            Preview monitoring — no live fills
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
              <div className="panel-sub">Storyboard 06_monitor</div>
              <h1>{monitorHero.title}</h1>
              <p>{monitorHero.subtitle}</p>
            </div>
            <span className="tag teal">Watch</span>
          </div>
          <div className="meter" aria-hidden="true" style={{ ["--meter-pct" as string]: `${monitorHero.healthPct}%` }} />
          <div className="side-label">{monitorHero.healthLabel}</div>

          <div className="watch-grid" aria-label="Monitoring panels">
            {watchPanels.map((panel) => (
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
            <div className="panel-sub">Honest fixture copy — not trade advice.</div>
          </div>
          {monitorAlerts.map((alert) => (
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

      <p className="footer-note">Research demo — monitoring fixtures only; no live order transmitted</p>
    </>
  );
}
