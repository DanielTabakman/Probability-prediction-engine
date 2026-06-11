import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { ExpressionPlanningPanel } from "@/components/ExpressionPlanningPanel";

export const metadata: Metadata = {
  title: "Expression planning | Strategy Lab | Market Structure OS",
  description:
    "MSOS expression planning — compare families, optimized plan ticket, sim-only save. No live order transmission.",
};

export default function ExpressionPlanningPage() {
  return (
    <AppShell activeNavId="expression">
      <ExpressionPlanningPanel />
    </AppShell>
  );
}
