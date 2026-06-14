import Link from "next/link";

import type { ResearchOfferCta } from "@/lib/researchOfferCta";

type PublicNavProps = {
  researchOffer?: ResearchOfferCta | null;
};

export function PublicNav({ researchOffer = null }: PublicNavProps) {
  return (
    <nav className="public-nav">
      <div className="brand">
        <div className="logo" aria-hidden="true" />
        <div>
          Market Structure OS
          <small>Probability &amp; thesis intelligence</small>
        </div>
      </div>
      <div className="nav-links">
        <span className="sel">Platform</span>
        <span>Strategy Lab</span>
        <span>Market surfaces</span>
        <span>Vision</span>
        <div className="nav-actions">
          <span className="btn slim dark">Sign in</span>
          {researchOffer ? (
            <Link className="btn slim primary" href={researchOffer.url}>
              {researchOffer.label}
            </Link>
          ) : null}
          <Link
            className={`btn slim ${researchOffer ? "dark" : "primary"}`}
            href="/command-center"
          >
            Enter Command Center
          </Link>
        </div>
      </div>
    </nav>
  );
}
