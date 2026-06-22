import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { StrategyLabContent } from "@/components/StrategyLabContent";
import { strategyLabMetadata } from "@/content/strategyLab";
import { fetchDisplayPayload } from "@/lib/ppeDisplayPayload";

export const metadata: Metadata = strategyLabMetadata;

export default async function StrategyLabPage() {
  const displayPayload = await fetchDisplayPayload();

  return (
    <AppShell activeNavId="strategy-lab">
      <StrategyLabContent displayPayload={displayPayload} />
    </AppShell>
  );
}
