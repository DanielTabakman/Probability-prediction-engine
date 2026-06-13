import Link from "next/link";

import { lensTiles, outcomeSummary, strategyLabMetrics } from "@/data/strategyLabFixtures";
import { FeedbackForm } from "@/components/FeedbackForm";
import { PpeEmbedBoundary } from "@/components/PpeEmbedBoundary";

export function StrategyLabContent() {
  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Strategy Lab / PPE / Distribution summary</div>
          <h1 className="title">Strategy Lab — research demo</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot" aria-hidden="true" />
            Live via PPE when embed wired
          </span>
          <span className="btn slim">Share view</span>
          <Link href="/strategy-lab/confirm" className="btn slim primary">
            Save draft thesis
          </Link>
          <span className="avatar" aria-hidden="true">
            DT
          </span>
        </div>
      </header>

      <section className="metrics" aria-label="Lab context">
        {strategyLabMetrics.map((metric) => (
          <div key={metric.label} className="metric">
            <div className="label">{metric.label}</div>
            <div className={`value ${metric.tone ?? ""}`.trim()}>{metric.value}</div>
          </div>
        ))}
      </section>

      <section className="work strategy-lab-work">
        <div className="panel chart">
          <div className="belief-builder">
            <h3>What do you believe?</h3>
            <div className="selectline">
              I believe BTC will <span className="selectchip">remain within a narrower range</span> than the market
              prices over <span className="selectchip">30 days</span>.
            </div>
            <p className="micro">Natural thesis builder first; authoritative stats live in the embedded PPE lab below.</p>
          </div>

          <div className="panel-head">
            <div>
              <h2>Distribution summary (live PPE)</h2>
              <div className="panel-sub">
                Research-demo path: embedded implied lab shows labeled mean and quartiles per expiry — math stays in
                Python / Streamlit.
              </div>
            </div>
            <span className="tag">PPE</span>
          </div>

          <PpeEmbedBoundary />

          <div className="panel-head compact">
            <div>
              <h2>Market lenses</h2>
              <div className="panel-sub">BTC options live via PPE; other lenses planned or pending.</div>
            </div>
          </div>
          <div className="lab-list compact">
            {lensTiles.map((tile) =>
              tile.live && tile.href ? (
                <Link key={tile.title} href={tile.href} className="lab-tile">
                  <div className="lab-mark">{tile.mark}</div>
                  <div>
                    <h3>{tile.title}</h3>
                    <p>{tile.description}</p>
                  </div>
                  <span className="tiny-pill">{tile.status}</span>
                </Link>
              ) : (
                <div key={tile.title} className="lab-tile muted">
                  <div className="lab-mark">{tile.mark}</div>
                  <div>
                    <h3>{tile.title}</h3>
                    <p>{tile.description}</p>
                  </div>
                  <span className="tag muted">{tile.status}</span>
                </div>
              ),
            )}
          </div>
        </div>

        <div className="panel outcome">
          <div className="panel-head">
            <div>
              <h2>What this run is saying</h2>
              <div className="panel-sub">Decision support, not trade advice.</div>
            </div>
            <span className={`tag ${outcomeSummary.tagTone}`}>{outcomeSummary.tag}</span>
          </div>
          <div className="bigdelta">{outcomeSummary.delta}</div>
          <h2 className="outcome-headline">{outcomeSummary.headline}</h2>
          <p className="bodycopy">{outcomeSummary.body}</p>
          <div className="score">
            {outcomeSummary.scores.map((item) => (
              <div key={item.label} className="small-panel">
                <div className="k">{item.label}</div>
                <div className={`v ${item.tone}`}>{item.value}</div>
              </div>
            ))}
          </div>
          <div className="decision-strip">
            <div>
              <strong>Candidate: narrower-range disagreement</strong>
              <p>Potential expression families available after thesis confirmation.</p>
            </div>
            <Link href="/strategy-lab/confirm" className="btn slim primary">
              Confirm thesis →
            </Link>
          </div>
        </div>
      </section>

      <section className="panel feedback-lab-panel">
        <div className="panel-head compact">
          <div>
            <h2>Quick feedback</h2>
            <div className="panel-sub">Three questions — helps us prioritize the research beta.</div>
          </div>
          <Link href="/feedback" className="btn slim dark">
            Full page
          </Link>
        </div>
        <FeedbackForm pagePath="/strategy-lab" compact />
      </section>

      <p className="footer-note">Research demo — fixture panels beside live PPE embed; no live order transmitted</p>
    </>
  );
}
