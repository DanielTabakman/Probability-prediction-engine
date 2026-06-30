import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { StrategyLabContent } from "@/components/StrategyLabContent";

export const metadata: Metadata = {
  title: "Strategy Lab | Market Structure OS",
  description:
    "Compare your view to what options imply — live market data on the demo.",
};

/** Shell renders immediately; live payload loads client-side in StrategyLabClientShell. */
export default function StrategyLabPage() {
  return (
    <AppShell activeNavId="strategy-lab">
      <StrategyLabContent />
    </AppShell>
  );
}
