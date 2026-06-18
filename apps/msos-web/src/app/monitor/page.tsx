import type { Metadata } from "next";
import { headers } from "next/headers";

import { AppShell } from "@/components/AppShell";
import { MonitorContent } from "@/components/MonitorContent";
import { loadMonitorFeed } from "@/lib/monitorHistoryFeed";
import { resolveMsosIdentityFromHeaders } from "@/lib/msosIdentity";

export const metadata: Metadata = {
  title: "Monitor | Market Structure OS",
  description: "MSOS thesis and expression monitoring from workflow + PPE snapshot review metadata.",
};

export default async function MonitorPage() {
  const requestHeaders = await headers();
  const ownerEmail = resolveMsosIdentityFromHeaders(requestHeaders);
  const feed = await loadMonitorFeed(ownerEmail);
  return (
    <AppShell activeNavId="monitor">
      <MonitorContent feed={feed} />
    </AppShell>
  );
}
