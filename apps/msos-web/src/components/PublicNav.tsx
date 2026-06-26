"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { ActionLink } from "@/components/ActionLink";
import { MsosLogo } from "@/components/MsosLogo";
import { MSOS_ROUTES, resolveSignInUrl } from "@/lib/msosPublicUrls";
import { clearPlatformTutorialComplete } from "@/lib/platformTutorial";

export function PublicNav() {
  const signInUrl = resolveSignInUrl();
  const router = useRouter();

  const restartTour = () => {
    clearPlatformTutorialComplete();
    router.push("/strategy-lab?tutorial=1");
  };

  return (
    <nav className="public-nav">
      <Link className="brand" href={MSOS_ROUTES.home}>
        <MsosLogo className="logo" size={38} />
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
        <button type="button" className="nav-text-btn" onClick={restartTour}>
          Restart tour
        </button>
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
