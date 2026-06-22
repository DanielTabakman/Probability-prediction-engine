import Link from "next/link";

import { MSOS_ROUTES, resolveSignInUrl } from "@/lib/msosPublicUrls";
import { resolveResearchOfferCta } from "@/lib/researchOfferCta";

const PRODUCT_CARDS = [
  {
    title: "Market Structure OS",
    body: "One workspace for thesis-driven market decisions.",
  },
  {
    title: "Strategy Lab",
    body: "Build, compare, and monitor strategies from a clear market view.",
  },
  {
    title: "Probability Engine",
    body: "See where options pricing agrees — or disagrees — with your thesis.",
  },
] as const;

export function HeroSection() {
  const signInUrl = resolveSignInUrl();
  const researchOffer = resolveResearchOfferCta();

  return (
    <section>
      <div className="eyebrow">For traders with a market view</div>
      <h1>Turn your market thesis into a trade you can reason about.</h1>
      <p>
        Market Structure OS helps traders compare market-implied probabilities with their own view,
        locate meaningful disagreement, and explore structures that fit the thesis — without hiding
        the assumptions.
      </p>
      <div className="hero-actions">
        <Link className="btn primary" href={MSOS_ROUTES.strategyLab}>
          Explore the platform <span aria-hidden="true">→</span>
        </Link>
        <Link className="btn" href={MSOS_ROUTES.commandCenter}>
          Open Command Center
        </Link>
        {researchOffer ? (
          <a className="btn" href={researchOffer.url}>
            {researchOffer.label}
          </a>
        ) : null}
        <a className="btn slim dark" href={signInUrl}>
          Sign in
        </a>
      </div>
      <div className="chips">
        <span className="pill">
          <span className="dot" />
          Your thesis stays yours
        </span>
        <span className="pill">
          <span className="dot amber" />
          Expression, not recommendation
        </span>
        <span className="pill">BTC options live preview</span>
      </div>
      <div className="semantic-lock" aria-label="Platform products">
        {PRODUCT_CARDS.map((card) => (
          <div className="lock" key={card.title}>
            <h3>{card.title}</h3>
            <p>{card.body}</p>
          </div>
        ))}
      </div>
      <div className="lens-row" aria-label="Market lens availability">
        <span className="tag">BTC options — Live</span>
        <span className="tag muted">Event markets — Coming</span>
        <span className="tag muted">Perp positioning — Coming</span>
      </div>
    </section>
  );
}
