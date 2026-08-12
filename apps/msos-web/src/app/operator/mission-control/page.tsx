import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { operatingLoopProbe } from "@/data/operatingLoopProbe";

export const metadata: Metadata = {
  title: "Mission Control (Experimental) | Market Structure OS",
  description: "Fixture-backed operating-loop probe for MSOS operator workflow testing.",
};

function stageMark(status: "active" | "pending") {
  return status === "active" ? "●" : "○";
}

function ProbeCard({
  eyebrow,
  title,
  status,
  detail,
}: {
  eyebrow: string;
  title: string;
  status: string;
  detail: string;
}) {
  return (
    <section className="panel compact">
      <div className="panel-sub">{eyebrow}</div>
      <div className="row" style={{ alignItems: "center", gap: "0.75rem" }}>
        <h2 style={{ margin: 0 }}>{title}</h2>
        <span className="tag muted">{status}</span>
      </div>
      <p style={{ marginBottom: 0 }}>{detail}</p>
    </section>
  );
}

export default function MissionControlPage() {
  const probe = operatingLoopProbe;

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
            {probe.mode}
          </span>
        </div>
      </header>

      <section className="panel compact" aria-label="Operating loop probe">
        <div className="panel-sub">{probe.label}</div>
        <h2 style={{ marginBottom: "0.35rem" }}>{probe.experiment}</h2>
        <p className="panel-sub" style={{ marginTop: 0 }}>
          Deliberately janky. The goal is to test whether this structure is useful before MSOS is redesigned around it.
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
        <ProbeCard eyebrow="OBSERVE" {...probe.observe} />
        <ProbeCard eyebrow="UNDERSTAND" {...probe.understand} />
        <ProbeCard eyebrow="DECIDE" {...probe.decide} />
        <ProbeCard eyebrow="EXECUTE" {...probe.execute} />
        <ProbeCard eyebrow="LEARN" {...probe.learn} />
      </div>

      <section className="panel" style={{ marginTop: "1rem" }}>
        <div className="panel-sub">NEXT ACTION</div>
        <h2 style={{ marginBottom: "0.35rem" }}>{probe.nextAction}</h2>
        <p className="panel-sub" style={{ marginBottom: 0 }}>
          No action on this page can place a trade. We are testing the workflow representation first.
        </p>
      </section>

      <section className="panel compact" style={{ marginTop: "1rem" }}>
        <div className="panel-sub">PROBE SUCCESS QUESTION</div>
        <p style={{ marginBottom: 0 }}>{probe.successQuestion}</p>
      </section>
    </AppShell>
  );
}
