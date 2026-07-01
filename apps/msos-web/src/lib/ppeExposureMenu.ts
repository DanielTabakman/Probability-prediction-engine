/**
 * PPE exposure menu boundary — display/proxy only (path ranking math in Python).
 * Asset picker uses catalog.json (registry SSOT) — see ppeAssetCatalog.ts.
 */

import { normalizeCatalogAssetId, type AssetCatalogPayload } from "@/lib/ppeAssetCatalog";
import { REGISTRY_DEFAULT_ASSET_ID } from "@/lib/ppeDisplayPayload";

export const PPE_EXPOSURE_MENU_API_URL = (
  process.env.NEXT_PUBLIC_PPE_EXPOSURE_MENU_API_URL ?? "/ppe-display-api/exposure-menu.json"
).trim();

export const EXPOSURE_ASSET_QUERY_PARAM = "asset";
export const EXPOSURE_DIRECTION_QUERY_PARAM = "direction";
export const EXPOSURE_HORIZON_QUERY_PARAM = "horizon";

export type ExposureDirection = "long" | "short" | "neutral";
export type HorizonChip = "any" | "3m" | "12m";
export type InstrumentRail = "spot_equity" | "listed_options" | "etf_proxy" | "perp";
export type TrustBadge = "Live" | "Thin chain" | "Planned";

export type FitLensId =
  | "simplest"
  | "defined_risk"
  | "capital_light"
  | "upside_leverage"
  | "patient"
  | "liquid"
  | "income_style";

export type ExposureSectionRecord = {
  section_key: string;
  title: string;
  subcopy: string;
  path_ids: string[];
};

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
  sort_group: string;
  fit_lenses?: FitLensId[];
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
  planned_path_count?: number;
  paths: ExposurePathRecord[];
  sections?: ExposureSectionRecord[];
  recommendation_status: string;
  footer_copy: string;
  as_of_utc?: string;
  spot_usd?: number | null;
  proof_asset?: boolean;
};

export const FIT_LENS_CATALOG: {
  id: FitLensId;
  label: string;
  shortLabel: string;
  direction?: ExposureDirection;
}[] = [
  { id: "simplest", label: "Simplest", shortLabel: "Simplest" },
  { id: "defined_risk", label: "Defined max loss", shortLabel: "Defined risk" },
  { id: "capital_light", label: "Light capital", shortLabel: "Light capital" },
  { id: "upside_leverage", label: "Upside leverage", shortLabel: "Upside leverage" },
  { id: "patient", label: "Patient horizon", shortLabel: "Patient" },
  { id: "liquid", label: "Most liquid", shortLabel: "Liquid" },
  {
    id: "income_style",
    label: "Income-style",
    shortLabel: "Income-style",
    direction: "short",
  },
];

export const DEFAULT_EXPOSURE_ASSET_ID = REGISTRY_DEFAULT_ASSET_ID;
export const DEFAULT_EXPOSURE_DIRECTION: ExposureDirection = "long";
export const DEFAULT_EXPOSURE_HORIZON: HorizonChip = "any";

/** Normalize ?asset= against enabled catalog ids (registry SSOT). */
export function normalizeExposureAssetId(
  value: string | null | undefined,
  catalog: AssetCatalogPayload | null,
  fallback: string = DEFAULT_EXPOSURE_ASSET_ID,
): string {
  return normalizeCatalogAssetId(value, catalog, fallback);
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

export function fitLensLabel(id: FitLensId): string {
  return FIT_LENS_CATALOG.find((row) => row.id === id)?.label ?? id;
}

export function leverageChipLabel(leverage: ExposurePathRecord["leverage"]): string {
  if (leverage === "none") return "No leverage";
  if (leverage === "defined") return "Defined leverage";
  return "High leverage";
}

export function timeBoundChipLabel(timeBound: ExposurePathRecord["time_bound"]): string {
  return timeBound === "dated" ? "Dated" : "No expiry";
}

export function liquidityChipLabel(liquidity: ExposurePathRecord["liquidity"]): string {
  if (liquidity === "high") return "High liquidity";
  if (liquidity === "medium") return "Medium liquidity";
  if (liquidity === "low") return "Low liquidity";
  return "Planned liquidity";
}

export function formatLegsOneLine(legs: ExposurePathRecord["legs"]): string {
  if (!legs?.length) {
    return "—";
  }
  return legs
    .map((leg) => {
      const side = leg.side ?? "";
      const strike = leg.strike ?? "";
      const tenor = leg.tenor ?? "";
      return `${side} ${strike}${tenor ? ` · ${tenor}` : ""}`.trim();
    })
    .join(" · ");
}

export function fitLensOptionsForDirection(direction: ExposureDirection): typeof FIT_LENS_CATALOG {
  return FIT_LENS_CATALOG.filter((row) => !row.direction || row.direction === direction);
}

export function resolveExposureSections(payload: ExposureMenuPayload): ExposureSectionRecord[] {
  if (payload.sections?.length) {
    return payload.sections;
  }
  const byKey = new Map<string, string[]>();
  const order: string[] = [];
  for (const path of payload.paths) {
    const key = path.sort_group || path.path_id;
    if (!byKey.has(key)) {
      byKey.set(key, []);
      order.push(key);
    }
    byKey.get(key)!.push(path.path_id);
  }
  return order.map((key) => ({
    section_key: key,
    title: key.replace(/_/g, " "),
    subcopy: "",
    path_ids: byKey.get(key) ?? [],
  }));
}

export function pathMatchesFitLens(path: ExposurePathRecord, lensId: FitLensId | null): boolean {
  if (!lensId) {
    return true;
  }
  return (path.fit_lenses ?? []).includes(lensId);
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
