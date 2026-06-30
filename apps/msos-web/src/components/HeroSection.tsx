"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import { ActionButton, ActionLink } from "@/components/ActionLink";
import { ResearchBetaModal } from "@/components/ResearchBetaModal";
import { resolveSignInUrl } from "@/lib/msosPublicUrls";
import { scheduleStrategyLabTourPrefetch } from "@/lib/prefetchStrategyLab";
import { strategyLabForcedTourHref, strategyLabTutorialHref } from "@/lib/platformTutorial";
import { resolveResearchOfferCta } from "@/lib/researchOfferCta";

export function HeroSection() {
  const router = useRouter();
  const signInUrl = resolveSignInUrl();
  const researchOffer = resolveResearchOfferCta();
  const [researchOpen, setResearchOpen] = useState(false);

  useEffect(() => scheduleStrategyLabTourPrefetch(router), [router]);

  return (
    <section>
      <div className="eyebrow">For traders with a market view</div>
      <h1>Turn your market thesis into a trade you can reason about.</h1>
      <p>
        Compare what BTC and ETH options imply with your own view, see the disagreement on a chart, and
        explore paper-trade structures — with assumptions visible, not hidden.
      </p>
      <div className="hero-cta-primary" data-self-serve-entry="hero-tour">
        <p className="hero-cta-eyebrow">Recommended first step</p>
        <ActionLink
          className="btn primary hero-tour-btn"
          href={strategyLabForcedTourHref()}
          pendingLabel="Opening tour…"
          warmupOnHover
        >
          Start guided tour
          <span className="hero-tour-arrow" aria-hidden="true">
            →
          </span>
        </ActionLink>
        <p className="hero-cta-hint">
          3-minute walkthrough of Strategy Lab with live BTC options — paper trading only, no sign-in
          required.
        </p>
      </div>
      <div className="hero-actions-secondary">
        <ActionLink className="btn slim" href={strategyLabTutorialHref()} warmupOnHover>
          Jump to Strategy Lab
        </ActionLink>
        <ActionButton className="btn slim" onClick={() => setResearchOpen(true)}>
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
