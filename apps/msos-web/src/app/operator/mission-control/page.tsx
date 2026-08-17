import type { Metadata } from "next";
import { AppShell } from "@/components/AppShell";
import { MarketStructureProjectMap } from "@/components/MarketStructureProjectMap";
import { MarketStructureSandbox } from "@/components/MarketStructureSandbox";
import { MultiScaleStructureProbe } from "@/components/MultiScaleStructureProbe";
import { ProbeAutoRefresh } from "@/components/ProbeAutoRefresh";
import { ResearchEvidenceSummary } from "@/components/ResearchEvidenceSummary";
import { ResearchExperimentPanel } from "@/components/ResearchExperimentPanel";
import { operatingLoopProbe } from "@/data/operatingLoopProbe";
import { loadMarketStructureProbeState } from "@/lib/marketStructureProbe";
import { loadSignalCaptureProbeState } from "@/lib/signalCaptureProbe";

export const metadata: Metadata = { title: "Market Structure Project Console | Market Structure OS" };
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

function Finding({ title, detail }: { title: string; detail: string }) {
  return <div className="panel compact"><strong>{title}</strong><div className="panel-sub" style={{ marginTop: "0.3rem" }}>{detail}</div></div>;
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
          <div className="crumb">Market Structure / Project Console</div>
          <h1 className="title">Market Structure OS</h1>
        </div>
        <div className="tools"><ProbeAutoRefresh intervalMs={15000} /><span className="pill">Research only · no trading</span></div>
      </header>

      <MarketStructureProjectMap
        captureStatus={capture.status}
        captureDetail={capture.detail}
        engineStatus={structure.status}
        engineDetail={structure.detail}
      />

      <section className="panel" id="infrastructure" style={{ marginTop: "1rem" }}>
        <div className="panel-sub">LANE 1 · INFRASTRUCTURE</div>
        <h2 style={{ margin: "0.15rem 0 0.4rem" }}>Can we collect, preserve and replay market data well enough to do science?</h2>
        <p style={{ marginTop: 0, maxWidth: "940px" }}>
          Infrastructure is not the strategy. Its job is to make every future experiment trustworthy and reproducible. Generic exchange connectivity and execution should stay with OCT / Hummingbot where possible; this project should own only the evidence and research plumbing that makes market-structure work distinctive.
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "0.6rem" }}>
          <Card eyebrow="1A · SIGNAL CAPTURE" title="Normalized observations" status={capture.status} detail={capture.detail} />
          <Card eyebrow="1B · REPLAYABLE DATA" title="Historical evidence" status="WORKING · IMPROVEMENT NEEDED" detail="V0 was preserved, but NDAX later stopped returning some old minute history. Future experiments should snapshot replayable raw inputs as well as summary results." />
          <Card eyebrow="1C · STRUCTURE ENGINE" title="Features and market state" status={structure.status} detail={structure.detail} />
          <Card eyebrow="1D · RESEARCH UI" title="MSOS Project Console" status="STAGING LIVE" detail="Human-facing place to understand the project, explore hypotheses, preserve tests and eventually package the workflow for other users." />
        </div>
        <details style={{ marginTop: "0.75rem" }}>
          <summary style={{ cursor: "pointer", fontWeight: 700 }}>Infrastructure details / feed health</summary>
          <div style={{ marginTop: "0.7rem" }}>
            <Card eyebrow="DATA HEALTH" title="Can we trust the incoming observations?" status={capture.status} detail={capture.detail}>
              {ndaxReady ? (
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(145px, 1fr))", gap: "0.5rem", marginTop: "0.5rem" }}>
                  <div className="panel compact"><div className="panel-sub">NDAX observations</div><strong>{ndax.l1_observations ?? "—"}</strong></div>
                  <div className="panel compact"><div className="panel-sub">15m price range</div><strong>{fmt(ndax.range_pct, 3, "%")}</strong></div>
                  <div className="panel compact"><div className="panel-sub">Typical spread</div><strong>{fmt(ndax.median_spread_bps, 2, " bps")}</strong></div>
                  <div className="panel compact"><div className="panel-sub">Largest observation gap</div><strong>{fmt(ndax.max_gap_seconds, 1, "s")}</strong></div>
                  <div className="panel compact"><div className="panel-sub">Jupiter comparison feed</div><strong>{jupiterReady ? `${jupiter.quote_observations ?? "—"} quotes` : "waiting"}</strong></div>
                </div>
              ) : null}
            </Card>
          </div>
        </details>
      </section>

      <section className="panel" id="research" style={{ marginTop: "1rem" }}>
        <div className="panel-sub">LANE 2 · ACTIVE RESEARCH</div>
        <div className="row" style={{ gap: "0.7rem", alignItems: "center", flexWrap: "wrap" }}>
          <h2 style={{ margin: "0.15rem 0" }}>🟡 Searching for an edge</h2>
          <span className="tag muted">ACTIVE EXPLORATION</span>
        </div>
        <p style={{ maxWidth: "940px" }}>
          There is currently <strong>no locked V1 hypothesis</strong>. We are exploring the completed V0 evidence to find narrower rules worth testing. Exploration can generate ideas; only a fresh untouched test can validate one.
        </p>
        <div className="panel compact" style={{ margin: "0.7rem 0" }}>
          <div className="panel-sub">THE PERMANENT RESEARCH LOOP</div>
          <div style={{ marginTop: "0.35rem", fontWeight: 700 }}>EXPLORE → CANDIDATE → LOCK HYPOTHESIS → FRESH TEST → DECISION → LEARN → NEXT HYPOTHESIS</div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "0.55rem" }}>
          <Step number={1} title="Explore" detail="Move dials and inspect patterns. This is allowed to be messy." />
          <Step number={2} title="Candidate" detail="Write down an interesting rule and why it might work." />
          <Step number={3} title="Lock for test" detail="Freeze the exact rule and evaluation plan before seeing fresh outcomes." />
          <Step number={4} title="Fresh test" detail="Run on untouched data with controls and enough events." />
          <Step number={5} title="Learn" detail="Pass, fail or inconclusive all become permanent evidence in the test library." />
        </div>
        <div className="panel compact" style={{ marginTop: "0.7rem" }}>
          <div className="panel-sub">WHAT SHOULD I DO?</div>
          <strong>Use the sandbox below. The important number is detector versus control. Interesting is not the same as validated.</strong>
        </div>
      </section>

      <div style={{ marginTop: "0.8rem" }}>
        <MarketStructureSandbox />
      </div>

      <section className="panel" id="test-library" style={{ marginTop: "1rem" }}>
        <div className="panel-sub">LANE 3 · TEST LIBRARY</div>
        <h2 style={{ margin: "0.15rem 0 0.4rem" }}>Every test we run stays here permanently.</h2>
        <p style={{ marginTop: 0, maxWidth: "940px" }}>
          This is our institutional memory. We should be able to come back after test #30 and instantly see what question was asked, what data was used, what happened, what we learned and whether the idea advanced.
        </p>
        <div className="panel compact" style={{ marginBottom: "0.65rem" }}>
          <div className="row" style={{ justifyContent: "space-between", gap: "0.75rem", flexWrap: "wrap" }}>
            <div>
              <div className="panel-sub">TEST 4 · PRIMARY V0 BATCH · JUL 18–AUG 14</div>
              <strong style={{ fontSize: "1.1rem" }}>Persistent levels → future reaction</strong>
              <div className="panel-sub" style={{ marginTop: "0.25rem" }}>Question: {probe.successQuestion}</div>
            </div>
            <span className="tag muted">NO EDGE DEMONSTRATED</span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(155px, 1fr))", gap: "0.45rem", marginTop: "0.65rem" }}>
            <div className="panel compact"><div className="panel-sub">Detected levels</div><strong>24 / 144 · 16.67%</strong></div>
            <div className="panel compact"><div className="panel-sub">Controls</div><strong>26 / 137 · 18.98%</strong></div>
            <div className="panel compact"><div className="panel-sub">Difference</div><strong>−2.31 pp</strong></div>
            <div className="panel compact"><div className="panel-sub">Decision</div><strong>Do not advance</strong></div>
          </div>
          <div className="panel-sub" style={{ marginTop: "0.55rem" }}>Learned: recurring-looking structure exists, but this specific bounce/reaction rule did not predict better than matched controls.</div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "0.6rem" }}>
          {probe.priorEvidence.map((item, index) => (
            <div className="panel compact" key={item.label}>
              <div className="panel-sub">TEST {index + 1}</div>
              <strong>{item.label}</strong>
              <div className="tiny-pill" style={{ display: "inline-block", margin: "0.45rem 0" }}>{item.result}</div>
              <div className="panel-sub">{item.detail}</div>
            </div>
          ))}
        </div>
        <div className="row" style={{ gap: "0.55rem", flexWrap: "wrap", marginTop: "0.7rem" }}>
          <a className="btn" href="/docs/market-structure-v0-report.md" target="_blank" rel="noreferrer">Read / share full V0 report (.md)</a>
        </div>
      </section>

      <section className="panel" id="findings" style={{ marginTop: "1rem" }}>
        <div className="panel-sub">LANE 4 · WHAT WE KNOW</div>
        <h2 style={{ margin: "0.15rem 0 0.4rem" }}>Findings accumulate even when strategies fail.</h2>
        <p style={{ marginTop: 0, maxWidth: "940px" }}>
          A failed hypothesis is still useful if it permanently reduces uncertainty. This section becomes the market-structure knowledge base that future tests and eventually customers can build on.
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "0.6rem" }}>
          <Finding title="Data quality is scale-dependent" detail="NDAX SOL/CAD is poor for fine-grained reference but becomes more usable on larger time scales." />
          <Finding title="Persistent structure is detectable" detail="The engine can identify recurring levels that persist across multiple timeframes." />
          <Finding title="Detection is not prediction" detail="V0 proved that visually meaningful recurring levels do not automatically predict a bounce or reaction." />
          <Finding title="Controls are mandatory" detail="Without matched controls, the same V0 result could easily have looked impressive even though it underperformed the baseline." />
          <Finding title="Raw evidence must be preserved" detail="Exchange history retention changed after V0. Future experiments should snapshot replayable inputs so old tests remain reproducible." />
          <Finding title="Signal is not strategy" detail="Even a predictive pattern still needs direction, entry, exit, sizing, instrument choice and costs before it has trading EV." />
        </div>
      </section>

      <section className="panel" id="strategy" style={{ marginTop: "1rem" }}>
        <div className="panel-sub">LANE 5 · STRATEGY + HUMMINGBOT</div>
        <h2 style={{ margin: "0.15rem 0 0.4rem" }}>This lane stays blocked until research earns it.</h2>
        <p style={{ marginTop: 0, maxWidth: "940px" }}>
          A validated signal is the input to strategy construction, not the end of the project. Only then do we define how to trade it, model costs, choose spot/perps/options/LP expression, and hand the finished strategy to Hummingbot for backtesting and paper execution.
        </p>
        <div className="row" style={{ gap: "0.45rem", flexWrap: "wrap", alignItems: "center", margin: "0.7rem 0" }}>
          <span className="tiny-pill">VALIDATED SIGNAL</span><strong>→</strong>
          <span className="tiny-pill">ENTRY / EXIT</span><strong>→</strong>
          <span className="tiny-pill">COSTS + RISK</span><strong>→</strong>
          <span className="tiny-pill">INSTRUMENT</span><strong>→</strong>
          <span className="tiny-pill">BACKTEST</span><strong>→</strong>
          <span className="tiny-pill">PAPER</span><strong>→</strong>
          <span className="tiny-pill">LIVE LATER</span>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "0.6rem" }}>
          <Card eyebrow="CURRENT" {...probe.decide} />
          <Card eyebrow="CURRENT" {...probe.execute} />
        </div>
        <div className="panel compact" style={{ marginTop: "0.7rem" }}>
          <div className="panel-sub">V0 stops before strategy backtesting</div>
          <strong>Correct behavior: do nothing here until a future hypothesis survives validation.</strong>
        </div>
      </section>

      <section className="panel" id="product" style={{ marginTop: "1rem" }}>
        <div className="panel-sub">LANE 6 · PRODUCTIZATION</div>
        <h2 style={{ margin: "0.15rem 0 0.4rem" }}>We are building toward two possible valuable outcomes.</h2>
        <p style={{ marginTop: 0, maxWidth: "960px" }}>
          We keep researching until we find real trading value <strong>or</strong> the research system itself becomes detailed, reproducible and easy enough that other traders or teams would pay to use it. Those paths reinforce each other.
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "0.6rem" }}>
          <Card eyebrow="PRODUCT A" title="Edge-producing engine" status="NOT THERE YET" detail="Find validated market-state signals, construct robust strategies around them, and monetize the resulting trading edge." />
          <Card eyebrow="PRODUCT B" title="Research operating system" status="EMERGING" detail="Let another researcher bring data or an idea, explore it visually, lock a hypothesis, test it honestly, preserve the evidence and understand what to do next." />
        </div>
        <div className="panel compact" style={{ marginTop: "0.7rem" }}>
          <div className="panel-sub">PRODUCT MATURITY LADDER</div>
          <div className="row" style={{ gap: "0.45rem", flexWrap: "wrap", alignItems: "center", marginTop: "0.45rem" }}>
            <span className="tiny-pill">INTERNAL TOOL · NOW</span><strong>→</strong>
            <span className="tiny-pill">REPEATABLE RESEARCH SYSTEM</span><strong>→</strong>
            <span className="tiny-pill">MULTI-MARKET WORKBENCH</span><strong>→</strong>
            <span className="tiny-pill">STRATEGY WORKFLOW</span><strong>→</strong>
            <span className="tiny-pill">EXTERNAL PRODUCT</span>
          </div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))", gap: "0.55rem", marginTop: "0.7rem" }}>
          <Finding title="Easy to understand" detail="A new user can see the full pipeline, current state, blockers and next action without knowing the codebase." />
          <Finding title="Easy to experiment" detail="Important definitions become real controls rather than hidden constants or agent-only code changes." />
          <Finding title="Scientifically honest" detail="Exploration is separated from locked tests; every result and failure remains auditable." />
          <Finding title="Reusable" detail="New markets, features, hypotheses and instruments plug into the same workflow instead of creating a new project every time." />
        </div>
      </section>

      <details className="panel" style={{ marginTop: "1rem" }}>
        <summary style={{ cursor: "pointer", fontWeight: 800, fontSize: "1.05rem" }}>
          Advanced / project details — raw evidence, live detector, saved experiment machinery and V0 lifecycle
        </summary>
        <div style={{ display: "grid", gap: "1rem", marginTop: "1rem" }}>
          <section>
            <div className="panel-sub" style={{ marginBottom: "0.45rem" }}>LIVE MARKET · WHAT DOES THE DETECTOR SEE RIGHT NOW?</div>
            <MultiScaleStructureProbe payload={structure.payload} sourceStatus={structure.status} sourceDetail={structure.detail} />
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

          <ResearchExperimentPanel />

          <section className="panel compact">
            <div className="panel-sub">V0 LIFECYCLE</div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "0.5rem", marginTop: "0.55rem" }}>
              {probe.stages.map(stage => (
                <div key={stage.id} className="panel compact" style={{ textAlign: "center" }}>
                  <div style={{ fontSize: "1.2rem" }}>{mark(stage.status)}</div>
                  <strong>{stage.label}</strong>
                  <div className="panel-sub" style={{ marginTop: "0.25rem" }}>{stage.detail}</div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </details>
    </AppShell>
  );
}
