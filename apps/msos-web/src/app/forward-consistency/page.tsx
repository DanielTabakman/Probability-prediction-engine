import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { ForwardConsistencyDashboardContent } from "@/components/ForwardConsistencyDashboardContent";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Forward consistency | Market Structure OS",
  description:
    "Ops dashboard — options-implied forward vs futures/perp across assets and expiries. Research only.",
};

export default function ForwardConsistencyPage() {
  return (
    <AppShell activeNavId="forward-consistency">
      <ForwardConsistencyDashboardContent />
    </AppShell>
  );
}
