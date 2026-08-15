import type { Metadata } from "next";
import { AppShell } from "@/components/AppShell";
import { MultiScaleStructureProbe } from "@/components/MultiScaleStructureProbe";
import { ProbeAutoRefresh } from "@/components/ProbeAutoRefresh";
import { ResearchExperimentPanel } from "@/components/ResearchExperimentPanel";
import { operatingLoopProbe } from "@/data/operatingLoopProbe";
import { loadMarketStructureProbeState } from "@/lib/marketStructureProbe";
import { loadSignalCaptureProbeState } from "@/lib/signalCaptureProbe";

export const metadata: Metadata = { title: "Market Structure Lab | Market Structure OS" };
export const dynamic = "force-dynamic";

function fmt(value: number | null | undefined, digits = 2, suffix = "") {
  return typeof value === "number" && Number.isFinite(value) ? `${value.toFixed(digits)}${suffix}` : "—";
}
function mark(status: "active" | "pending") { return status === "active" ? "●" : "○"; }
function Card({ eyebrow, title, status, detail, children }: { eyebrow: string; title: string; status: string; detail: string; children?: React.ReactNode }) {
  return <section className="panel compact"><div className="panel-sub">{eyebrow}</div><div className="row" style={{ alignItems: "center", gap: "0.75rem" }}><h2 style={{ margin: 0 }}>{title}</h2><span className="tag muted">{status}</span></div><p style={{ marginBottom: children ? "0.75rem" : 0 }}>{detail}</p>{children}</section>;
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
      <header className="topline"><div><div className="crumb">Research / Team Console v0</div><h1 className="title">Market Structure Lab</h1></div><div className="tools"><ProbeAutoRefresh intervalMs={15000} /><span className="pill">Research only · no execution</span></div></header>

      <section className="panel compact">
        <div className="panel-sub">PURPOSE</div>
        <h2 style={{ marginBottom: "0.35rem" }}>Find market structure that contains useful information about future price behavior.</h2>
        <p className="panel-sub" style={{ marginBottom: "0.75rem" }}><strong>Current question:</strong> {probe.successQuestion}</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, minmax(0, 1fr))", gap: "0.5rem" }}>
          {probe.stages.map(stage => <div key={stage.id} className="panel compact" style={{ textAlign: "center" }}><div style={{ fontSize: "1.2rem" }}>{mark(stage.status)}</div><strong>{stage.label}</strong></div>)}
        </div>
      </section>

      <div style={{ display: "grid", gap: "1rem", marginTop: "1rem" }}>
        <Card eyebrow="1 · DATA" title="Market observations" status={capture.status} detail={capture.detail}>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>{capture.sourceStates.map(source => <span key={source.source} className="tiny-pill">{source.source}: {source.files || "—"}</span>)}</div>
          {ndaxReady && <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(145px, 1fr))", gap: "0.5rem", marginTop: "0.75rem" }}>
            <div className="panel compact"><div className="panel-sub">NDAX observations</div><strong>{ndax.l1_observations ?? "—"}</strong></div>
            <div className="panel compact"><div className="panel-sub">15m range</div><strong>{fmt(ndax.range_pct, 3, "%")}</strong></div>
            <div className="panel compact"><div className="panel-sub">Median spread</div><strong>{fmt(ndax.median_spread_bps, 2, " bps")}</strong></div>
            <div className="panel compact"><div className="panel-sub">Max gap</div><strong>{fmt(ndax.max_gap_seconds, 1, "s")}</strong></div>
            <div className="panel compact"><div className="panel-sub">Jupiter</div><strong>{jupiterReady ? `${jupiter.quote_observations ?? "—"} quotes` : "waiting"}</strong></div>
          </div>}
        </Card>

        <MultiScaleStructureProbe payload={structure.payload} sourceStatus={structure.status} sourceDetail={structure.detail} />
        <ResearchExperimentPanel />
        <Card eyebrow="4 · STRATEGY · LATER" {...probe.decide} />
        <Card eyebrow="5 · HUMMINGBOT · LATER" {...probe.execute} />
        <Card eyebrow="6 · LEARN" {...probe.learn} />
      </div>

      <section className="panel" style={{ marginTop: "1rem" }}><div className="panel-sub">NEXT ACTION</div><h2 style={{ marginBottom: "0.35rem" }}>{probe.nextAction}</h2><p className="panel-sub" style={{ marginBottom: 0 }}>Keep v0 narrow: fresh observations → frozen levels → matched baseline → saved result. Expand only after the team has used this loop.</p></section>
    </AppShell>
  );
}
