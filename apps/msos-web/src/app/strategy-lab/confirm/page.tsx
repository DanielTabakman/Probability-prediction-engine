import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { ThesisConfirmationPanel } from "@/components/ThesisConfirmationPanel";

export const metadata: Metadata = {
  title: "Thesis confirmation | Strategy Lab | Market Structure OS",
  description:
    "MSOS thesis confirmation — is this what you think is true? Preview persistence only; proceed to expression planning, not execution.",
};

export default function ThesisConfirmPage() {
  return (
    <AppShell activeNavId="strategy-lab">
      <ThesisConfirmationPanel />
    </AppShell>
  );
}
