import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { HistoryContent } from "@/components/HistoryContent";
import { loadHistoryFeed } from "@/lib/monitorHistoryFeed";
import { resolveWorkflowOwnerId } from "@/lib/msosWorkflowOwner";

export const metadata: Metadata = {
  title: "History | Market Structure OS",
  description: "MSOS lifecycle history — observed, saved, simulated, reviewed from live feeds.",
};

export default async function HistoryPage() {
  const ownerId = await resolveWorkflowOwnerId();
  const feed = await loadHistoryFeed(ownerId);
  return (
    <AppShell activeNavId="history">
      <HistoryContent feed={feed} />
    </AppShell>
  );
}
