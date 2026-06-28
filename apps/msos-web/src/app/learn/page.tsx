import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { ConclusionContent } from "@/components/ConclusionContent";

export const metadata: Metadata = {
  title: "Learn loop | Market Structure OS",
  description:
    "Reflect on a session — feedback helps improve the demo for new traders.",
};

type LearnPageProps = {
  searchParams: Promise<{ debrief?: string }>;
};

export default async function LearnPage({ searchParams }: LearnPageProps) {
  const params = await searchParams;
  return (
    <AppShell activeNavId="learn">
      <ConclusionContent highlightDebrief={params.debrief === "1"} />
    </AppShell>
  );
}
