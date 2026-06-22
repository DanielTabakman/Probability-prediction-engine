import Link from "next/link";

import {
  homepageHero,
  homepageLensTags,
  homepageProductCards,
} from "@/content/homepage";
import { MSOS_ROUTES, resolveSignInUrl } from "@/lib/msosPublicUrls";
import { resolveResearchOfferCta } from "@/lib/researchOfferCta";

export function HeroSection() {
  const signInUrl = resolveSignInUrl();
  const researchOffer = resolveResearchOfferCta();

  return (
    <section>
      <div className="eyebrow">{homepageHero.eyebrow}</div>
      <h1>{homepageHero.h1}</h1>
      <p>{homepageHero.body}</p>
      <div className="hero-actions">
        <Link className="btn primary" href={MSOS_ROUTES.strategyLab}>
          {homepageHero.primaryCta} <span aria-hidden="true">→</span>
        </Link>
        <Link className="btn" href={MSOS_ROUTES.commandCenter}>
          {homepageHero.secondaryCta}
        </Link>
        {researchOffer ? (
          <a className="btn" href={researchOffer.url}>
            {researchOffer.label}
          </a>
        ) : null}
        <a className="btn slim dark" href={signInUrl}>
          {homepageHero.signInCta}
        </a>
      </div>
      <div className="chips">
        <span className="pill">
          <span className="dot" />
          {homepageHero.pills[0]}
        </span>
        <span className="pill">
          <span className="dot amber" />
          {homepageHero.pills[1]}
        </span>
        <span className="pill">{homepageHero.pills[2]}</span>
      </div>
      <div className="semantic-lock" aria-label="Platform products">
        {homepageProductCards.map((card) => (
          <div className="lock" key={card.title}>
            <h3>{card.title}</h3>
            <p>{card.body}</p>
          </div>
        ))}
      </div>
      <div className="lens-row" aria-label="Market lens availability">
        <span className="tag">{homepageLensTags.btcLive}</span>
        <span className="tag muted">{homepageLensTags.eventMarkets}</span>
        <span className="tag muted">{homepageLensTags.perpPositioning}</span>
      </div>
    </section>
  );
}
