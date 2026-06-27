import type { Metadata } from "next";

/** Agent: msos-shell Strategy Lab SSR — fetches Python display JSON; no TS math. Tests: tests/test_msos_web_strategy_lab.py */
import { AppShell } from "@/components/AppShell";
import { StrategyLabContent } from "@/components/StrategyLabContent";
import {
  fetchDisplayPayload,
  normalizeLabAssetId,
} from "@/lib/ppeDisplayPayload";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Strategy Lab | Market Structure OS",
  description:
    "Compare your view to what options imply — live market data on the demo.",
};

type StrategyLabPageProps = {
  searchParams: Promise<{ asset?: string | string[] }>;
};

export default async function StrategyLabPage({ searchParams }: StrategyLabPageProps) {
  const params = await searchParams;
  const rawAsset = Array.isArray(params.asset) ? params.asset[0] : params.asset;
  const assetId = normalizeLabAssetId(rawAsset);
  const displayPayload = await fetchDisplayPayload(assetId);

  return (
    <AppShell activeNavId="strategy-lab">
      <StrategyLabContent displayPayload={displayPayload} />
    </AppShell>
  );
}
