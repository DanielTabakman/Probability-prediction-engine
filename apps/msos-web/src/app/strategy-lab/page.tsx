import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { StrategyLabContent } from "@/components/StrategyLabContent";

export const metadata: Metadata = {
  title: "Strategy Lab | Market Structure OS",
  description:
    "MSOS Strategy Lab — PPE options distribution lens. Display/proxy boundary only; authoritative math in Streamlit.",
};

export default function StrategyLabPage() {
  return (
    <AppShell activeNavId="strategy-lab">
      <StrategyLabContent />
    </AppShell>
  );
}
