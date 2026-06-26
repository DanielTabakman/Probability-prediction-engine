"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";

import {
  markMonitorWelcomeDismissed,
  MONITOR_WELCOME_QUERY,
  shouldShowMonitorWelcome,
} from "@/lib/monitorWelcome";

type MonitorWelcomeCardProps = {
  paperTradeCount: number;
  firstTradeHref?: string;
};

export function MonitorWelcomeCard({ paperTradeCount, firstTradeHref }: MonitorWelcomeCardProps) {
  const searchParams = useSearchParams();
  const welcomeQuery = searchParams.get(MONITOR_WELCOME_QUERY) === "1";
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setVisible(shouldShowMonitorWelcome(paperTradeCount, welcomeQuery));
  }, [paperTradeCount, welcomeQuery]);

  if (!visible) {
    return null;
  }

  function dismiss() {
    markMonitorWelcomeDismissed();
    setVisible(false);
  }

  return (
    <div className="monitor-welcome-card" role="status">
      <div>
        <strong>Your first paper trade is on the watch list</strong>
        <p>
          We compare live BTC to the prices you saved at — no orders, no broker connection. Tap a
          trade to see how the sketch is tracking until expiry.
        </p>
        {firstTradeHref ? (
          <Link href={firstTradeHref} className="btn slim primary monitor-welcome-cta">
            Open your paper trade
          </Link>
        ) : null}
      </div>
      <button type="button" className="btn slim dark" onClick={dismiss}>
        Got it
      </button>
    </div>
  );
}
