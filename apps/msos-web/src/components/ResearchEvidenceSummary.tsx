type PrimaryEvidence = {
  label: string;
  market: string;
  sample: string;
  windows: number;
  usableRows: string;
  detectedTouched: number;
  detectedReacted: number;
  detectedReactionRate: number;
  controlTouched: number;
  controlReacted: number;
  controlReactionRate: number;
  delta: number;
  ciLower: number;
  ciUpper: number;
  verdict: string;
  interpretation: string;
  witnessUrl: string;
  artifactUrl: string;
  artifactLabel: string;
  artifactSha256: string;
};

type PriorEvidence = {
  label: string;
  result: string;
  detail: string;
};

function pct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function signedPp(value: number): string {
  const sign = value > 0 ? "+" : "";
  return `${sign}${(value * 100).toFixed(1)} pp`;
}

export function ResearchEvidenceSummary({
  status,
  headline,
  summary,
  whatWeKnow,
  whatWeDoNotKnow,
  nextAction,
  evidence,
  priorEvidence,
}: {
  status: string;
  headline: string;
  summary: string;
  whatWeKnow: string;
  whatWeDoNotKnow: string;
  nextAction: string;
  evidence: PrimaryEvidence;
  priorEvidence: readonly PriorEvidence[];
}) {
  return (
    <section className="panel">
      <div className="panel-sub">RESEARCH DECISION · WHAT DID V0 ACTUALLY TEACH US?</div>
      <div className="row" style={{ alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
        <h2 style={{ margin: 0 }}>{headline}</h2>
        <span className="tiny-pill amber">{status}</span>
      </div>
      <p style={{ maxWidth: "920px", marginBottom: "1rem", fontSize: "1.02rem" }}>{summary}</p>

      <div className="panel compact" style={{ marginBottom: "1rem" }}>
        <div className="panel-sub">DECISION</div>
        <h3 style={{ margin: "0.25rem 0" }}>Do not promote v0 to Hummingbot.</h3>
        <p style={{ margin: 0 }}>
          We finally collected enough touches to run the batch test. Our detected levels did not beat the matched controls. “Inconclusive” means we cannot prove the true effect is negative; it does <strong>not</strong> mean v0 has shown an edge.
        </p>
      </div>

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
            <div className="panel-sub">PRIMARY EVIDENCE · {evidence.label}</div>
            <h3 style={{ margin: "0.2rem 0" }}>{evidence.market} · {evidence.sample}</h3>
            <div className="panel-sub">{evidence.windows} predeclared 4h windows · {evidence.usableRows}</div>
          </div>
          <span className="tiny-pill amber">{evidence.verdict} · NO EDGE DEMONSTRATED</span>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(165px, 1fr))", gap: "0.5rem", marginTop: "0.9rem" }}>
          <div className="panel compact">
            <div className="panel-sub">Our detected levels</div>
            <strong>{evidence.detectedReacted} / {evidence.detectedTouched} reacted</strong>
            <div className="panel-sub">{pct(evidence.detectedReactionRate)} after touch</div>
          </div>
          <div className="panel compact">
            <div className="panel-sub">Matched control levels</div>
            <strong>{evidence.controlReacted} / {evidence.controlTouched} reacted</strong>
            <div className="panel-sub">{pct(evidence.controlReactionRate)} after touch</div>
          </div>
          <div className="panel compact">
            <div className="panel-sub">Observed difference</div>
            <strong>{signedPp(evidence.delta)}</strong>
            <div className="panel-sub">detector minus control</div>
          </div>
          <div className="panel compact">
            <div className="panel-sub">Plausible range (95%)</div>
            <strong>{signedPp(evidence.ciLower)} to {signedPp(evidence.ciUpper)}</strong>
            <div className="panel-sub">crosses zero → formal verdict stays inconclusive</div>
          </div>
        </div>

        <p style={{ margin: "0.9rem 0 0.35rem" }}><strong>Plain English:</strong> {evidence.interpretation}</p>
        <p className="panel-sub" style={{ margin: 0 }}>
          The important product decision is simpler than the statistical label: v0 has not earned the next stage. We preserve it as a completed negative/neutral research result instead of tuning it until it looks good.
        </p>

        <details style={{ marginTop: "0.9rem" }}>
          <summary style={{ cursor: "pointer", fontWeight: 700 }}>Evidence & reproducibility</summary>
          <div className="panel-sub" style={{ marginTop: "0.6rem" }}>
            The raw evidence package is the machine-readable lab notebook behind this summary. It contains source provenance, frozen parameters, all 168 windows, detected/control levels, touches, reactions, and bootstrap calculations. The ZIP is for audit/reproduction; teammates should not need it to understand the conclusion.
          </div>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginTop: "0.65rem" }}>
            <a href={evidence.witnessUrl} target="_blank" rel="noreferrer">View research witness</a>
            <a href={evidence.artifactUrl} target="_blank" rel="noreferrer">Raw evidence package ({evidence.artifactLabel})</a>
          </div>
          <div className="panel-sub" style={{ marginTop: "0.45rem", wordBreak: "break-all" }}>SHA-256 {evidence.artifactSha256}</div>
        </details>
      </div>

      <details style={{ marginTop: "1rem" }}>
        <summary style={{ cursor: "pointer", fontWeight: 700 }}>How we got here · earlier evidence</summary>
        <div style={{ display: "grid", gap: "0.5rem", marginTop: "0.65rem" }}>
          {priorEvidence.map((item) => (
            <div key={item.label} className="panel compact">
              <div className="row" style={{ alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
                <strong>{item.label}</strong>
                <span className="tiny-pill amber">{item.result}</span>
              </div>
              <div className="panel-sub" style={{ marginTop: "0.35rem" }}>{item.detail}</div>
            </div>
          ))}
        </div>
      </details>
    </section>
  );
}
