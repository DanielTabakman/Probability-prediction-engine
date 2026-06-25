import type { Metadata } from "next";
import { redirect } from "next/navigation";

import { AppShell } from "@/components/AppShell";
import { PaperTradeDetailContent } from "@/components/PaperTradeDetailContent";
import { resolveWorkflowOwnerId } from "@/lib/msosWorkflowOwner";
import { getPaperTradeById } from "@/lib/msosWorkflowStore";
import { fetchDisplayPayload } from "@/lib/ppeDisplayPayload";

export const metadata: Metadata = {
  title: "Paper trade | Monitor | Market Structure OS",
  description: "Saved paper trade detail — legs, marks, and belief snapshot.",
};

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function PaperTradeDetailPage({ params }: PageProps) {
  const { id } = await params;
  const ownerId = await resolveWorkflowOwnerId();
  const [trade, display] = await Promise.all([
    getPaperTradeById(ownerId ?? "", id),
    fetchDisplayPayload(),
  ]);
  if (!trade) {
    redirect("/monitor");
  }
  return (
    <AppShell activeNavId="monitor">
      <PaperTradeDetailContent trade={trade} currentSpotUsd={display?.spot_usd ?? null} />
    </AppShell>
  );
}
