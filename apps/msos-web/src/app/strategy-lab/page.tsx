import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { StrategyLabContent } from "@/components/StrategyLabContent";
import {
  bucketsFromCatalog,
  FALLBACK_ASSET_PICKER,
  fetchAssetCatalogServer,
  listSelectableAssetIds,
} from "@/lib/ppeAssetCatalog";
import { fetchDisplayPayload } from "@/lib/ppeDisplayPayload";
import { resolveLabAssetId } from "@/lib/strategyLabAsset";

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
  const catalog = await fetchAssetCatalogServer();
  const allowedIds = catalog
    ? listSelectableAssetIds(bucketsFromCatalog(catalog))
    : listSelectableAssetIds(FALLBACK_ASSET_PICKER);
  const assetId = resolveLabAssetId({
    query: rawAsset,
    catalogDefault: catalog?.default_asset_id,
    allowedIds,
    useStored: false,
  });
  const displayPayload = await fetchDisplayPayload(assetId);

  return (
    <AppShell activeNavId="strategy-lab">
      <StrategyLabContent displayPayload={displayPayload} />
    </AppShell>
  );
}
