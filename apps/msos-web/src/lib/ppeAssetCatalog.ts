/**
 * Read-only PPE asset catalog (metadata only — no prices or curves).
 */

import { PPE_DISPLAY_API_URL } from "@/lib/ppeDisplayPayload";

export const PPE_CATALOG_API_URL = (
  process.env.NEXT_PUBLIC_PPE_CATALOG_API_URL ??
  PPE_DISPLAY_API_URL.replace(/display\.json(\?.*)?$/i, "catalog.json")
).trim();

export const CATALOG_PAYLOAD_KIND = "asset_catalog";

export type CatalogAsset = {
  id: string;
  label: string;
  asset_class?: string;
  venue?: string;
  tier?: string;
  catalog_group?: string;
};

export type CatalogGroup = {
  id: string;
  label: string;
  assets: CatalogAsset[];
};

export type AssetCatalogPayload = {
  kind: string;
  default_asset_id: string;
  groups: CatalogGroup[];
};

export type AssetPickerBuckets = {
  crypto: CatalogAsset[];
  stocks: CatalogAsset[];
};

const CRYPTO_GROUP_ID = "crypto";

const STOCK_GROUP_IDS = new Set(["equity_index", "equity_mega", "commodity_proxy"]);

/** Static fallback when catalog.json is unavailable (matches legacy lab allowlist). */
export const FALLBACK_ASSET_PICKER: AssetPickerBuckets = {
  crypto: [
    { id: "BTC", label: "BTC options", catalog_group: "crypto" },
    { id: "ETH", label: "ETH options", catalog_group: "crypto" },
  ],
  stocks: [{ id: "NVDA", label: "NVDA options", catalog_group: "equity_mega" }],
};

export function isAssetCatalogPayload(value: unknown): value is AssetCatalogPayload {
  if (!value || typeof value !== "object") {
    return false;
  }
  const payload = value as Partial<AssetCatalogPayload>;
  return (
    payload.kind === CATALOG_PAYLOAD_KIND &&
    typeof payload.default_asset_id === "string" &&
    Array.isArray(payload.groups) &&
    payload.groups.length > 0
  );
}

export function partitionCatalogGroups(groups: CatalogGroup[]): AssetPickerBuckets {
  const crypto: CatalogAsset[] = [];
  const stocks: CatalogAsset[] = [];

  for (const group of groups) {
    const assets = group.assets ?? [];
    if (group.id === CRYPTO_GROUP_ID) {
      crypto.push(...assets);
      continue;
    }
    if (STOCK_GROUP_IDS.has(group.id)) {
      stocks.push(...assets);
    }
  }

  return { crypto, stocks };
}

export function bucketsFromCatalog(payload: AssetCatalogPayload): AssetPickerBuckets {
  const partitioned = partitionCatalogGroups(payload.groups);
  return {
    crypto: partitioned.crypto.length > 0 ? partitioned.crypto : FALLBACK_ASSET_PICKER.crypto,
    stocks: partitioned.stocks.length > 0 ? partitioned.stocks : FALLBACK_ASSET_PICKER.stocks,
  };
}

export function listSelectableAssetIds(buckets: AssetPickerBuckets): string[] {
  return [...buckets.crypto, ...buckets.stocks].map((asset) => asset.id.toUpperCase());
}

export function assetBucketForId(
  assetId: string,
  buckets: AssetPickerBuckets,
): "crypto" | "stocks" | null {
  const upper = assetId.toUpperCase();
  if (buckets.crypto.some((asset) => asset.id.toUpperCase() === upper)) {
    return "crypto";
  }
  if (buckets.stocks.some((asset) => asset.id.toUpperCase() === upper)) {
    return "stocks";
  }
  return null;
}

export async function fetchAssetCatalog(): Promise<AssetCatalogPayload | null> {
  return fetchAssetCatalogFromUrl(PPE_CATALOG_API_URL);
}

function resolveCatalogApiFetchUrl(): string {
  const serverUrl = process.env.PPE_DISPLAY_API_SERVER_URL?.trim();
  if (serverUrl) {
    return serverUrl.replace(/display\.json(\?.*)?$/i, "catalog.json");
  }
  return PPE_CATALOG_API_URL;
}

export async function fetchAssetCatalogServer(): Promise<AssetCatalogPayload | null> {
  return fetchAssetCatalogFromUrl(resolveCatalogApiFetchUrl());
}

async function fetchAssetCatalogFromUrl(fetchUrl: string): Promise<AssetCatalogPayload | null> {
  if (!fetchUrl) {
    return null;
  }
  try {
    const res = await fetch(fetchUrl, {
      cache: "no-store",
      headers: {
        Accept: "application/json",
        "User-Agent": "msos-web/1",
      },
    });
    if (!res.ok) {
      return null;
    }
    const data: unknown = await res.json();
    if (!isAssetCatalogPayload(data)) {
      return null;
    }
    return data;
  } catch {
    return null;
  }
}
