import Link from "next/link";

import { historyEntries, historyIntro, stateLabels } from "@/data/historyFixtures";

export function HistoryContent() {
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
            Preview timeline
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
            <div className="panel-sub">{historyIntro}</div>
          </div>
          <span className="tag">07_history</span>
        </div>

        <div className="history-list">
          {historyEntries.map((entry) => (
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
          <strong>Executed</strong> — no live positions connected in preview.
        </div>
      </section>

      <p className="footer-note">Research demo — history fixtures only; no live order transmitted</p>
    </>
  );
}
