import type { Metadata } from "next";
import { AppShell } from "@/components/AppShell";
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
function mark(status: "done" | "blocked") { return status === "done" ? "✓" : "×"; }
function Card({ eyebrow, title, status, detail, children }: { eyebrow: string; title: string; status: string; detail: string; children?: React.ReactNode }) {
  return <section className="panel compact"><div className="panel-sub">{eyebrow}</div><div className="row" style={{ alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}><h2 style={{ margin: 0 }}>{title}</h2><span className="tag muted">{status}</span></div><p style={{ marginBottom: children ? "0.75rem" : 0 }}>{detail}</p>{children}</section>;
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
          <div className="crumb">Research / Team Console</div>
          <h1 className="title">Market Structure Lab</h1>
        </div>
        <div className="tools"><ProbeAutoRefresh intervalMs={15000} /><span className="pill">Research only · no trading</span></div>
      </header>

      <section className="panel compact">
        <div className="panel-sub">WHAT ARE WE BUILDING?</div>
        <h2 style={{ marginBottom: "0.35rem" }}>A research lab that tests market ideas before they become Hummingbot strategies.</h2>
        <p style={{ marginBottom: "0.35rem" }}>
          V0 asked one narrow question: do recurring multi-scale price levels predict future reactions better than matched control levels? We built the detector, ran historical and prospective tests, and now have a complete v0 research decision.
        </p>
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

      <div style={{ display: "grid", gap: "1rem", marginTop: "1rem" }}>
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
      </div>

      <section className="panel" style={{ marginTop: "1rem" }}>
        <div className="panel-sub">NEXT RESEARCH DECISION</div>
        <h2 style={{ marginBottom: "0.35rem" }}>{probe.nextAction}</h2>
        <p className="panel-sub" style={{ marginBottom: 0 }}>
          V0 stays preserved exactly as tested. A future v1 can ask a different question, but it should be written down before inspecting its evaluation sample.
        </p>
      </section>
    </AppShell>
  );
}
