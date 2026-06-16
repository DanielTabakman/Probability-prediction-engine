import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { CommandCenterContent } from "@/components/CommandCenterContent";
import { loadWorkflowSummary } from "@/lib/msosWorkflowStore";

export const metadata: Metadata = {
  title: "Command Center | Market Structure OS",
  description:
    "Authenticated MSOS workspace overview — thesis workflow KPIs from the MSOS server store.",
};

export default async function CommandCenterPage() {
  const workflow = await loadWorkflowSummary();
  return (
    <AppShell activeNavId="command-center">
      <CommandCenterContent workflow={workflow} />
    </AppShell>
  );
}
