const FEATURES = [
  {
    n: "01 - Read",
    title: "Read market surfaces",
    body: "Options, event probabilities, positioning and contextual data as modular lenses.",
  },
  {
    n: "02 - State",
    title: "State your thesis",
    body: "Translate a human view into a structured thesis the system can compare.",
  },
  {
    n: "03 - Fit",
    title: "Find fitting expression",
    body: "Compare expression families without hiding assumptions or risk constraints.",
  },
  {
    n: "04 - Learn",
    title: "Build calibration memory",
    body: "Track perception quality, expression fit and outcomes over time.",
  },
] as const;

export function FeaturesRow() {
  return (
    <section className="features-row" aria-label="Platform journey">
      {FEATURES.map((feature) => (
        <article className="feature" key={feature.n}>
          <div className="n">{feature.n}</div>
          <h3>{feature.title}</h3>
          <p>{feature.body}</p>
        </article>
      ))}
    </section>
  );
}
