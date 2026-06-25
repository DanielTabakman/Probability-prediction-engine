import { Suspense } from "react";

import { StrategyLabClientShell } from "@/components/StrategyLabClientShell";
import type { DisplayPayload } from "@/lib/ppeDisplayPayload";

type StrategyLabContentProps = {
  displayPayload?: DisplayPayload | null;
};

export function StrategyLabContent({ displayPayload = null }: StrategyLabContentProps) {
  return (
    <Suspense fallback={<p className="footer-note">Loading Strategy Lab…</p>}>
      <StrategyLabClientShell initialPayload={displayPayload} />
    </Suspense>
  );
}
