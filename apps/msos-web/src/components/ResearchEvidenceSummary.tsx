type RetrospectiveEvidence = {
  label: string;
  market: string;
  sample: string;
  windows: number;
  usableRows: string;
  detectedReactionRate: number;
  controlReactionRate: number;
  delta: number;
  pass: number;
  fail: number;
  inconclusive: number;
  interpretation: string;
  witnessUrl: string;
  artifactUrl: string;
  artifactLabel: string;
  artifactSha256: string;
};

function pct(value: number): string {
  const sign = value > 0 ? "+" : "";
  return `${sign}${(value * 100).toFixed(1)}%`;
}

export function ResearchEvidenceSummary({
  status,
  headline,
  summary,
  whatWeKnow,
  whatWeDoNotKnow,
  nextAction,
  evidence,
}: {
  status: string;
  headline: string;
  summary: string;
  whatWeKnow: string;
  whatWeDoNotKnow: string;
  nextAction: string;
  evidence: RetrospectiveEvidence;
}) {
  return (
    <section className="panel">
      <div className="panel-sub">RESEARCH STATUS · WHAT HAVE WE ACTUALLY PROVEN?</div>
      <div className="row" style={{ alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
        <h2 style={{ margin: 0 }}>{headline}</h2>
        <span className="tiny-pill amber">{status}</span>
      </div>
      <p style={{ maxWidth: "900px", marginBottom: "1rem" }}>{summary}</p>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "0.75rem" }}>
        <div className="panel compact">
          <div className="panel-sub">WHAT WE KNOW</div>
          <strong>{whatWeKnow}</strong>
        </div>
        <div className="panel compact">
          <div className="panel-sub">WHAT WE DO NOT KNOW</div>
          <strong>{whatWeDoNotKnow}</strong>
        </div>
        <div className="panel compact">
          <div className="panel-sub">WHAT HAPPENS NEXT</div>
          <strong>{nextAction}</strong>
        </div>
      </div>

      <div className="panel compact" style={{ marginTop: "1rem" }}>
        <div className="row" style={{ alignItems: "center", justifyContent: "space-between", gap: "0.75rem", flexWrap: "wrap" }}>
          <div>
            <div className="panel-sub">FIRST HISTORICAL VALIDATION · {evidence.label}</div>
            <h3 style={{ margin: "0.2rem 0" }}>{evidence.market} · {evidence.sample}</h3>
            <div className="panel-sub">{evidence.windows} predeclared windows · {evidence.usableRows}</div>
          </div>
          <span className="tiny-pill amber">INCONCLUSIVE · NO EDGE SHOWN</span>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: "0.5rem", marginTop: "0.9rem" }}>
          <div className="panel compact">
            <div className="panel-sub">Detected levels reacted</div>
            <strong>{pct(evidence.detectedReactionRate)}</strong>
          </div>
          <div className="panel compact">
            <div className="panel-sub">Matched controls reacted</div>
            <strong>{pct(evidence.controlReactionRate)}</strong>
          </div>
          <div className="panel compact">
            <div className="panel-sub">Observed difference</div>
            <strong>{pct(evidence.delta)}</strong>
          </div>
          <div className="panel compact">
            <div className="panel-sub">Window verdicts</div>
            <strong>{evidence.pass} pass · {evidence.fail} fail · {evidence.inconclusive} inconclusive</strong>
          </div>
        </div>

        <p style={{ margin: "0.9rem 0 0.35rem" }}><strong>Plain English:</strong> {evidence.interpretation}</p>
        <p className="panel-sub" style={{ margin: 0 }}>
          Inconclusive does not mean “almost passed.” It means the frozen evidence rule did not see enough qualifying touches inside any one four-hour window to make a PASS/FAIL call.
        </p>

        <details style={{ marginTop: "0.9rem" }}>
          <summary style={{ cursor: "pointer", fontWeight: 700 }}>Evidence & reproducibility</summary>
          <div className="panel-sub" style={{ marginTop: "0.6rem" }}>
            The raw evidence package is the machine-readable lab notebook behind this summary. It contains the source provenance, frozen parameters, all windows, levels, controls, touches, reactions, and calculations. The ZIP is for audit/reproduction; teammates should not need it to understand the result.
          </div>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginTop: "0.65rem" }}>
            <a href={evidence.witnessUrl} target="_blank" rel="noreferrer">View GitHub witness</a>
            <a href={evidence.artifactUrl} target="_blank" rel="noreferrer">Raw evidence package ({evidence.artifactLabel})</a>
          </div>
          <div className="panel-sub" style={{ marginTop: "0.45rem", wordBreak: "break-all" }}>SHA-256 {evidence.artifactSha256}</div>
        </details>
      </div>
    </section>
  );
}
