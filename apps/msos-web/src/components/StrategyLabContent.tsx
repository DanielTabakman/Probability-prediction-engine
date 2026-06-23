import Link from "next/link";

import { StrategyLabWorkSection } from "@/components/StrategyLabWorkSection";
import { DEMO_FOOTER } from "@/lib/publicCopy";
import type { DisplayPayload } from "@/lib/ppeDisplayPayload";

type StrategyLabContentProps = {
  displayPayload?: DisplayPayload | null;
};

export function StrategyLabContent({ displayPayload = null }: StrategyLabContentProps) {
  const live = displayPayload != null;

  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Strategy Lab · BTC options</div>
          <h1 className="title">Strategy Lab</h1>
        </div>
        <div className="tools">
          <span className="pill">
            <span className="dot" aria-hidden="true" />
            {live ? "Live market data" : "Demo data"}
          </span>
          <span className="btn slim">Share</span>
          <Link href="/strategy-lab/confirm" className="btn slim primary">
            Save your view
          </Link>
          <span className="avatar" aria-hidden="true">
            DT
          </span>
        </div>
      </header>

      <StrategyLabWorkSection displayPayload={displayPayload} />

      <p className="footer-note">{DEMO_FOOTER}</p>
    </>
  );
}
