export function HeroSection() {
  return (
    <section>
      <div className="eyebrow">A coherent interface for uncertainty</div>
      <h1>Market Structure OS for legible market theses.</h1>
      <p>
        Market Structure OS is the company and software platform. The Strategy Lab is where users
        design, test and monitor thesis-driven strategies. PPE is the first tool inside the lab — a
        probability/thesis engine that compares what markets imply with what a human believes.
      </p>
      <div className="hero-actions">
        <span className="btn primary">
          Explore the platform <span aria-hidden="true">→</span>
        </span>
        <span className="btn">Enter Command Center</span>
      </div>
      <div className="chips">
        <span className="pill">
          <span className="dot" />
          Human-owned theses
        </span>
        <span className="pill">
          <span className="dot amber" />
          Fit, not recommendation
        </span>
        <span className="pill">Preview includes BTC options through PPE</span>
      </div>
      <div className="semantic-lock">
        <div className="lock">
          <h3>MSOS</h3>
          <p>Company and platform identity.</p>
        </div>
        <div className="lock">
          <h3>Strategy Lab</h3>
          <p>Workspace for designing thesis-driven market strategies.</p>
        </div>
        <div className="lock">
          <h3>PPE</h3>
          <p>First tool: probability/thesis comparison engine.</p>
        </div>
      </div>
      <div className="lens-row" aria-label="Market lens availability">
        <span className="tag">BTC options (PPE) — Preview</span>
        <span className="tag muted">Prediction markets — Planned</span>
        <span className="tag muted">Perpetual positioning — Planned</span>
      </div>
    </section>
  );
}
