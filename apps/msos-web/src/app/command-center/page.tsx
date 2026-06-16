import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { CommandCenterContent } from "@/components/CommandCenterContent";
import { loadCommandCenterSummary } from "@/lib/commandCenterSummary";

export const metadata: Metadata = {
  title: "Command Center | Market Structure OS",
  description:
    "Authenticated MSOS workspace — KPI and current work from PPE frozen snapshots when configured.",
};

export default function CommandCenterPage() {
  const summary = loadCommandCenterSummary();
  return (
    <AppShell activeNavId="command-center">
      <CommandCenterContent summary={summary} />
    </AppShell>
  );
}
