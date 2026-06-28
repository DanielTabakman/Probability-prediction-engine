import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { ExpressionPlanningPanel } from "@/components/ExpressionPlanningPanel";

export const metadata: Metadata = {
  title: "Expression planning | Strategy Lab | Market Structure OS",
  description:
    "Paper trade planner — compare structure types to your view. No live orders.",
};

export default function ExpressionPlanningPage() {
  return (
    <AppShell activeNavId="strategy-lab">
      <ExpressionPlanningPanel />
    </AppShell>
  );
}
