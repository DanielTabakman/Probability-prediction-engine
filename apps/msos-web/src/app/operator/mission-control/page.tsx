import type { Metadata } from "next";
import { AppShell } from "@/components/AppShell";
import { MarketStructureSandbox } from "@/components/MarketStructureSandbox";
import { MultiScaleStructureProbe } from "@/components/MultiScaleStructureProbe";
import { ProbeAutoRefresh } from "@/components/ProbeAutoRefresh";
import { ResearchEvidenceSummary } from "@/components/ResearchEvidenceSummary";
import { ResearchExperimentPanel } from "@/components/ResearchExperimentPanel";
import { operatingLoopProbe } from "@/data/operatingLoopProbe";
import { loadMarketStructureProbeState } from "@/lib/marketStructureProbe";
import { loadSignalCaptureProbeState } from "@/lib/signalCaptureProbe";

export const metadata: Metadata = { title: "Market Structure Lab | Market Structure OS" };
export const dynamic = "force-dynamic";

function fmt(value: number | null | undefined, digits = 2, suffix = "") {
  return typeof value === "number" && Number.isFinite(value) ? `${value.toFixed(digits)}${suffix}` : "—";
}

function mark(status: "done" | "blocked") {
  return status === "done" ? "✓" : "×";
}

function Card({ eyebrow, title, status, detail, children }: { eyebrow: string; title: string; status: string; detail: string; children?: React.ReactNode }) {
  return <section className="panel compact">
    <div className="panel-sub">{eyebrow}</div>
    <div className="row" style={{ alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
      <h2 style={{ margin: 0 }}>{title}</h2>
      <span className="tag muted">{status}</span>
    </div>
    <p style={{ marginBottom: children ? "0.75rem" : 0 }}>{detail}</p>
    {children}
  </section>;
}

function Step({ number, title, detail }: { number: number; title: string; detail: string }) {
  return <div className="panel compact" style={{ display: "grid", gridTemplateColumns: "2rem 1fr", gap: "0.65rem", alignItems: "start" }}>
    <strong style={{ fontSize: "1.15rem" }}>{number}</strong>
    <div>
      <strong>{title}</strong>
      <div className="panel-sub" style={{ marginTop: "0.2rem" }}>{detail}</div>
    </div>
  </div>;
}

export default async function MissionControlPage() {
  const probe = operatingLoopProbe;
  const capture = await loadSignalCaptureProbeState();
  const structure = await loadMarketStructureProbeState();
  const ndax = capture.ndax15m;
  const jupiter = capture.jupiter15m;
  const ndaxReady = ndax?.status === "OK";
  const jupiterReady = jupiter?.status === "OK";

  return (
    <AppShell activeNavId="mission-control">
      <header className="topline">
        <div>
          <div className="crumb">Research / Founder View</div>
          <h1 className="title">Market Structure Lab</h1>
        </div>
        <div className="tools"><ProbeAutoRefresh intervalMs={15000} /><span className="pill">Research only · no trading</span></div>
      </header>

      <div style={{ display: "grid", gap: "0.8rem" }}>
        <section className="panel">
          <div className="panel-sub">WHERE ARE WE?</div>
          <div className="row" style={{ alignItems: "center", gap: "0.7rem", flexWrap: "wrap" }}>
            <h2 style={{ margin: "0.15rem 0" }}>🟡 Searching for an edge</h2>
            <span className="tag muted">CURRENT STAGE</span>
          </div>
          <p style={{ marginBottom: "0.45rem", maxWidth: "920px" }}>
            V0 tested one simple idea: <strong>when price returns to persistent multi-timeframe levels, does it react more often than at matched control levels?</strong>
          </p>
          <div className="panel compact" style={{ marginTop: "0.6rem" }}>
            <div className="panel-sub">V0 RESULT</div>
            <strong style={{ fontSize: "1.15rem" }}>❌ No demonstrated edge.</strong>
            <div className="panel-sub" style={{ marginTop: "0.3rem" }}>
              The detected levels did not beat the controls. That does not mean market structure is useless; it means this particular rule did not work.
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel-sub">WHAT ARE WE DOING NOW?</div>
          <h2 style={{ margin: "0.15rem 0 0.45rem" }}>Using the sandbox to figure out what part of the setup actually matters.</h2>
          <p style={{ marginTop: 0, maxWidth: "920px" }}>
            Instead of assuming every persistent level should bounce, we change the rules and look for narrower patterns that behave differently.
          </p>
          <div className="row" style={{ gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
            <span className="tiny-pill">Level strength</span>
            <strong>→</strong>
            <span className="tiny-pill">How price approaches</span>
            <strong>→</strong>
            <span className="tiny-pill">What happens afterward</span>
          </div>
        </section>

        <section className="panel">
          <div className="panel-sub">WHAT SHOULD I DO?</div>
          <h2 style={{ margin: "0.15rem 0 0.65rem" }}>Play with the rule. Watch whether the detected levels start beating the controls.</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0.55rem" }}>
            <Step number={1} title="Move a dial" detail="Try persistence, timeframe, level type, or outcome size." />
            <Step number={2} title="Watch the difference" detail="Detector minus control is the number that matters. Positive is interesting, not validated." />
            <Step number={3} title="Notice a pattern" detail="If one rule keeps looking different, treat it as a candidate hypothesis." />
            <Step number={4} title="Freeze it as V1" detail="Then test that exact rule on fresh data it has never seen." />
          </div>
          <div className="panel compact" style={{ marginTop: "0.7rem" }}>
            <strong>THE LOOP</strong>
            <div style={{ marginTop: "0.25rem" }}>SEE PATTERN → PLAY WITH RULE → FIND SOMETHING INTERESTING → FREEZE IT → TEST ON NEW DATA</div>
          </div>
        </section>

        <section className="panel compact">
          <div className="panel-sub">WHAT WORKS RIGHT NOW?</div>
          <strong>Basic sandbox: live.</strong>
          <div className="panel-sub" style={{ marginTop: "0.25rem" }}>
            You can explore the frozen V0 evidence with persistence, timeframe, level type, sample window and outcome size. The deeper raw-path replay for touch distance, horizon, rejection and breakout is built but still waiting for the separate research engine runtime update.
          </div>
        </section>
      </div>

      <div style={{ marginTop: "1rem" }}>
        <MarketStructureSandbox />
      </div>

      <details className="panel" style={{ marginTop: "1rem" }}>
        <summary style={{ cursor: "pointer", fontWeight: 800, fontSize: "1.05rem" }}>
          Advanced / project details — evidence, live detector, feed health, experiment history and Hummingbot status
        </summary>

        <div style={{ display: "grid", gap: "1rem", marginTop: "1rem" }}>
          <section className="panel compact">
            <div className="panel-sub">PROJECT CONTEXT</div>
            <h2 style={{ marginBottom: "0.35rem" }}>A research lab that tests market ideas before they become Hummingbot strategies.</h2>
            <p style={{ marginBottom: "0.35rem" }}>
              V0 asked one narrow question: do recurring multi-scale price levels predict future reactions better than matched control levels? We built the detector, ran historical and prospective tests, and now have a complete v0 research decision.
            </p>
            <div className="panel compact" style={{ margin: "0.75rem 0" }}>
              <div className="panel-sub">TEAM BRIEF · SHARE THIS</div>
              <div className="row" style={{ alignItems: "center", justifyContent: "space-between", gap: "0.75rem", flexWrap: "wrap" }}>
                <div style={{ maxWidth: "760px" }}>
                  <strong>Market Structure V0 — full project report</strong>
                  <div className="panel-sub" style={{ marginTop: "0.25rem" }}>
                    One Markdown memo with the context, architecture, exact hypothesis, evidence, interpretation, what v0 is useful for, and where a future v1 could go.
                  </div>
                </div>
                <a className="btn" href="/docs/market-structure-v0-report.md" target="_blank" rel="noreferrer">Read / share full V0 report (.md)</a>
              </div>
            </div>
            <p className="panel-sub" style={{ marginBottom: "0.8rem" }}><strong>V0 question:</strong> {probe.successQuestion}</p>
            <div className="panel-sub" style={{ marginBottom: "0.45rem" }}>V0 LIFECYCLE</div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "0.5rem" }}>
              {probe.stages.map(stage => (
                <div key={stage.id} className="panel compact" style={{ textAlign: "center" }}>
                  <div style={{ fontSize: "1.2rem" }}>{mark(stage.status)}</div>
                  <strong>{stage.label}</strong>
                  <div className="panel-sub" style={{ marginTop: "0.25rem" }}>{stage.detail}</div>
                </div>
              ))}
            </div>
          </section>

          <ResearchEvidenceSummary
            status={probe.researchStatus.status}
            headline={probe.researchStatus.headline}
            summary={probe.researchStatus.summary}
            whatWeKnow={probe.researchStatus.whatWeKnow}
            whatWeDoNotKnow={probe.researchStatus.whatWeDoNotKnow}
            nextAction={probe.researchStatus.nextAction}
            evidence={probe.primaryEvidence}
            priorEvidence={probe.priorEvidence}
          />

          <section>
            <div className="panel-sub" style={{ marginBottom: "0.45rem" }}>LIVE MARKET · WHAT DOES THE DETECTOR SEE RIGHT NOW?</div>
            <MultiScaleStructureProbe payload={structure.payload} sourceStatus={structure.status} sourceDetail={structure.detail} />
            <p className="panel-sub" style={{ margin: "0.45rem 0 0" }}>
              Live levels are still useful as research observations. V0 validation showed that seeing recurring structure is not enough to treat those levels as predictive signals.
            </p>
          </section>

          <Card eyebrow="DATA HEALTH · SUPPORTING DETAIL" title="Can we trust the incoming observations?" status={capture.status} detail={capture.detail}>
            {ndaxReady ? (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(145px, 1fr))", gap: "0.5rem", marginTop: "0.5rem" }}>
                <div className="panel compact"><div className="panel-sub">NDAX observations</div><strong>{ndax.l1_observations ?? "—"}</strong></div>
                <div className="panel compact"><div className="panel-sub">15m price range</div><strong>{fmt(ndax.range_pct, 3, "%")}</strong></div>
                <div className="panel compact"><div className="panel-sub">Typical spread</div><strong>{fmt(ndax.median_spread_bps, 2, " bps")}</strong></div>
                <div className="panel compact"><div className="panel-sub">Largest observation gap</div><strong>{fmt(ndax.max_gap_seconds, 1, "s")}</strong></div>
                <div className="panel compact"><div className="panel-sub">Jupiter comparison feed</div><strong>{jupiterReady ? `${jupiter.quote_observations ?? "—"} quotes` : "waiting"}</strong></div>
              </div>
            ) : null}
            <details style={{ marginTop: "0.75rem" }}>
              <summary style={{ cursor: "pointer" }}>Capture source details</summary>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "0.5rem" }}>
                {capture.sourceStates.map(source => <span key={source.source} className="tiny-pill">{source.source}: {source.files || "—"}</span>)}
              </div>
            </details>
          </Card>

          <ResearchExperimentPanel />

          <section className="panel compact">
            <div className="panel-sub">WHAT THIS MEANS FOR HUMMINGBOT</div>
            <h2 style={{ marginBottom: "0.35rem" }}>V0 stops before strategy backtesting.</h2>
            <p style={{ marginBottom: "0.75rem" }}>
              The research console did its job: it prevented a visually plausible pattern from becoming a strategy before it demonstrated predictive value. Hummingbot remains the next layer only for future hypotheses that survive validation.
            </p>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "0.75rem" }}>
              <Card eyebrow="V0 · STRATEGY" {...probe.decide} />
              <Card eyebrow="V0 · HUMMINGBOT" {...probe.execute} />
            </div>
          </section>

          <section className="panel">
            <div className="panel-sub">NEXT RESEARCH DECISION</div>
            <h2 style={{ marginBottom: "0.35rem" }}>{probe.nextAction}</h2>
            <p className="panel-sub" style={{ marginBottom: 0 }}>
              V0 stays preserved exactly as tested. A future v1 can ask a different question, but it should be written down before inspecting its evaluation sample.
            </p>
          </section>
        </div>
      </details>
    </AppShell>
  );
}
