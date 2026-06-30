import { fetchAssetCatalog } from "@/lib/ppeAssetCatalog";
import {
  buildDisplayApiUrl,
  DEFAULT_LAB_ASSET_ID,
  fetchDisplayPayloadFromUrl,
  type LabAssetId,
} from "@/lib/ppeDisplayPayload";
import { strategyLabForcedTourHref } from "@/lib/platformTutorial";

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
  assetId: LabAssetId = DEFAULT_LAB_ASSET_ID,
): void {
  router?.prefetch(tourHref);

  if (warmInFlight) {
    return;
  }

  warmInFlight = warmStrategyLabData(assetId).finally(() => {
    warmInFlight = null;
  });
}

/** Idle prefetch for homepage — tour route + default lab data. */
export function scheduleStrategyLabTourPrefetch(router: PrefetchRouter): () => void {
  const tourHref = strategyLabForcedTourHref();
  const run = () => warmStrategyLabEntry(router, tourHref);

  if (typeof window.requestIdleCallback === "function") {
    const id = window.requestIdleCallback(run, { timeout: 2500 });
    return () => window.cancelIdleCallback(id);
  }

  const id = window.setTimeout(run, 600);
  return () => window.clearTimeout(id);
}
