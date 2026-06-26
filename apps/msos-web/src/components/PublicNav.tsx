"use client";

import Link from "next/link";

import { ActionLink } from "@/components/ActionLink";
import { MSOS_ROUTES, resolveSignInUrl } from "@/lib/msosPublicUrls";
import { strategyLabRetakeTourHref } from "@/lib/platformTutorial";

export function PublicNav() {
  const signInUrl = resolveSignInUrl();

  return (
    <nav className="public-nav">
      <Link className="brand" href={MSOS_ROUTES.home}>
        <div className="logo" aria-hidden="true" />
        <div>
          Market Structure OS
          <small>For traders with a market view</small>
        </div>
      </Link>
      <div className="nav-links">
        <Link className="sel" href={MSOS_ROUTES.home}>
          Platform
        </Link>
        <ActionLink href={MSOS_ROUTES.strategyLab}>Strategy Lab</ActionLink>
        <ActionLink href={MSOS_ROUTES.monitor}>Monitor</ActionLink>
        <Link className="nav-text-btn" href={strategyLabRetakeTourHref()}>
          Retake tour
        </Link>
        <div className="nav-actions">
          <a className="btn slim dark" href={signInUrl}>
            Sign in
          </a>
          <ActionLink className="btn slim primary" href={MSOS_ROUTES.commandCenter}>
            Command Center
          </ActionLink>
        </div>
      </div>
    </nav>
  );
}
