type StatusTone = "working" | "active" | "blocked" | "future" | "warning";

type Stage = {
  number: number;
  title: string;
  status: string;
  tone: StatusTone;
  purpose: string;
  href: string;
};

function toneMark(tone: StatusTone) {
  if (tone === "working") return "✓";
  if (tone === "active") return "●";
  if (tone === "warning") return "!";
  if (tone === "blocked") return "×";
  return "○";
}

function StageCard({ stage }: { stage: Stage }) {
  return (
    <a
      href={stage.href}
      className="panel compact"
      style={{ textDecoration: "none", color: "inherit", display: "block", minHeight: "155px" }}
    >
      <div className="panel-sub">STAGE {stage.number}</div>
      <div className="row" style={{ gap: "0.55rem", alignItems: "center", marginTop: "0.25rem" }}>
        <strong style={{ fontSize: "1.25rem" }}>{toneMark(stage.tone)}</strong>
        <strong>{stage.title}</strong>
      </div>
      <div className="tiny-pill" style={{ display: "inline-block", marginTop: "0.55rem" }}>{stage.status}</div>
      <div className="panel-sub" style={{ marginTop: "0.55rem" }}>{stage.purpose}</div>
    </a>
  );
}

export function MarketStructureProjectMap({
  captureStatus,
  captureDetail,
  engineStatus,
  engineDetail,
}: {
  captureStatus: string;
  captureDetail: string;
  engineStatus: string;
  engineDetail: string;
}) {
  const stages: Stage[] = [
    {
      number: 1,
      title: "Infrastructure",
      status: captureStatus === "LIVE" || captureStatus === "OK" ? "WORKING" : captureStatus,
      tone: captureStatus === "LIVE" || captureStatus === "OK" ? "working" : "warning",
      purpose: "Collect trustworthy market observations and preserve replayable data.",
      href: "#infrastructure",
    },
    {
      number: 2,
      title: "Structure Engine",
      status: engineStatus === "OK" ? "WORKING" : engineStatus,
      tone: engineStatus === "OK" ? "working" : "warning",
      purpose: "Turn observations into multi-scale levels, features and market-state evidence.",
      href: "#infrastructure",
    },
    {
      number: 3,
      title: "Research",
      status: "ACTIVE",
      tone: "active",
      purpose: "Generate hypotheses, explore them in the sandbox, and keep an experiment library.",
      href: "#research",
    },
    {
      number: 4,
      title: "Validation",
      status: "V0 COMPLETE · NEXT TEST TBD",
      tone: "active",
      purpose: "Lock candidate rules before looking at fresh data, then decide pass / fail / learn.",
      href: "#test-library",
    },
    {
      number: 5,
      title: "Strategy",
      status: "WAITING FOR EDGE",
      tone: "blocked",
      purpose: "Convert a validated signal into entry, exit, sizing, costs and instrument choice.",
      href: "#strategy",
    },
    {
      number: 6,
      title: "Hummingbot",
      status: "DOWNSTREAM",
      tone: "blocked",
      purpose: "Backtest, paper trade and eventually execute only after a strategy earns promotion.",
      href: "#strategy",
    },
    {
      number: 7,
      title: "Product",
      status: "BUILDING TOWARD",
      tone: "future",
      purpose: "Become either an edge-producing system, a sellable research tool, or both.",
      href: "#product",
    },
  ];

  return (
    <>
      <section className="panel" id="project-map">
        <div className="panel-sub">THE WHOLE PROJECT</div>
        <h2 style={{ margin: "0.15rem 0 0.4rem" }}>From messy market data to something we can trust, trade, or sell.</h2>
        <p style={{ maxWidth: "960px", marginTop: 0 }}>
          This is the permanent workflow. We can run dozens of experiments without changing the structure: infrastructure feeds the engine, the engine feeds research, research produces validated signals, signals become strategies, and Hummingbot handles execution. The product layer packages whatever becomes genuinely useful.
        </p>
        <div className="row" style={{ gap: "0.45rem", flexWrap: "wrap", alignItems: "center", margin: "0.75rem 0" }}>
          <span className="tiny-pill">CAPTURE</span><strong>→</strong>
          <span className="tiny-pill">STRUCTURE</span><strong>→</strong>
          <span className="tiny-pill">RESEARCH</span><strong>→</strong>
          <span className="tiny-pill">VALIDATE</span><strong>→</strong>
          <span className="tiny-pill">STRATEGY</span><strong>→</strong>
          <span className="tiny-pill">HUMMINGBOT</span><strong>→</strong>
          <span className="tiny-pill">PRODUCT</span>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: "0.6rem" }}>
          {stages.map(stage => <StageCard key={stage.number} stage={stage} />)}
        </div>
      </section>

      <section className="panel" style={{ marginTop: "0.8rem" }}>
        <div className="panel-sub">WHERE ARE WE RIGHT NOW?</div>
        <h2 style={{ margin: "0.15rem 0 0.4rem" }}>Stage 3–4: Research + Validation</h2>
        <p style={{ marginTop: 0, maxWidth: "920px" }}>
          The plumbing works well enough to run real experiments. V0 is finished and did not show an edge. We are now using the sandbox to generate narrower candidate hypotheses, then we will lock promising ones and test them on untouched data.
        </p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "0.55rem" }}>
          <div className="panel compact"><div className="panel-sub">INFRASTRUCTURE</div><strong>{captureStatus}</strong><div className="panel-sub" style={{ marginTop: "0.25rem" }}>{captureDetail}</div></div>
          <div className="panel compact"><div className="panel-sub">ENGINE</div><strong>{engineStatus}</strong><div className="panel-sub" style={{ marginTop: "0.25rem" }}>{engineDetail}</div></div>
          <div className="panel compact"><div className="panel-sub">ACTIVE WORK</div><strong>Hypothesis discovery</strong><div className="panel-sub" style={{ marginTop: "0.25rem" }}>Explore → candidate → lock → fresh test → decision.</div></div>
          <div className="panel compact"><div className="panel-sub">TRADING</div><strong>Blocked on purpose</strong><div className="panel-sub" style={{ marginTop: "0.25rem" }}>No validated signal has earned strategy or execution work yet.</div></div>
        </div>
      </section>

      <nav className="panel compact" style={{ marginTop: "0.8rem" }} aria-label="Market Structure project sections">
        <div className="panel-sub">JUMP TO A LANE</div>
        <div className="row" style={{ gap: "0.5rem", flexWrap: "wrap", marginTop: "0.45rem" }}>
          <a className="btn" href="#infrastructure">Infrastructure</a>
          <a className="btn" href="#research">Active research</a>
          <a className="btn" href="#test-library">Tests already run</a>
          <a className="btn" href="#findings">What we know</a>
          <a className="btn" href="#strategy">Strategy / Hummingbot</a>
          <a className="btn" href="#product">Product path</a>
        </div>
      </nav>
    </>
  );
}
