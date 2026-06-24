import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { MonitorContent } from "@/components/MonitorContent";
import { loadMonitorFeed } from "@/lib/monitorHistoryFeed";
import { resolveWorkflowOwnerId } from "@/lib/msosWorkflowOwner";

export const metadata: Metadata = {
  title: "Monitor | Market Structure OS",
  description: "Watch saved views and paper trades from your workspace.",
};

export default async function MonitorPage() {
  const ownerId = await resolveWorkflowOwnerId();
  const feed = await loadMonitorFeed(ownerId);
  return (
    <AppShell activeNavId="monitor">
      <MonitorContent feed={feed} />
    </AppShell>
  );
}
