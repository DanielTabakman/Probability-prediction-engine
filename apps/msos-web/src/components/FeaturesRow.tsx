import { homepageFeatures } from "@/content/homepage";

export function FeaturesRow() {
  return (
    <section className="features-row" aria-label="How it works">
      {homepageFeatures.map((feature) => (
        <article className="feature" key={feature.kicker}>
          <div className="n">{feature.kicker}</div>
          <h3>{feature.title}</h3>
          <p>{feature.body}</p>
        </article>
      ))}
    </section>
  );
}
