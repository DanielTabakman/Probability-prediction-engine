import Link from "next/link";

import { publicNavCopy } from "@/content/publicNav";
import { MSOS_ROUTES, resolveSignInUrl } from "@/lib/msosPublicUrls";

export function PublicNav() {
  const signInUrl = resolveSignInUrl();
  const nav = publicNavCopy;

  return (
    <nav className="public-nav">
      <Link className="brand" href={MSOS_ROUTES.home}>
        <div className="logo" aria-hidden="true" />
        <div>
          {nav.brandName}
          <small>{nav.brandTagline}</small>
        </div>
      </Link>
      <div className="nav-links">
        <Link className="sel" href={MSOS_ROUTES.home}>
          {nav.links.platform}
        </Link>
        <Link href={MSOS_ROUTES.strategyLab}>{nav.links.strategyLab}</Link>
        <Link href={MSOS_ROUTES.monitor}>{nav.links.marketSurfaces}</Link>
        <Link href={MSOS_ROUTES.learn}>{nav.links.vision}</Link>
        <div className="nav-actions">
          <a className="btn slim dark" href={signInUrl}>
            {nav.signInCta}
          </a>
          <Link className="btn slim primary" href={MSOS_ROUTES.commandCenter}>
            {nav.enterCommandCenterCta}
          </Link>
        </div>
      </div>
    </nav>
  );
}
