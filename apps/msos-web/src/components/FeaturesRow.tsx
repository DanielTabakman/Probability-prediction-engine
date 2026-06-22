const FEATURES = [
  {
    n: "01",
    title: "Read the market",
    body: "See the range and shape BTC options imply — updated from live quotes.",
  },
  {
    n: "02",
    title: "State your view",
    body: "Higher, lower, more vol, less vol — say what you believe in plain language.",
  },
  {
    n: "03",
    title: "Plan a trade",
    body: "Match structures to your view with risk limits spelled out upfront.",
  },
  {
    n: "04",
    title: "Review over time",
    body: "Track paper trades and learn whether your reads were useful.",
  },
] as const;

export function FeaturesRow() {
  return (
    <section className="features-row" aria-label="How it works">
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
