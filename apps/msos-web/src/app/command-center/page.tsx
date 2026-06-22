import type { Metadata } from "next";
import { headers } from "next/headers";

import { AppShell } from "@/components/AppShell";
import { CommandCenterContent } from "@/components/CommandCenterContent";
import { commandCenterMetadata } from "@/content/commandCenter";
import { loadCommandCenterSummary } from "@/lib/commandCenterSummary";
import { resolveMsosIdentityFromHeaders } from "@/lib/msosIdentity";

export const metadata: Metadata = commandCenterMetadata;

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
