import Link from "next/link";

import { MSOS_ROUTES } from "@/lib/msosPublicUrls";

export default function NotFound() {
  return (
    <main className="not-found-shell">
      <div className="panel not-found-panel">
        <div className="crumb">Not found</div>
        <h1 className="title">This page isn&apos;t available</h1>
        <p className="panel-sub">
          The link may be outdated or the item was removed. Head back to a live area of the app.
        </p>
        <div className="not-found-actions">
          <Link href={MSOS_ROUTES.monitor} className="btn slim primary">
            Monitor
          </Link>
          <Link href={MSOS_ROUTES.commandCenter} className="btn slim">
            Command Center
          </Link>
          <Link href={MSOS_ROUTES.strategyLab} className="btn slim">
            Strategy Lab
          </Link>
        </div>
      </div>
    </main>
  );
}
