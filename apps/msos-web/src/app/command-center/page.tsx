import type { Metadata } from "next";
import { headers } from "next/headers";

import { AppShell } from "@/components/AppShell";
import { CommandCenterContent } from "@/components/CommandCenterContent";
import { loadCommandCenterSummary } from "@/lib/commandCenterSummary";
import { resolveMsosIdentityFromHeaders } from "@/lib/msosIdentity";

export const metadata: Metadata = {
  title: "Command Center | Market Structure OS",
  description:
    "Track saved views and paper trades — reminders only, not trade advice.",
};

export default async function CommandCenterPage() {
  const requestHeaders = await headers();
  const ownerEmail = resolveMsosIdentityFromHeaders(requestHeaders);
  const summary = loadCommandCenterSummary(ownerEmail);
  return (
    <AppShell activeNavId="command-center">
      <CommandCenterContent summary={summary} />
    </AppShell>
  );
}
