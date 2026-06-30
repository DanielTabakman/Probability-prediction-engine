import { fetchAssetCatalog } from "@/lib/ppeAssetCatalog";
import {
  buildDisplayApiUrl,
  DEFAULT_LAB_ASSET_ID,
  fetchDisplayPayloadFromUrl,
  type LabAssetId,
} from "@/lib/ppeDisplayPayload";
import { PLATFORM_TOUR_DEFAULT_ASSET, strategyLabForcedTourHref } from "@/lib/platformTutorial";

type PrefetchRouter = {
  prefetch: (href: string) => void;
};

let warmInFlight: Promise<void> | null = null;

/** Warm catalog + default display payload so Strategy Lab hydrates faster. */
export async function warmStrategyLabData(assetId: LabAssetId = DEFAULT_LAB_ASSET_ID): Promise<void> {
  await Promise.allSettled([
    fetchAssetCatalog(),
    fetchDisplayPayloadFromUrl(buildDisplayApiUrl(assetId)),
  ]);
}

/** Prefetch route + warm API payloads (deduped). */
export function warmStrategyLabEntry(
  router?: PrefetchRouter,
  tourHref: string = strategyLabForcedTourHref(),
  assetId: LabAssetId = PLATFORM_TOUR_DEFAULT_ASSET,
): void {
  router?.prefetch(tourHref);

  if (warmInFlight) {
    return;
  }

  warmInFlight = warmStrategyLabData(assetId).finally(() => {
    warmInFlight = null;
  });
}

/** Homepage prefetch — route + lab data warm immediately on mount. */
export function scheduleStrategyLabTourPrefetch(router: PrefetchRouter): () => void {
  const tourHref = strategyLabForcedTourHref();
  warmStrategyLabEntry(router, tourHref);
  return () => {};
}
