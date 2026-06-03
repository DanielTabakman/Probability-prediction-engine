import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { CommandCenterContent } from "@/components/CommandCenterContent";

export const metadata: Metadata = {
  title: "Command Center | Market Structure OS",
  description:
    "Authenticated MSOS workspace overview — fixture preview data; BTC options lens live in preview.",
};

export default function CommandCenterPage() {
  return (
    <AppShell activeNavId="command-center">
      <CommandCenterContent />
    </AppShell>
  );
}
