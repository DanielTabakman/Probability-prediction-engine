const LAB_ASSET_QUERY_PARAM = "asset";

const PUBLIC_DISTRIBUTION_EXPORT_PATH =
  process.env.NEXT_PUBLIC_PPE_DISTRIBUTION_EXPORT_API_URL?.trim() ??
  "/ppe-display-api/distribution-export.csv";

function normalizeAssetId(raw: string | null): string {
  const trimmed = (raw ?? "BTC").trim().toUpperCase();
  return trimmed || "BTC";
}

/** Server-side upstream (Docker internal) or same-origin public path via Caddy. */
export function buildDistributionExportUpstreamUrl(assetId: string): string {
  const asset = normalizeAssetId(assetId);
  const serverUrl = process.env.PPE_DISPLAY_API_SERVER_URL?.trim();
  if (serverUrl) {
    const base = serverUrl.replace(/\/display\.json(\?.*)?$/i, "");
    return `${base}/distribution-export.csv?${LAB_ASSET_QUERY_PARAM}=${encodeURIComponent(asset)}`;
  }
  const separator = PUBLIC_DISTRIBUTION_EXPORT_PATH.includes("?") ? "&" : "?";
  return `${PUBLIC_DISTRIBUTION_EXPORT_PATH}${separator}${LAB_ASSET_QUERY_PARAM}=${encodeURIComponent(asset)}`;
}

export { LAB_ASSET_QUERY_PARAM, normalizeAssetId };
