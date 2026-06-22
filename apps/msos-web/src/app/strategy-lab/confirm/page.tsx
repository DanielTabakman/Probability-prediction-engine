import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { ThesisConfirmationPanel } from "@/components/ThesisConfirmationPanel";

export const metadata: Metadata = {
  title: "Confirm your view | Strategy Lab | Market Structure OS",
  description:
    "Lock in your view in plain language — then plan a paper trade. No live orders.",
};

export default function ThesisConfirmPage() {
  return (
    <AppShell activeNavId="strategy-lab">
      <ThesisConfirmationPanel />
    </AppShell>
  );
}
