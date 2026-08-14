import type { Metadata } from "next";
import { AppShell } from "@/components/AppShell";
import { MultiScaleStructureProbe } from "@/components/MultiScaleStructureProbe";
import { ProbeAutoRefresh } from "@/components/ProbeAutoRefresh";
import { operatingLoopProbe } from "@/data/operatingLoopProbe";
import { loadMarketStructureProbeState } from "@/lib/marketStructureProbe";
import { loadSignalCaptureProbeState } from "@/lib/signalCaptureProbe";

export const metadata: Metadata = { title: "Mission Control (Experimental) | Market Structure OS" };
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
      <header className="topline"><div><div className="crumb">Operator / Experimental</div><h1 className="title">Mission Control</h1></div><div className="tools"><ProbeAutoRefresh intervalMs={15000} /><span className="pill">Hybrid / read-only</span></div></header>

      <section className="panel compact">
        <div className="panel-sub">{probe.label}</div><h2 style={{ marginBottom: "0.35rem" }}>{probe.experiment}</h2>
        <p className="panel-sub">Observe real data, test structure across scales, keep interpretation manual.</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, minmax(0, 1fr))", gap: "0.5rem" }}>
          {probe.stages.map(stage => <div key={stage.id} className="panel compact" style={{ textAlign: "center" }}><div style={{ fontSize: "1.2rem" }}>{mark(stage.status)}</div><strong>{stage.label}</strong></div>)}
        </div>
      </section>

      <div style={{ display: "grid", gap: "1rem", marginTop: "1rem" }}>
        <Card eyebrow="OBSERVE · CONDOR READ-ONLY" title="Signal Capture" status={capture.status} detail={capture.detail}>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>{capture.sourceStates.map(source => <span key={source.source} className="tiny-pill">{source.source}: {source.files || "—"}</span>)}</div>
        </Card>

        <Card eyebrow="UNDERSTAND · LATEST WINDOW" title={probe.understand.title} status={ndaxReady ? probe.understand.status : "WAITING"} detail={probe.understand.detail}>
          {ndaxReady && <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(145px, 1fr))", gap: "0.5rem" }}>
            <div className="panel compact"><div className="panel-sub">NDAX observations</div><strong>{ndax.l1_observations ?? "—"}</strong></div>
            <div className="panel compact"><div className="panel-sub">15m range</div><strong>{fmt(ndax.range_pct, 3, "%")}</strong></div>
            <div className="panel compact"><div className="panel-sub">Median spread</div><strong>{fmt(ndax.median_spread_bps, 2, " bps")}</strong></div>
            <div className="panel compact"><div className="panel-sub">Max gap</div><strong>{fmt(ndax.max_gap_seconds, 1, "s")}</strong></div>
            <div className="panel compact"><div className="panel-sub">Jupiter</div><strong>{jupiterReady ? `${jupiter.quote_observations ?? "—"} quotes` : "waiting"}</strong></div>
          </div>}
        </Card>

        <MultiScaleStructureProbe payload={structure.payload} sourceStatus={structure.status} sourceDetail={structure.detail} />
        <Card eyebrow="DECIDE · MANUAL" {...probe.decide} />
        <Card eyebrow="EXECUTE · READ ONLY / NOT WIRED" {...probe.execute} />
        <Card eyebrow="LEARN · MANUAL" {...probe.learn} />
      </div>

      <section className="panel" style={{ marginTop: "1rem" }}><div className="panel-sub">NEXT ACTION</div><h2 style={{ marginBottom: "0.35rem" }}>{probe.nextAction}</h2><p className="panel-sub" style={{ marginBottom: 0 }}>The detector uses the same relative rule at 5m, 15m, 1h, 4h, and 1d. Mission Control refreshes every 15 seconds.</p></section>
    </AppShell>
  );
}
