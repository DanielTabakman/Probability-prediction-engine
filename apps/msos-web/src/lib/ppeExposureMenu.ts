/**
 * PPE exposure menu boundary — display/proxy only (path ranking math in Python).
 */

export const PPE_EXPOSURE_MENU_API_URL = (
  process.env.NEXT_PUBLIC_PPE_EXPOSURE_MENU_API_URL ?? "/ppe-display-api/exposure-menu.json"
).trim();

export const EXPOSURE_ASSET_QUERY_PARAM = "asset";
export const EXPOSURE_DIRECTION_QUERY_PARAM = "direction";
export const EXPOSURE_HORIZON_QUERY_PARAM = "horizon";

export const EXPOSURE_PROOF_ASSETS = ["NVDA", "BTC"] as const;
export type ExposureProofAssetId = (typeof EXPOSURE_PROOF_ASSETS)[number];

export type ExposureDirection = "long" | "short" | "neutral";
export type HorizonChip = "any" | "3m" | "12m";
export type InstrumentRail = "spot_equity" | "listed_options" | "etf_proxy" | "perp";
export type TrustBadge = "Live" | "Thin chain" | "Planned";

export type ExposurePathRecord = {
  path_id: string;
  instrument_rail: InstrumentRail;
  label: string;
  direction: ExposureDirection;
  headline: string;
  capital_shape: string;
  leverage: "none" | "defined" | "high";
  time_bound: "none" | "dated";
  liquidity: "high" | "medium" | "low" | "planned";
  trust_badge: TrustBadge;
  pros: string[];
  cons: string[];
  recommendation_status: string;
  cost_hint_usd?: number;
  legs?: Array<Record<string, string>>;
  deep_link?: string;
};

export type ExposureMenuPayload = {
  kind: "exposure_paths";
  asset_id: string;
  direction: ExposureDirection;
  horizon: HorizonChip;
  status: string;
  live_path_count: number;
  paths: ExposurePathRecord[];
  recommendation_status: string;
  footer_copy: string;
  as_of_utc?: string;
  spot_usd?: number | null;
  proof_asset?: boolean;
};

export const DEFAULT_EXPOSURE_ASSET_ID: ExposureProofAssetId = "NVDA";
export const DEFAULT_EXPOSURE_DIRECTION: ExposureDirection = "long";
export const DEFAULT_EXPOSURE_HORIZON: HorizonChip = "any";

const ASSET_PATTERN = /^[A-Z][A-Z0-9._-]{0,11}$/;

export function normalizeExposureAssetId(
  value: string | null | undefined,
  fallback: ExposureProofAssetId = DEFAULT_EXPOSURE_ASSET_ID,
): ExposureProofAssetId {
  const upper = (value ?? "").trim().toUpperCase();
  if (!upper || !ASSET_PATTERN.test(upper)) {
    return fallback;
  }
  const proof = EXPOSURE_PROOF_ASSETS as readonly string[];
  return proof.includes(upper) ? (upper as ExposureProofAssetId) : fallback;
}

export function normalizeExposureDirection(
  value: string | null | undefined,
  fallback: ExposureDirection = DEFAULT_EXPOSURE_DIRECTION,
): ExposureDirection {
  const key = (value ?? "").trim().toLowerCase();
  if (key === "long" || key === "short" || key === "neutral") {
    return key;
  }
  return fallback;
}

export function normalizeExposureHorizon(
  value: string | null | undefined,
  fallback: HorizonChip = DEFAULT_EXPOSURE_HORIZON,
): HorizonChip {
  const key = (value ?? "").trim().toLowerCase();
  if (key === "any" || key === "3m" || key === "12m") {
    return key;
  }
  return fallback;
}

export function railDisplayLabel(rail: InstrumentRail): string {
  switch (rail) {
    case "spot_equity":
      return "Spot";
    case "listed_options":
      return "Options";
    case "etf_proxy":
      return "ETF proxy";
    case "perp":
      return "Perp";
    default:
      return rail;
  }
}

export function trustBadgeTone(badge: TrustBadge): string {
  if (badge === "Live") return "teal";
  if (badge === "Thin chain") return "amber";
  return "muted";
}

export function buildExposureMenuFetchUrl(
  assetId: string,
  direction: ExposureDirection,
  horizon: HorizonChip,
  baseUrl = PPE_EXPOSURE_MENU_API_URL,
): string {
  const params = new URLSearchParams({
    [EXPOSURE_ASSET_QUERY_PARAM]: assetId.trim().toUpperCase(),
    [EXPOSURE_DIRECTION_QUERY_PARAM]: direction,
    [EXPOSURE_HORIZON_QUERY_PARAM]: horizon,
  });
  const separator = baseUrl.includes("?") ? "&" : "?";
  return `${baseUrl}${separator}${params.toString()}`;
}

export function buildExposurePagePath(
  assetId: string,
  direction: ExposureDirection,
  horizon: HorizonChip,
): string {
  const params = new URLSearchParams({
    [EXPOSURE_ASSET_QUERY_PARAM]: assetId.trim().toUpperCase(),
    [EXPOSURE_DIRECTION_QUERY_PARAM]: direction,
    [EXPOSURE_HORIZON_QUERY_PARAM]: horizon,
  });
  return `/exposure?${params.toString()}`;
}

export function isExposureMenuPayload(value: unknown): value is ExposureMenuPayload {
  if (!value || typeof value !== "object") {
    return false;
  }
  const payload = value as Partial<ExposureMenuPayload>;
  return payload.kind === "exposure_paths" && Array.isArray(payload.paths);
}

function resolveExposureApiFetchUrl(
  assetId: string,
  direction: ExposureDirection,
  horizon: HorizonChip,
): string {
  const serverUrl = process.env.PPE_EXPOSURE_MENU_API_SERVER_URL?.trim();
  if (serverUrl) {
    return buildExposureMenuFetchUrl(assetId, direction, horizon, serverUrl);
  }
  return buildExposureMenuFetchUrl(assetId, direction, horizon);
}

export async function fetchExposureMenuFromUrl(
  fetchUrl: string,
): Promise<ExposureMenuPayload | null> {
  if (!fetchUrl) {
    return null;
  }
  try {
    const res = await fetch(fetchUrl, {
      cache: "no-store",
      headers: { Accept: "application/json", "User-Agent": "msos-web/1" },
      signal: AbortSignal.timeout(120_000),
    });
    if (!res.ok) {
      return null;
    }
    const data: unknown = await res.json();
    return isExposureMenuPayload(data) ? data : null;
  } catch {
    return null;
  }
}

export async function fetchExposureMenu(
  assetId: string,
  direction: ExposureDirection,
  horizon: HorizonChip,
): Promise<ExposureMenuPayload | null> {
  return fetchExposureMenuFromUrl(resolveExposureApiFetchUrl(assetId, direction, horizon));
}

export async function fetchExposureMenuClient(
  assetId: string,
  direction: ExposureDirection,
  horizon: HorizonChip,
): Promise<ExposureMenuPayload | null> {
  return fetchExposureMenuFromUrl(buildExposureMenuFetchUrl(assetId, direction, horizon));
}
