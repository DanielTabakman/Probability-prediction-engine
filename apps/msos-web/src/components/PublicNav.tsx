import Link from "next/link";

import { MSOS_ROUTES, resolveSignInUrl } from "@/lib/msosPublicUrls";

export function PublicNav() {
  const signInUrl = resolveSignInUrl();

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
        <Link className="sel" href={MSOS_ROUTES.home}>
          Platform
        </Link>
        <Link href={MSOS_ROUTES.strategyLab}>Strategy Lab</Link>
        <Link href={MSOS_ROUTES.monitor}>Market surfaces</Link>
        <Link href={MSOS_ROUTES.learn}>Vision</Link>
        <div className="nav-actions">
          <a className="btn slim dark" href={signInUrl}>
            Sign in
          </a>
          <Link className="btn slim primary" href={MSOS_ROUTES.commandCenter}>
            Enter Command Center
          </Link>
        </div>
      </div>
    </nav>
  );
}
