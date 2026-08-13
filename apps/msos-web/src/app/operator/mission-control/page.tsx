import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { ProbeAutoRefresh } from "@/components/ProbeAutoRefresh";
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

function fmt(value: number | null | undefined, digits = 2, suffix = "") {
  return typeof value === "number" && Number.isFinite(value) ? `${value.toFixed(digits)}${suffix}` : "—";
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
  const ndax = capture.ndax15m;
  const ndaxEvidenceReady = ndax?.status === "OK";
  const observeEyebrow =
    capture.origin === "https"
      ? "OBSERVE · CONDOR READ-ONLY"
      : capture.origin === "vm"
        ? "OBSERVE · VM READ-ONLY"
        : "OBSERVE · REAL READ-ONLY";

  return (
    <AppShell activeNavId="mission-control">
      <header className="topline">
        <div>
          <div className="crumb">Operator / Experimental</div>
          <h1 className="title">Mission Control</h1>
        </div>
        <div className="tools">
          <ProbeAutoRefresh intervalMs={15000} />
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
          Deliberately janky. Observe is wired to real capture activity; objective NDAX evidence is computed automatically, while interpretation and decisions remain manual.
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
        <ProbeCard eyebrow={observeEyebrow} title="Signal Capture" status={capture.status} detail={capture.detail}>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
            {capture.sourceStates.map((source) => (
              <span key={source.source} className="tiny-pill">
                {source.source}: {source.files > 0 ? `${source.files} file${source.files === 1 ? "" : "s"}` : "—"}
              </span>
            ))}
          </div>
        </ProbeCard>

        <ProbeCard
          eyebrow="UNDERSTAND · EVIDENCE AUTO / CONCLUSION MANUAL"
          title={probe.understand.title}
          status={ndaxEvidenceReady ? probe.understand.status : "WAITING FOR EVIDENCE"}
          detail={probe.understand.detail}
        >
          {ndaxEvidenceReady ? (
            <>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(145px, 1fr))",
                  gap: "0.5rem",
                }}
              >
                <div className="panel compact">
                  <div className="panel-sub">L1 observations</div>
                  <strong>{ndax.l1_observations ?? "—"}</strong>
                </div>
                <div className="panel compact">
                  <div className="panel-sub">Coverage</div>
                  <strong>{fmt((ndax.coverage_seconds ?? 0) / 60, 1, " min")}</strong>
                </div>
                <div className="panel compact">
                  <div className="panel-sub">Freshness</div>
                  <strong>{fmt(ndax.freshness_seconds, 1, "s")}</strong>
                </div>
                <div className="panel compact">
                  <div className="panel-sub">L1 rate</div>
                  <strong>{fmt(ndax.event_rate_hz, 2, " Hz")}</strong>
                </div>
                <div className="panel compact">
                  <div className="panel-sub">Mid CAD</div>
                  <strong>
                    {fmt(ndax.first_mid_cad, 3)} → {fmt(ndax.last_mid_cad, 3)}
                  </strong>
                </div>
                <div className="panel compact">
                  <div className="panel-sub">15m move</div>
                  <strong>{fmt(ndax.move_pct, 3, "%")}</strong>
                </div>
                <div className="panel compact">
                  <div className="panel-sub">15m range</div>
                  <strong>{fmt(ndax.range_pct, 3, "%")}</strong>
                </div>
                <div className="panel compact">
                  <div className="panel-sub">Median spread</div>
                  <strong>{fmt(ndax.median_spread_bps, 2, " bps")}</strong>
                </div>
                <div className="panel compact">
                  <div className="panel-sub">P95 spread</div>
                  <strong>{fmt(ndax.p95_spread_bps, 2, " bps")}</strong>
                </div>
                <div className="panel compact">
                  <div className="panel-sub">Max L1 gap</div>
                  <strong>{fmt(ndax.max_gap_seconds, 2, "s")}</strong>
                </div>
              </div>
              <p className="panel-sub" style={{ marginBottom: 0, marginTop: "0.75rem" }}>
                Derived from normalized NDAX Level 1 index rows over the latest 15-minute window. Evidence only; no trade signal or strategy conclusion is generated automatically.
              </p>
            </>
          ) : (
            <p className="panel-sub" style={{ marginBottom: 0 }}>
              {ndax?.status === "ERROR"
                ? "NDAX analysis is temporarily unavailable; capture status remains independent."
                : "Waiting for enough normalized NDAX Level 1 observations to summarize the latest 15-minute window."}
            </p>
          )}
        </ProbeCard>

        <ProbeCard eyebrow="DECIDE · MANUAL" {...probe.decide} />
        <ProbeCard eyebrow="EXECUTE · READ ONLY / NOT WIRED" {...probe.execute} />
        <ProbeCard eyebrow="LEARN · MANUAL" {...probe.learn} />
      </div>

      <section className="panel" style={{ marginTop: "1rem" }}>
        <div className="panel-sub">NEXT ACTION</div>
        <h2 style={{ marginBottom: "0.35rem" }}>
          {capture.status === "NOT CONNECTED"
            ? capture.origin === "https"
              ? "Restore the token-protected Condor status endpoint."
              : capture.origin === "vm"
                ? "Restore the read-only SSH status connection to the capture VM."
                : "Point MSOS at the shared, VM, or local oct-signal-capture status."
            : capture.status === "STOPPED"
              ? "Start the persistent oct-signal-capture service on the VM."
              : capture.status === "EMPTY"
                ? "Let persistent capture collect its first live observations."
                : capture.status === "LIVE" && ndaxEvidenceReady
                  ? probe.nextAction
                  : capture.status === "LIVE"
                    ? "Let the NDAX evidence window populate, then interpret it."
                    : "Inspect persistent signal capture; the newest output is stale."}
        </h2>
        <p className="panel-sub" style={{ marginBottom: 0 }}>
          Shared staging prefers the token-protected HTTPS status endpoint. SSH and local filesystem modes remain development fallbacks. Mission Control refreshes this read-only status automatically every 15 seconds.
        </p>
      </section>

      <section className="panel compact" style={{ marginTop: "1rem" }}>
        <div className="panel-sub">PROBE SUCCESS QUESTION</div>
        <p style={{ marginBottom: 0 }}>{probe.successQuestion}</p>
      </section>
    </AppShell>
  );
}
