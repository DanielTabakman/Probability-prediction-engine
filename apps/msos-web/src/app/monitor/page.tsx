import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { MonitorContent } from "@/components/MonitorContent";

export const metadata: Metadata = {
  title: "Monitor | Market Structure OS",
  description: "MSOS thesis and expression monitoring — preview fixtures only.",
};

export default function MonitorPage() {
  return (
    <AppShell activeNavId="monitor">
      <MonitorContent />
    </AppShell>
  );
}
