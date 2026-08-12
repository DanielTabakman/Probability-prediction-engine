import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { operatingLoopProbe } from "@/data/operatingLoopProbe";
import { loadSignalCaptureProbeState } from "@/lib/signalCaptureProbe";

export const metadata: Metadata = {
  title: "Mission Control (Experimental) | Market Structure OS",
  description: "Read-only operating-loop probe for MSOS operator workflow testing.",
};

export const dynamic = "force-dynamic";

function stageMark(status: "active" | "pending") {
  return status === "active" ? "●" : "○";
}

function ProbeCard({
  eyebrow,
  title,
  status,
  detail,
  children,
}: {
  eyebrow: string;
  title: string;
  status: string;
  detail: string;
  children?: React.ReactNode;
}) {
  return (
    <section className="panel compact">
      <div className="panel-sub">{eyebrow}</div>
      <div className="row" style={{ alignItems: "center", gap: "0.75rem" }}>
        <h2 style={{ margin: 0 }}>{title}</h2>
        <span className="tag muted">{status}</span>
      </div>
      <p style={{ marginBottom: children ? "0.75rem" : 0 }}>{detail}</p>
      {children}
    </section>
  );
}

export default async function MissionControlPage() {
  const probe = operatingLoopProbe;
  const capture = await loadSignalCaptureProbeState();

  return (
    <AppShell activeNavId="mission-control">
      <header className="topline">
        <div>
          <div className="crumb">Operator / Experimental</div>
          <h1 className="title">Mission Control</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot amber" aria-hidden="true" />
            Hybrid probe / read-only
          </span>
        </div>
      </header>

      <section className="panel compact" aria-label="Operating loop probe">
        <div className="panel-sub">{probe.label}</div>
        <h2 style={{ marginBottom: "0.35rem" }}>{probe.experiment}</h2>
        <p className="panel-sub" style={{ marginTop: 0 }}>
          Deliberately janky. Observe is now wired to real capture-file activity; the middle of the loop remains manual while we test the structure.
        </p>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(5, minmax(0, 1fr))",
            gap: "0.5rem",
            marginTop: "1rem",
          }}
        >
          {probe.stages.map((stage) => (
            <div key={stage.id} className="panel compact" style={{ textAlign: "center" }}>
              <div aria-hidden="true" style={{ fontSize: "1.25rem" }}>
                {stageMark(stage.status)}
              </div>
              <strong>{stage.label}</strong>
            </div>
          ))}
        </div>
      </section>

      <div style={{ display: "grid", gap: "1rem", marginTop: "1rem" }}>
        <ProbeCard eyebrow="OBSERVE · REAL READ-ONLY" title="Signal Capture" status={capture.status} detail={capture.detail}>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
            {capture.sourceStates.map((source) => (
              <span key={source.source} className="tiny-pill">
                {source.source}: {source.files > 0 ? `${source.files} file${source.files === 1 ? "" : "s"}` : "—"}
              </span>
            ))}
          </div>
        </ProbeCard>
        <ProbeCard eyebrow="UNDERSTAND · MANUAL" {...probe.understand} />
        <ProbeCard eyebrow="DECIDE · MANUAL" {...probe.decide} />
        <ProbeCard eyebrow="EXECUTE · READ ONLY / NOT WIRED" {...probe.execute} />
        <ProbeCard eyebrow="LEARN · MANUAL" {...probe.learn} />
      </div>

      <section className="panel" style={{ marginTop: "1rem" }}>
        <div className="panel-sub">NEXT ACTION</div>
        <h2 style={{ marginBottom: "0.35rem" }}>
          {capture.status === "NOT CONNECTED"
            ? "Point MSOS at the oct-signal-capture data directory."
            : capture.status === "EMPTY"
              ? "Start live signal capture from the normal Ubuntu/WSL shell."
              : capture.status === "LIVE"
                ? "Observe the live feed, then record the first research conclusion."
                : "Restart or inspect signal capture; the newest output is stale."}
        </h2>
        <p className="panel-sub" style={{ marginBottom: 0 }}>
          Set <code>OCT_SIGNAL_CAPTURE_DATA_DIR</code> in the MSOS process environment. This page only reads file names and modification times; it does not read .env files, credentials, or place trades.
        </p>
      </section>

      <section className="panel compact" style={{ marginTop: "1rem" }}>
        <div className="panel-sub">PROBE SUCCESS QUESTION</div>
        <p style={{ marginBottom: 0 }}>{probe.successQuestion}</p>
      </section>
    </AppShell>
  );
}
