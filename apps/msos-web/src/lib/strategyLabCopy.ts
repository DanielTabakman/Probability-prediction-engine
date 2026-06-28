/** Strategy Lab data-mode copy — live vs sample (fixtures). */

import { optionsSourceLabel, type DisplayAssetMeta } from "@/lib/ppeDisplayPayload";

export type LabDataMode = "loading" | "live" | "demo";

export const LAB_DATA_DEMO_PILL = "Sample data · not live";

export function labDataLivePill(asset: DisplayAssetMeta): string {
  return `Live · ${optionsSourceLabel(asset)}`;
}

export const LAB_DATA_LOADING_PILL = "Loading live data…";

export const LAB_DEMO_BANNER_TITLE = "Sample mode — not live market data";

export function labDemoBannerBody(asset: DisplayAssetMeta): string {
  return `The numbers and chart below use placeholder fixtures for layout preview. Refresh the page or check your connection — live ${asset.instrument_label ?? asset.label} load automatically when available.`;
}

export function labLoadingBannerBody(asset: DisplayAssetMeta): string {
  return `Fetching live ${asset.instrument_label ?? asset.label} from ${optionsSourceLabel(asset)}. Metrics and chart will update in a moment.`;
}

export const LAB_THIN_CHAIN_BANNER_TITLE = "Thin options chain";

export function labThinChainBannerBody(asset: DisplayAssetMeta): string {
  return `Options liquidity is limited for ${asset.label}. Implied curves may be approximate — read catalog trust notes below before trading.`;
}

export const LAB_DEGRADED_BANNER_TITLE = "Approximate curve";

export function labDegradedBannerBody(asset: DisplayAssetMeta): string {
  return `Live quotes for ${asset.label} were incomplete or failed quality checks. Treat the purple curve as indicative, not precise.`;
}

export function labLiveBannerBody(asset: DisplayAssetMeta): string {
  return `Spot, range, and curves come from live ${optionsSourceLabel(asset)} for the selected expiry.`;
}
