import type { Metadata } from "next";
import { headers } from "next/headers";

import { AppShell } from "@/components/AppShell";
import { HistoryContent } from "@/components/HistoryContent";
import { loadHistoryFeed } from "@/lib/monitorHistoryFeed";
import { resolveMsosIdentityFromHeaders } from "@/lib/msosIdentity";

export const metadata: Metadata = {
  title: "History | Market Structure OS",
  description: "Track saved views and paper trades over time.",
};

export default async function HistoryPage() {
  const requestHeaders = await headers();
  const ownerEmail = resolveMsosIdentityFromHeaders(requestHeaders);
  const feed = await loadHistoryFeed(ownerEmail);
  return (
    <AppShell activeNavId="history">
      <HistoryContent feed={feed} />
    </AppShell>
  );
}
