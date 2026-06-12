import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { HistoryContent } from "@/components/HistoryContent";

export const metadata: Metadata = {
  title: "History | Market Structure OS",
  description: "MSOS lifecycle history — observed, saved, simulated, reviewed (preview).",
};

export default function HistoryPage() {
  return (
    <AppShell activeNavId="history">
      <HistoryContent />
    </AppShell>
  );
}
