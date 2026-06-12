import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { ConclusionContent } from "@/components/ConclusionContent";

export const metadata: Metadata = {
  title: "Learn loop | Market Structure OS",
  description:
    "MSOS tester release conclusion — learn loop narrative and validation metrics template (preview).",
};

export default function LearnPage() {
  return (
    <AppShell activeNavId="learn">
      <ConclusionContent />
    </AppShell>
  );
}
