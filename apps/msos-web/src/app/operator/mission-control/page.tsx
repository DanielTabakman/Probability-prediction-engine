import type { Metadata } from "next";
import { AppShell } from "@/components/AppShell";
import { ActiveExperimentStatus } from "@/components/ActiveExperimentStatus";
import { MarketStructureSandbox } from "@/components/MarketStructureSandbox";
import { MultiScaleStructureProbe } from "@/components/MultiScaleStructureProbe";
import { ProbeAutoRefresh } from "@/components/ProbeAutoRefresh";
import { ResearchEvidenceSummary } from "@/components/ResearchEvidenceSummary";
import { ResearchExperimentPanel } from "@/components/ResearchExperimentPanel";
import { operatingLoopProbe } from "@/data/operatingLoopProbe";
import { loadMarketStructureProbeState } from "@/lib/marketStructureProbe";
import { loadSignalCaptureProbeState } from "@/lib/signalCaptureProbe";

export const metadata: Metadata = { title: "Market Structure Workstation | Market Structure OS" };
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

function SectionIntro({ eyebrow, title, detail }: { eyebrow: string; title: string; detail: string }) {
  return (
    <div className="panel" style={{ marginBottom: "0.65rem" }}>
      <div className="panel-sub">{eyebrow}</div>
      <h2 style={{ margin: "0.15rem 0 0.3rem" }}>{title}</h2>
      <p className="panel-sub" style={{ margin: 0, maxWidth: "880px" }}>{detail}</p>
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
          <div className="crumb">Market Structure / Workstation</div>
          <h1 className="title">Market Structure Workstation</h1>
          <p className="panel-sub" style={{ margin: "0.25rem 0 0", maxWidth: "760px" }}>
            One place to watch the market, see the active experiment, explore new hypotheses, and review the evidence trail.
          </p>
        </div>
        <div className="tools">
          <ProbeAutoRefresh intervalMs={15000} />
          <span className="pill">Research only · no trading</span>
        </div>
      </header>

      <nav
        className="panel compact"
        aria-label="Market Structure workstation sections"
        style={{ position: "sticky", top: "0.5rem", zIndex: 20, backdropFilter: "blur(10px)" }}
      >
        <div className="row" style={{ gap: "0.45rem", flexWrap: "wrap" }}>
          <a className="btn" href="#desk">Desk</a>
          <a className="btn" href="#live">Live market</a>
          <a className="btn" href="#experiments">Experiments</a>
          <a className="btn" href="#sandbox">Sandbox</a>
          <a className="btn" href="#infrastructure">Infrastructure</a>
          <a className="btn" href="#evidence">Evidence</a>
        </div>
      </nav>

      <section id="desk" style={{ marginTop: "0.9rem" }}>
        <SectionIntro
          eyebrow="DESK · WHAT MATTERS NOW"
          title="Current mission: collect clean forward evidence."
          detail="EXP-001A is the active job. The detector is frozen; the workstation should help you observe the run and generate future hypotheses without quietly changing the test that is already underway."
        />

        <ActiveExperimentStatus />

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))", gap: "0.55rem", marginTop: "0.65rem" }}>
          <Stat label="MARKET DATA" value={capture.status} detail={capture.detail} />
          <Stat label="STRUCTURE ENGINE" value={structure.status} detail={structure.detail} />
          <Stat label="LAST FINISHED HYPOTHESIS" value="V0 · NO EDGE" detail="16.67% detector reactions vs 18.98% matched controls." />
          <Stat label="NEXT DECISION" value="EVIDENCE FIRST" detail="Do not promote to strategy until prospective results justify it." />
        </div>

        <div className="panel compact" style={{ marginTop: "0.65rem" }}>
          <div className="panel-sub">WORKFLOW</div>
          <div className="row" style={{ gap: "0.45rem", flexWrap: "wrap", alignItems: "center", marginTop: "0.55rem" }}>
            <span className="tiny-pill">1 · OBSERVE</span><strong>→</strong>
            <span className="tiny-pill">2 · TEST</span><strong>→</strong>
            <span className="tiny-pill">3 · COMPARE TO CONTROL</span><strong>→</strong>
            <span className="tiny-pill">4 · SAVE RESULT</span><strong>→</strong>
            <span className="tiny-pill">5 · ONLY THEN BUILD STRATEGY</span>
          </div>
        </div>
      </section>

      <section id="live" style={{ marginTop: "1.2rem", scrollMarginTop: "5rem" }}>
        <SectionIntro
          eyebrow="LIVE MARKET"
          title="What does the engine see right now?"
          detail="Live detector output and feed condition. This is observation, not validation: a level appearing here does not mean it predicts anything."
        />

        <MultiScaleStructureProbe payload={structure.payload} sourceStatus={structure.status} sourceDetail={structure.detail} />

        <details className="panel" style={{ marginTop: "0.65rem" }}>
          <summary style={{ cursor: "pointer", fontWeight: 800 }}>Feed diagnostics</summary>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(155px, 1fr))", gap: "0.5rem", marginTop: "0.65rem" }}>
            <Stat label="NDAX OBSERVATIONS" value={String(ndax?.l1_observations ?? "—")} />
            <Stat label="15M RANGE" value={fmt(ndax?.range_pct, 3, "%")} />
            <Stat label="TYPICAL SPREAD" value={fmt(ndax?.median_spread_bps, 2, " bps")} />
            <Stat label="LARGEST GAP" value={fmt(ndax?.max_gap_seconds, 1, "s")} />
            <Stat label="JUPITER QUOTES" value={String(jupiter?.quote_observations ?? "—")} />
          </div>
        </details>
      </section>

      <section id="experiments" style={{ marginTop: "1.2rem", scrollMarginTop: "5rem" }}>
        <SectionIntro
          eyebrow="EXPERIMENTS"
          title="What is running, finished, or blocked?"
          detail="The active test stays separate from finished tests. Nulls and failures remain visible so we do not accidentally retell the project as a string of wins."
        />

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))", gap: "0.55rem", marginBottom: "0.65rem" }}>
          <Stat label="EXP-001A" value="RUNNING" detail="Prospective frozen-zone validation; snapshots every 15 minutes." />
          <Stat label="V0 HISTORICAL" value="STOPPED" detail="No edge demonstrated against matched controls." />
          <Stat label="V1 CANDIDATE" value="NOT FROZEN" detail="Use the sandbox to explore; a promising rule becomes a new written experiment." />
          <Stat label="STRATEGY / HUMMINGBOT" value="BLOCKED" detail="Requires validated predictive evidence first." />
        </div>

        <ResearchExperimentPanel />
      </section>

      <section id="sandbox" style={{ marginTop: "1.2rem", scrollMarginTop: "5rem" }}>
        <SectionIntro
          eyebrow="SANDBOX · EXPLORATION"
          title="Turn the dials and see what changes."
          detail="This is the hands-on workbench. Change persistence, timeframe membership, level type, thresholds and replay definitions. Sandbox results generate candidate hypotheses; they do not rewrite V0 or EXP-001A."
        />
        <div className="row" style={{ gap: "0.5rem", flexWrap: "wrap", marginBottom: "0.65rem" }}>
          <span className="tiny-pill">SAFE TO EXPLORE</span>
          <span className="tiny-pill">DOES NOT MUTATE ACTIVE TEST</span>
          <span className="tiny-pill">PROMISING RULE → FREEZE NEW EXPERIMENT</span>
        </div>
        <MarketStructureSandbox />
      </section>

      <section id="infrastructure" style={{ marginTop: "1.2rem", scrollMarginTop: "5rem" }}>
        <SectionIntro
          eyebrow="INFRASTRUCTURE"
          title="Is the machinery healthy?"
          detail="Operational plumbing lives here instead of dominating the research view. Open the details only when something is broken or you need provenance."
        />
        <details className="panel">
          <summary style={{ cursor: "pointer", fontWeight: 800 }}>System health and ownership</summary>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0.55rem", marginTop: "0.65rem" }}>
            <Stat label="SIGNAL CAPTURE" value={capture.status} detail={capture.detail} />
            <Stat label="MARKET-STRUCTURE ENGINE" value={structure.status} detail={structure.detail} />
            <Stat label="EXP-001A RECORDER" value="DEPLOYED" detail="Condor runtime witness passed; capture mount remains read-only." />
            <Stat label="FROZEN V0 REPLAY" value="AVAILABLE" detail="Saved V0 evidence powers the instant sandbox lens." />
            <Stat label="RAW PATH REPLAY" value="STAGING WORK" detail="Keep separate from the frozen V0 evidence when current raw history is incomplete." />
            <Stat label="HUMMINGBOT" value="DOWNSTREAM" detail="Commodity strategy/execution infrastructure only after research validation." />
            <Stat label="LIVE TRADING" value="OFF" detail="No trading authority added." />
          </div>
        </details>
      </section>

      <section id="evidence" style={{ marginTop: "1.2rem", scrollMarginTop: "5rem" }}>
        <SectionIntro
          eyebrow="EVIDENCE & HISTORY"
          title="What have we actually learned?"
          detail="The archive keeps finished tests, durable findings, and audit details accessible without making them the first thing you have to look at every time you open the workstation."
        />

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))", gap: "0.55rem" }}>
          <Stat label="FEED QUALITY" value="SCALE-DEPENDENT" detail="Market-data usefulness changes by horizon; do not label an entire venue simply good or bad." />
          <Stat label="STRUCTURE" value="DETECTABLE" detail="Recurring multi-scale levels can be identified deterministically." />
          <Stat label="V0 PREDICTION" value="NOT VALIDATED" detail="The tested reaction rule did not beat matched controls." />
          <Stat label="RESEARCH RULE" value="CONTROLS REQUIRED" detail="Visual plausibility is not enough; every claim needs a baseline." />
          <Stat label="DATA PRESERVATION" value="IMPORTANT" detail="Replayable input history matters because exchange history can disappear or change." />
          <Stat label="STRATEGY" value="NOT YET" detail="Signal, entry, exit, costs, sizing and instrument choice remain separate questions." />
        </div>

        <details className="panel" style={{ marginTop: "0.65rem" }}>
          <summary style={{ cursor: "pointer", fontWeight: 800 }}>Primary V0 result</summary>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(155px, 1fr))", gap: "0.5rem", marginTop: "0.65rem" }}>
            <Stat label="DETECTOR" value="24 / 144" detail="16.67% reacted" />
            <Stat label="MATCHED CONTROL" value="26 / 137" detail="18.98% reacted" />
            <Stat label="DIFFERENCE" value="−2.31 pp" detail="detector minus control" />
            <Stat label="DECISION" value="STOP V0" detail="Do not advance this hypothesis to Hummingbot." />
          </div>
        </details>

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
    </AppShell>
  );
}
