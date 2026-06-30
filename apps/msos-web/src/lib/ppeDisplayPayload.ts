/**
 * Read-only PPE display payload (pre-computed in Python). No distribution math here.
 */

import type { CurveDisplayLabels } from "@/lib/chartCurveLabels";
import { formatMoney } from "@/lib/displayCurrency";

export const PPE_DISPLAY_API_URL = (
  process.env.NEXT_PUBLIC_PPE_DISPLAY_API_URL ?? "/ppe-display-api/display.json"
).trim();

/** Cold equity chains can take 30–120s; keep MSOS in Loading until then. */
export const DISPLAY_PAYLOAD_FETCH_TIMEOUT_MS = 120_000;

function resolveDisplayFetchSignal(): AbortSignal | undefined {
  const timeoutMs = DISPLAY_PAYLOAD_FETCH_TIMEOUT_MS;
  if (typeof AbortSignal !== "undefined" && typeof AbortSignal.timeout === "function") {
    return AbortSignal.timeout(timeoutMs);
  }
  if (typeof AbortController === "undefined") {
    return undefined;
  }
  const controller = new AbortController();
  globalThis.setTimeout(() => controller.abort(), timeoutMs);
  return controller.signal;
}

export const PPE_EMBED_ONLY_PARAM = "embed_only";

export const PPE_EMBED_URL = (process.env.NEXT_PUBLIC_PPE_EMBED_URL ?? "").trim();

export const LAB_ASSET_QUERY_PARAM = "asset";

/** System-wide default asset when registry/catalog/session provide nothing else. */
export const SYSTEM_DEFAULT_ASSET_ID = "ETH";

/** Registry / bare display API default — matches config/assets.yaml. */
export const REGISTRY_DEFAULT_ASSET_ID = SYSTEM_DEFAULT_ASSET_ID;

/** @deprecated Prefer `resolveLabAssetId` / `ABSOLUTE_FALLBACK_ASSET_ID` for UI defaults. */
export const DEFAULT_LAB_ASSET_ID = REGISTRY_DEFAULT_ASSET_ID;

/** Known assets for static copy fallbacks — not a runtime allowlist gate. */
export const KNOWN_LAB_ASSET_IDS = ["BTC", "ETH", "NVDA"] as const;

export type KnownLabAssetId = (typeof KNOWN_LAB_ASSET_IDS)[number];

/** Catalog-driven asset id (see ppeAssetCatalog.ts for selectable set). */
export type LabAssetId = string;

const LAB_ASSET_ID_PATTERN = /^[A-Z][A-Z0-9._-]{0,11}$/;

export type DisplayAssetMeta = {
  id: string;
  label: string;
  price_axis_label?: string;
  instrument_label?: string;
};

const LAB_ASSET_FALLBACKS: Record<KnownLabAssetId, DisplayAssetMeta> = {
  BTC: {
    id: "BTC",
    label: "BTC options",
    price_axis_label: "BTC price at expiry",
    instrument_label: "BTC options",
  },
  ETH: {
    id: "ETH",
    label: "ETH options",
    price_axis_label: "ETH price at expiry",
    instrument_label: "ETH options",
  },
  NVDA: {
    id: "NVDA",
    label: "NVDA options",
    price_axis_label: "NVDA price at expiry",
    instrument_label: "NVDA options",
  },
};

export function normalizeLabAssetId(
  value: string | null | undefined,
  allowedIds?: readonly string[],
  fallback: LabAssetId = REGISTRY_DEFAULT_ASSET_ID,
): LabAssetId {
  const upper = (value ?? "").trim().toUpperCase();
  if (!upper || !LAB_ASSET_ID_PATTERN.test(upper)) {
    return fallback;
  }
  if (allowedIds && allowedIds.length > 0) {
    const allowed = new Set(allowedIds.map((id) => id.toUpperCase()));
    return allowed.has(upper) ? upper : fallback;
  }
  return upper;
}

/** Venue name for trader-facing copy (display only — not routing). */
export function optionsVenueReferenceLabel(asset: DisplayAssetMeta): string {
  const id = asset.id.toUpperCase();
  if (id === "NVDA") {
    return "equity options chain";
  }
  if (id === "SOL") {
    return "Bybit";
  }
  return "Deribit";
}

/** Human label for where option quotes come from (display copy only). */
export function optionsSourceLabel(asset: DisplayAssetMeta): string {
  const venue = optionsVenueReferenceLabel(asset);
  return venue === "equity options chain" ? venue : `${venue} options`;
}

/** Trust strip label for confirm / thesis draft (display only). */
export function optionsTrustSourceLabel(asset: DisplayAssetMeta): string {
  if (asset.id.toUpperCase() === "NVDA") {
    return "Caution · dividends unmodelled";
  }
  return `Good · ${optionsVenueReferenceLabel(asset)}`;
}

/** True when a live payload matches the asset the user selected in the lab. */
export function isPayloadForSelectedAsset(
  payload: DisplayPayload | null | undefined,
  assetId: LabAssetId,
): boolean {
  const payloadAssetId = payload?.asset?.id?.toUpperCase();
  if (!payloadAssetId) {
    return false;
  }
  return payloadAssetId === assetId.toUpperCase();
}

function fallbackMetaForAsset(assetId: string): DisplayAssetMeta {
  const known = LAB_ASSET_FALLBACKS[assetId as KnownLabAssetId];
  if (known) {
    return known;
  }
  return {
    id: assetId,
    label: `${assetId} options`,
    price_axis_label: `${assetId} price at expiry`,
    instrument_label: `${assetId} options`,
  };
}

export function resolveDisplayAssetMeta(
  payload: DisplayPayload | null | undefined,
  assetId: LabAssetId = DEFAULT_LAB_ASSET_ID,
): DisplayAssetMeta {
  const payloadAsset = payload?.asset;
  const normalizedId = assetId.toUpperCase();
  if (payloadAsset?.id && payloadAsset.id.toUpperCase() === normalizedId) {
    const fallback = fallbackMetaForAsset(normalizedId);
    return {
      ...fallback,
      ...payloadAsset,
      id: normalizedId,
      label: payloadAsset.label || fallback.label,
    };
  }
  return fallbackMetaForAsset(normalizedId);
}

export function buildStrategyLabPath(assetId: LabAssetId): string {
  const normalized = assetId.trim().toUpperCase();
  if (!normalized) {
    return "/strategy-lab";
  }
  return `/strategy-lab?${LAB_ASSET_QUERY_PARAM}=${encodeURIComponent(normalized)}`;
}

export function buildDisplayApiUrl(assetId: LabAssetId): string {
  const base = PPE_DISPLAY_API_URL;
  const normalized = assetId.trim().toUpperCase();
  if (!normalized || normalized === REGISTRY_DEFAULT_ASSET_ID) {
    return base;
  }
  const separator = base.includes("?") ? "&" : "?";
  return `${base}${separator}${LAB_ASSET_QUERY_PARAM}=${encodeURIComponent(normalized)}`;
}

export type DisplaySeries = {
  expiry_date: string;
  prices_usd: number[];
  pdf_pct: number[];
  mean_usd?: number;
  quartiles_usd?: {
    q1_usd: number;
    median_usd: number;
    q3_usd: number;
  };
  belief_presets?: Partial<Record<string, BeliefPresetOverlay>>;
  curve_labels?: CurveDisplayLabels;
};

export type DisplaySummaryRow = Record<string, string>;

export type BeliefPresetOverlay = {
  pdf_pct: number[];
  forward_usd?: number;
  atm_iv_annual?: number;
};

export type DisplayPayload = {
  kind: string;
  spot_usd: number;
  as_of_utc?: string;
  trust_state?: string;
  series_by_expiry: DisplaySeries[];
  belief_presets?: Partial<Record<string, BeliefPresetOverlay>>;
  summary?: {
    table_rows?: DisplaySummaryRow[];
  };
  curve_labels?: CurveDisplayLabels;
  asset?: DisplayAssetMeta;
  meta?: {
    trust_state?: string;
    display_depth?: string;
    read_only?: boolean;
  };
};

export type LabMetric = {
  label: string;
  value: string;
  tone?: "teal" | "amber";
};

export type LabOutcomeSummary = {
  tag: string;
  tagTone: "teal" | "amber";
  delta: string;
  headline: string;
  body: string;
  scores: { label: string; value: string; tone: "teal" | "amber" }[];
};

function isNumberArray(value: unknown): value is number[] {
  return Array.isArray(value) && value.length > 1 && value.every((item) => typeof item === "number");
}

export function isDisplaySeries(value: unknown): value is DisplaySeries {
  if (!value || typeof value !== "object") {
    return false;
  }
  const series = value as Partial<DisplaySeries>;
  return (
    typeof series.expiry_date === "string" &&
    isNumberArray(series.prices_usd) &&
    isNumberArray(series.pdf_pct) &&
    series.prices_usd.length === series.pdf_pct.length
  );
}

export function isDisplayPayload(value: unknown): value is DisplayPayload {
  if (!value || typeof value !== "object") {
    return false;
  }
  const payload = value as Partial<DisplayPayload>;
  return (
    payload.kind === "distribution_display_boundary" &&
    typeof payload.spot_usd === "number" &&
    Array.isArray(payload.series_by_expiry) &&
    payload.series_by_expiry.some(isDisplaySeries)
  );
}

/** USD-only formatting — prefer formatMoney(usd, currency) at UI boundaries. */
export function formatUsd(value: number): string {
  return formatMoney(value, "USD");
}

export type MoneyFormatter = (usd: number) => string;

function resolveMoneyFormatter(formatter?: MoneyFormatter): MoneyFormatter {
  return formatter ?? formatUsd;
}

function primaryLognormalRow(payload: DisplayPayload): DisplaySummaryRow | undefined {
  const rows = payload.summary?.table_rows ?? [];
  return rows.find((row) => {
    const method = (row.Method ?? row.method ?? "").toLowerCase();
    return method.includes("lognormal") || method.includes("reference");
  });
}

export function listExpiryDates(payload: DisplayPayload): string[] {
  return payload.series_by_expiry.filter(isDisplaySeries).map((series) => series.expiry_date);
}

export function findSeriesByExpiry(
  payload: DisplayPayload,
  expiryDate: string,
): DisplaySeries | undefined {
  return payload.series_by_expiry.find(
    (series) => isDisplaySeries(series) && series.expiry_date === expiryDate,
  );
}

function summaryRowForExpiry(
  payload: DisplayPayload,
  expiryDate: string,
): DisplaySummaryRow | undefined {
  const rows = payload.summary?.table_rows ?? [];
  return rows.find((row) => {
    const method = (row.Method ?? row.method ?? "").toLowerCase();
    const expiry = row.Expiry ?? row.expiry_date ?? row.expiry ?? "";
    const isLognormal = method.includes("lognormal") || method.includes("reference");
    return isLognormal && String(expiry).startsWith(expiryDate.slice(0, 10));
  });
}

export function buildLabMetricsFromPayload(
  payload: DisplayPayload,
  expiryDate?: string,
  formatUsdAmount: MoneyFormatter = formatUsd,
  assetMeta?: DisplayAssetMeta,
): LabMetric[] {
  const fmt = resolveMoneyFormatter(formatUsdAmount);
  const asset = assetMeta ?? resolveDisplayAssetMeta(payload);
  const spotLabel = `Today's ${asset.id}`;
  const dates = listExpiryDates(payload);
  const resolvedExpiry = expiryDate && dates.includes(expiryDate) ? expiryDate : dates[0];
  const primary = resolvedExpiry ? findSeriesByExpiry(payload, resolvedExpiry) : undefined;
  const lognormal = resolvedExpiry ? summaryRowForExpiry(payload, resolvedExpiry) : primaryLognormalRow(payload);
  const marketWidth = lognormal?.["Implied range width (IQR)"] ?? "—";
  const median = lognormal?.["Median terminal price (50th %)"] ?? "—";
  const medianFromSeries = primary?.quartiles_usd?.median_usd ?? primary?.mean_usd;

  return [
    { label: "Expiry", value: primary?.expiry_date ?? resolvedExpiry ?? "—" },
    { label: spotLabel, value: fmt(payload.spot_usd) },
    {
      label: "Market best guess",
      value:
        typeof medianFromSeries === "number"
          ? fmt(medianFromSeries)
          : median,
      tone: "teal",
    },
    { label: "Typical range", value: marketWidth, tone: "amber" },
    {
      label: "Data",
      value:
        asset.id === "NVDA"
          ? "Live · equity chain"
          : `Live · ${optionsVenueReferenceLabel(asset)}`,
      tone: "teal",
    },
  ];
}

export function buildOutcomeFromPayload(
  payload: DisplayPayload,
  expiryDate?: string,
  formatUsdAmount: MoneyFormatter = formatUsd,
  assetMeta?: DisplayAssetMeta,
): LabOutcomeSummary {
  const fmt = resolveMoneyFormatter(formatUsdAmount);
  const asset = assetMeta ?? resolveDisplayAssetMeta(payload);
  const instrument = asset.instrument_label ?? asset.label;
  const spotLabel = `Today's ${asset.id}`;
  const dates = listExpiryDates(payload);
  const resolvedExpiry = expiryDate && dates.includes(expiryDate) ? expiryDate : dates[0];
  const lognormal = resolvedExpiry
    ? summaryRowForExpiry(payload, resolvedExpiry)
    : primaryLognormalRow(payload);
  const series = resolvedExpiry ? findSeriesByExpiry(payload, resolvedExpiry) : undefined;
  const marketWidth = lognormal?.["Implied range width (IQR)"] ?? "the range options imply";
  const medianUsd = series?.quartiles_usd?.median_usd;
  const medianLabel =
    typeof medianUsd === "number"
      ? fmt(medianUsd)
      : lognormal?.["Median terminal price (50th %)"] ?? lognormal?.["Risk-neutral mean"] ?? "—";

  return {
    tag: "Live market",
    tagTone: "teal",
    delta: "—",
    headline: `Here's what ${instrument} are pricing for your date.`,
    body: `For ${resolvedExpiry ?? "this expiry"}, the market's best guess is around ${medianLabel} and the middle-50% range is ${marketWidth}. Pick a view above to compare yours to the purple curve — then confirm when you're ready to plan a trade.`,
    scores: [
      { label: spotLabel, value: fmt(payload.spot_usd), tone: "amber" },
      { label: "Market guess", value: medianLabel, tone: "teal" },
      { label: "Your view", value: "Pick above", tone: "teal" },
      { label: "Next step", value: "Confirm", tone: "teal" },
    ],
  };
}

/** Short-lived client cache so homepage prefetch shares results with Strategy Lab. */
const DISPLAY_PAYLOAD_CACHE_TTL_MS = 45_000;

type DisplayPayloadCacheEntry = {
  at: number;
  value: DisplayPayload | null;
};

const displayPayloadCache = new Map<string, DisplayPayloadCacheEntry>();
const displayPayloadInFlight = new Map<string, Promise<DisplayPayload | null>>();

async function fetchDisplayPayloadFromNetwork(fetchUrl: string): Promise<DisplayPayload | null> {
  try {
    const res = await fetch(fetchUrl, {
      cache: "no-store",
      headers: {
        Accept: "application/json",
        "User-Agent": "msos-web/1",
      },
      signal: resolveDisplayFetchSignal(),
    });
    if (!res.ok) {
      return null;
    }
    const data: unknown = await res.json();
    if (!isDisplayPayload(data)) {
      return null;
    }
    return data;
  } catch {
    return null;
  }
}

export async function fetchDisplayPayloadFromUrl(fetchUrl: string): Promise<DisplayPayload | null> {
  if (!fetchUrl) {
    return null;
  }

  const cached = displayPayloadCache.get(fetchUrl);
  if (cached && Date.now() - cached.at < DISPLAY_PAYLOAD_CACHE_TTL_MS) {
    return cached.value;
  }

  let pending = displayPayloadInFlight.get(fetchUrl);
  if (!pending) {
    pending = fetchDisplayPayloadFromNetwork(fetchUrl);
    displayPayloadInFlight.set(fetchUrl, pending);
  }

  try {
    const value = await pending;
    displayPayloadCache.set(fetchUrl, { at: Date.now(), value });
    return value;
  } finally {
    displayPayloadInFlight.delete(fetchUrl);
  }
}

/** Browser / public-path fetch (relative display API). */
export async function fetchDisplayPayloadClient(
  assetId: LabAssetId = DEFAULT_LAB_ASSET_ID,
): Promise<DisplayPayload | null> {
  return fetchDisplayPayloadFromUrl(buildDisplayApiUrl(assetId));
}

/** Server-side fetch target (Docker internal); browser uses public relative path. */
function resolveDisplayApiFetchUrl(): string {
  const serverUrl = process.env.PPE_DISPLAY_API_SERVER_URL?.trim();
  if (serverUrl) {
    return serverUrl;
  }
  return PPE_DISPLAY_API_URL;
}

export async function fetchDisplayPayload(
  assetId: LabAssetId = DEFAULT_LAB_ASSET_ID,
): Promise<DisplayPayload | null> {
  const serverUrl = resolveDisplayApiFetchUrl();
  const fetchUrl =
    assetId === DEFAULT_LAB_ASSET_ID
      ? serverUrl
      : `${serverUrl}${serverUrl.includes("?") ? "&" : "?"}${LAB_ASSET_QUERY_PARAM}=${encodeURIComponent(assetId)}`;
  return fetchDisplayPayloadFromUrl(fetchUrl);
}
