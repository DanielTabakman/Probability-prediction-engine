import { RestartTourButton } from "@/components/RestartTourButton";

const FEATURES = [
  {
    title: "Read the market",
    body: "Live BTC options distribution from Deribit — what the chain implies at your expiry.",
  },
  {
    title: "State your view",
    body: "Nudge price and vol versus the market curve; confirm when it matches what you believe.",
  },
  {
    title: "Fit a structure",
    body: "Paper-trade expressions that map payoff to your thesis — no live orders on this demo.",
  },
] as const;

export function FeaturesRow() {
  return (
    <section className="features-row" aria-label="How it works">
      {FEATURES.map((feature) => (
        <article className="feature" key={feature.title}>
          <h3>{feature.title}</h3>
          <p>{feature.body}</p>
        </article>
      ))}
      <div className="feature feature-cta">
        <h3>Ready?</h3>
        <p>Walk through Strategy Lab with the guided tour — or jump straight in.</p>
        <RestartTourButton className="btn slim primary">Start the tour</RestartTourButton>
      </div>
    </section>
  );
}
