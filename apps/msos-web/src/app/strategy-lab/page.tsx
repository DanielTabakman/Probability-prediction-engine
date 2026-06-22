import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { StrategyLabContent } from "@/components/StrategyLabContent";
import { fetchDisplayPayload } from "@/lib/ppeDisplayPayload";

export const metadata: Metadata = {
  title: "Strategy Lab | Market Structure OS",
  description:
    "Compare your view to what BTC options imply — live Deribit data on the demo.",
};

export default async function StrategyLabPage() {
  const displayPayload = await fetchDisplayPayload();

  return (
    <AppShell activeNavId="strategy-lab">
      <StrategyLabContent displayPayload={displayPayload} />
    </AppShell>
  );
}
