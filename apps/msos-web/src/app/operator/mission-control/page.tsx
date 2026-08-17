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

function Stat({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return (
    <div className="panel compact">
      <div className="panel-sub">{label}</div>
      <strong style={{ fontSize: "1.05rem" }}>{value}</strong>
      {detail ? <div className="panel-sub" style={{ marginTop: "0.25rem" }}>{detail}</div> : null}
    </div>
  );
}

export default async function MissionControlPage() {
  const probe = operatingLoopProbe;
  const capture = await loadSignalCaptureProbeState();
  const structure = await loadMarketStructureProbeState();
  const ndax = capture.ndax15m;
  const jupiter = capture.jupiter15m;

  return (
    <AppShell activeNavId="mission-control">
      <header className="topline">
        <div>
          <div className="crumb">Market Structure / Lab</div>
          <h1 className="title">Market Structure Lab</h1>
        </div>
        <div className="tools">
          <ProbeAutoRefresh intervalMs={15000} />
          <span className="pill">Research only · no trading</span>
        </div>
      </header>

      <nav className="panel compact" aria-label="Market Structure Lab sections">
        <div className="row" style={{ gap: "0.5rem", flexWrap: "wrap" }}>
          <a className="btn" href="#live">1 · Live market</a>
          <a className="btn" href="#testing">2 · Testing</a>
          <a className="btn" href="#history">3 · Past tests</a>
          <a className="btn" href="#infrastructure">4 · Infrastructure</a>
          <a className="btn" href="#findings">5 · Findings</a>
        </div>
      </nav>

      <section className="panel" style={{ marginTop: "0.8rem" }}>
        <div className="panel-sub">RIGHT NOW</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "0.55rem", marginTop: "0.5rem" }}>
          <Stat label="MARKET DATA" value={capture.status} detail={capture.detail} />
          <Stat label="STRUCTURE ENGINE" value={structure.status} detail={structure.detail} />
          <Stat label="LAST COMPLETED RESEARCH" value="V0 · NO EDGE" detail="16.67% detector vs 18.98% matched controls." />
          <Stat label="CURRENT JOB" value="FIND V1 CANDIDATE" detail="Use the testing workspace below; nothing has advanced to strategy." />
        </div>
      </section>

      <section id="live" style={{ marginTop: "1rem" }}>
        <div className="panel" style={{ marginBottom: "0.65rem" }}>
          <div className="panel-sub">1 · LIVE MARKET</div>
          <h2 style={{ margin: "0.15rem 0 0.3rem" }}>What can we see right now?</h2>
          <p className="panel-sub" style={{ margin: 0 }}>This is the current detector output, not a description of the project.</p>
        </div>

        <MultiScaleStructureProbe payload={structure.payload} sourceStatus={structure.status} sourceDetail={structure.detail} />

        <div className="panel compact" style={{ marginTop: "0.65rem" }}>
          <div className="panel-sub">LIVE FEED SNAPSHOT</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(155px, 1fr))", gap: "0.5rem", marginTop: "0.5rem" }}>
            <Stat label="NDAX OBSERVATIONS" value={String(ndax?.l1_observations ?? "—")} />
            <Stat label="15M RANGE" value={fmt(ndax?.range_pct, 3, "%")} />
            <Stat label="TYPICAL SPREAD" value={fmt(ndax?.median_spread_bps, 2, " bps")} />
            <Stat label="LARGEST GAP" value={fmt(ndax?.max_gap_seconds, 1, "s")} />
            <Stat label="JUPITER QUOTES" value={String(jupiter?.quote_observations ?? "—")} />
          </div>
        </div>
      </section>

      <section id="testing" style={{ marginTop: "1.2rem" }}>
        <div className="panel" style={{ marginBottom: "0.65rem" }}>
          <div className="panel-sub">2 · TESTING WORKSPACE</div>
          <h2 style={{ margin: "0.15rem 0 0.3rem" }}>Change the rules and see what happens.</h2>
          <div className="row" style={{ gap: "0.5rem", flexWrap: "wrap", marginTop: "0.5rem" }}>
            <span className="tiny-pill">V0 IS FINISHED</span>
            <span className="tiny-pill">SANDBOX = EXPLORATION</span>
            <span className="tiny-pill">PROMISING RULE → NEW V1 TEST</span>
          </div>
        </div>
        <MarketStructureSandbox />
      </section>

      <section id="history" style={{ marginTop: "1.2rem" }}>
        <div className="panel" style={{ marginBottom: "0.65rem" }}>
          <div className="panel-sub">3 · PAST TESTS</div>
          <h2 style={{ margin: "0.15rem 0 0.3rem" }}>What have we actually tested already?</h2>
        </div>

        <div className="panel compact" style={{ marginBottom: "0.65rem" }}>
          <div className="row" style={{ justifyContent: "space-between", gap: "0.75rem", flexWrap: "wrap" }}>
            <div>
              <div className="panel-sub">PRIMARY V0 · JUL 18–AUG 14</div>
              <strong style={{ fontSize: "1.1rem" }}>Persistent multi-scale levels → future reaction</strong>
            </div>
            <span className="tag muted">NO EDGE DEMONSTRATED</span>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(155px, 1fr))", gap: "0.5rem", marginTop: "0.65rem" }}>
            <Stat label="DETECTOR" value="24 / 144" detail="16.67% reacted" />
            <Stat label="MATCHED CONTROL" value="26 / 137" detail="18.98% reacted" />
            <Stat label="DIFFERENCE" value="−2.31 pp" detail="detector minus control" />
            <Stat label="DECISION" value="STOP V0" detail="Do not advance to Hummingbot." />
          </div>
        </div>

        <ResearchExperimentPanel />

        <details className="panel" style={{ marginTop: "0.65rem" }}>
          <summary style={{ cursor: "pointer", fontWeight: 800 }}>Full V0 evidence / audit details</summary>
          <div style={{ marginTop: "0.75rem" }}>
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
          </div>
          <div className="row" style={{ marginTop: "0.65rem" }}>
            <a className="btn" href="/docs/market-structure-v0-report.md" target="_blank" rel="noreferrer">Open full V0 report</a>
          </div>
        </details>
      </section>

      <section className="panel" id="infrastructure" style={{ marginTop: "1.2rem" }}>
        <div className="panel-sub">4 · INFRASTRUCTURE</div>
        <h2 style={{ margin: "0.15rem 0 0.3rem" }}>What is working underneath the tests?</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0.55rem", marginTop: "0.65rem" }}>
          <Stat label="SIGNAL CAPTURE" value={capture.status} detail={capture.detail} />
          <Stat label="MARKET-STRUCTURE ENGINE" value={structure.status} detail={structure.detail} />
          <Stat label="FROZEN V0 REPLAY" value="AVAILABLE" detail="The saved V0 artifact powers the instant sandbox lens." />
          <Stat label="RAW PATH REPLAY" value="ENGINE DEPLOY PENDING" detail="The UI is wired, but Condor still needs the new replay runtime before this control is fully usable." />
          <Stat label="HUMMINGBOT" value="NOT IN USE" detail="Execution stays downstream until a signal validates." />
          <Stat label="LIVE TRADING" value="OFF" detail="No trading authority added." />
        </div>
      </section>

      <section className="panel" id="findings" style={{ marginTop: "1.2rem" }}>
        <div className="panel-sub">5 · FINDINGS SO FAR</div>
        <h2 style={{ margin: "0.15rem 0 0.4rem" }}>Things we have learned that should survive future tests.</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))", gap: "0.55rem", marginTop: "0.65rem" }}>
          <Stat label="FEED QUALITY" value="SCALE-DEPENDENT" detail="NDAX is poor at short horizons and more usable at larger ones." />
          <Stat label="STRUCTURE" value="DETECTABLE" detail="Recurring multi-scale levels can be identified deterministically." />
          <Stat label="V0 PREDICTION" value="NOT VALIDATED" detail="The tested reaction rule did not beat matched controls." />
          <Stat label="RESEARCH RULE" value="CONTROLS REQUIRED" detail="A pattern looking good by itself is not enough." />
          <Stat label="DATA PRESERVATION" value="NEEDS RAW SNAPSHOTS" detail="Old exchange minute history can disappear, so future tests must preserve replayable inputs." />
          <Stat label="STRATEGY" value="NOT YET" detail="A signal still needs entry, exit, costs, sizing and instrument choice before it has EV." />
        </div>
      </section>

      <details className="panel" style={{ marginTop: "1.2rem" }}>
        <summary style={{ cursor: "pointer", fontWeight: 800 }}>Project workflow / why the sections are separated</summary>
        <div className="row" style={{ gap: "0.45rem", flexWrap: "wrap", alignItems: "center", marginTop: "0.7rem" }}>
          <span className="tiny-pill">SEE MARKET</span><strong>→</strong>
          <span className="tiny-pill">TEST IDEA</span><strong>→</strong>
          <span className="tiny-pill">SAVE RESULT</span><strong>→</strong>
          <span className="tiny-pill">LEARN</span><strong>→</strong>
          <span className="tiny-pill">ONLY IF VALIDATED: STRATEGY / HUMMINGBOT</span>
        </div>
      </details>
    </AppShell>
  );
}
