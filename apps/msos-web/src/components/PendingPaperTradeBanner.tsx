"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { resolveSignInUrlWithReturn } from "@/lib/msosPublicUrls";
import { hasPendingPaperTrade, hasWorkflowIdentity } from "@/lib/msosWorkflowClient";

type PendingPaperTradeBannerProps = {
  returnPath?: string;
};

export function PendingPaperTradeBanner({
  returnPath = "/strategy-lab/expression",
}: PendingPaperTradeBannerProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      if (!hasPendingPaperTrade()) return;
      const signedIn = await hasWorkflowIdentity();
      if (!cancelled && !signedIn) {
        setVisible(true);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (!visible) {
    return null;
  }

  return (
    <div className="lab-data-banner demo pending-trade-banner" role="status">
      <span className="tag amber">Waiting</span>
      <div>
        <strong>Your paper trade is ready to save</strong>
        <p>
          Sign in to finish saving — we kept your plan while you authenticate.{" "}
          <Link href={returnPath}>Continue to paper trade planner</Link> or{" "}
          <a href={resolveSignInUrlWithReturn(returnPath)}>sign in now</a>.
        </p>
      </div>
    </div>
  );
}
