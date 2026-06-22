import Link from "next/link";

import { MSOS_ROUTES, resolveSignInUrl } from "@/lib/msosPublicUrls";
import { resolveResearchOfferCta } from "@/lib/researchOfferCta";

export function HeroSection() {
  const signInUrl = resolveSignInUrl();
  const researchOffer = resolveResearchOfferCta();

  return (
    <section>
      <div className="eyebrow">See what the market prices. State what you believe.</div>
      <h1>Compare your view to what BTC options imply.</h1>
      <p>
        Market Structure OS helps options traders read implied distributions, spell out a view in plain
        language, and sketch paper trades — without pretending the platform knows better than you.
      </p>
      <div className="hero-actions">
        <Link className="btn primary" href={MSOS_ROUTES.strategyLab}>
          Open Strategy Lab <span aria-hidden="true">→</span>
        </Link>
        <Link className="btn" href={MSOS_ROUTES.commandCenter}>
          Command Center
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
          Your view, your decision
        </span>
        <span className="pill">
          <span className="dot amber" />
          Fit ideas to structures — not buy/sell tips
        </span>
        <span className="pill">Live BTC options on the demo</span>
      </div>
      <div className="semantic-lock">
        <div className="lock">
          <h3>Read</h3>
          <p>What is the options market pricing for this expiry?</p>
        </div>
        <div className="lock">
          <h3>State</h3>
          <p>Where do you disagree — level, vol, or both?</p>
        </div>
        <div className="lock">
          <h3>Plan</h3>
          <p>Paper-trade structures that match your view.</p>
        </div>
      </div>
      <div className="lens-row" aria-label="Market lens availability">
        <span className="tag">BTC options — Live</span>
        <span className="tag muted">Event markets — Coming</span>
        <span className="tag muted">Perp positioning — Coming</span>
      </div>
    </section>
  );
}
