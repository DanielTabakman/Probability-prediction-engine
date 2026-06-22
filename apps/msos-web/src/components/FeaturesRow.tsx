const FEATURES = [
  {
    kicker: "01 — Read",
    title: "See what the market implies",
    body: "Start with options pricing, probabilities, positioning, and other market surfaces.",
  },
  {
    kicker: "02 — State",
    title: "Add your thesis",
    body: "Turn your view into something the system can compare against the market.",
  },
  {
    kicker: "03 — Fit",
    title: "Explore possible expressions",
    body: "Compare structures that fit your view, risk limits, and time horizon.",
  },
  {
    kicker: "04 — Learn",
    title: "Track what happened",
    body: "Review how the thesis, structure, and outcome evolved over time.",
  },
] as const;

export function FeaturesRow() {
  return (
    <section className="features-row" aria-label="How it works">
      {FEATURES.map((feature) => (
        <article className="feature" key={feature.kicker}>
          <div className="n">{feature.kicker}</div>
          <h3>{feature.title}</h3>
          <p>{feature.body}</p>
        </article>
      ))}
    </section>
  );
}
