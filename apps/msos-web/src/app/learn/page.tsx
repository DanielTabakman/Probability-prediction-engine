import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { ConclusionContent } from "@/components/ConclusionContent";

export const metadata: Metadata = {
  title: "Learn | Market Structure OS",
  description:
    "Reflect on a session — feedback helps improve the demo for new traders.",
};

export default function LearnPage() {
  return (
    <AppShell activeNavId="learn">
      <ConclusionContent />
    </AppShell>
  );
}
