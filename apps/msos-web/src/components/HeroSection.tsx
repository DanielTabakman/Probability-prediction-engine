"use client";

import { useState } from "react";

import { ActionButton, ActionLink } from "@/components/ActionLink";
import { ResearchBetaModal } from "@/components/ResearchBetaModal";
import { resolveSignInUrl } from "@/lib/msosPublicUrls";
import { strategyLabForcedTourHref, strategyLabTutorialHref } from "@/lib/platformTutorial";
import { resolveResearchOfferCta } from "@/lib/researchOfferCta";

export function HeroSection() {
  const signInUrl = resolveSignInUrl();
  const researchOffer = resolveResearchOfferCta();
  const [researchOpen, setResearchOpen] = useState(false);

  return (
    <section>
      <div className="eyebrow">For traders with a market view</div>
      <h1>Turn your market thesis into a trade you can reason about.</h1>
      <p>
        Compare what BTC and ETH options imply with your own view, see the disagreement on a chart, and
        explore paper-trade structures — with assumptions visible, not hidden.
      </p>
      <div className="hero-actions">
        <ActionLink
          className="btn primary"
          href={strategyLabForcedTourHref()}
          pendingLabel="Opening tour…"
        >
          Start guided tour <span aria-hidden="true">→</span>
        </ActionLink>
        <ActionLink className="btn" href={strategyLabTutorialHref()}>
          Jump to Strategy Lab
        </ActionLink>
        <ActionButton className="btn" onClick={() => setResearchOpen(true)}>
          {researchOffer?.label ?? "Request research beta"}
        </ActionButton>
        <a className="btn slim dark" href={signInUrl}>
          Sign in
        </a>
      </div>
      <p className="hero-hint">
        <span className="pill compact">
          <span className="dot" aria-hidden="true" />
          BTC + ETH options live · paper trading only
        </span>
      </p>
      <ResearchBetaModal open={researchOpen} onClose={() => setResearchOpen(false)} />
    </section>
  );
}
