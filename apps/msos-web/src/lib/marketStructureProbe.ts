const LATEST_PATH = "/v1/structure/latest";
const DEFAULT_SOURCE = "ndax";
const SCHEMA_VERSION = "market-structure.v1" as const;
const ENGINE_STATUSES = ["OK", "NO_DATA", "ERROR"] as const;
const SCALE_FITS = ["INSUFFICIENT", "POOR", "MARGINAL", "USABLE"] as const;

export type MarketStructureFit = (typeof SCALE_FITS)[number];
export type MarketStructureEngineStatus = (typeof ENGINE_STATUSES)[number];

export type MarketStructureZone = {
  center: number;
  kind: string;
  touches: number;
  distance_pct?: number | null;
  strength: string;
};

export type MarketStructureScale = {
  scale: string;
  fit: MarketStructureFit;
  fit_reason?: string | null;
  observations?: number | null;
  range_bps?: number | null;
  median_spread_bps?: number | null;
  spread_to_range_ratio?: number | null;
  max_gap_seconds?: number | null;
  last_price?: number | null;
  zone_half_width?: number | null;
  zones: MarketStructureZone[];
};

export type MarketStructurePersistentLevel = {
  center: number;
  scales: string[];
  persistence: number;
  kind: string;
  touches_total: number;
  strength: string;
};

export type MarketStructureV1 = {
  schema_version: typeof SCHEMA_VERSION;
  generated_at: string;
  status: MarketStructureEngineStatus;
  source: string;
  instrument?: string | null;
  currency?: string | null;
  method?: string | null;
  index_files_considered?: number | null;
  scales: MarketStructureScale[];
  persistent_levels: MarketStructurePersistentLevel[];
};

export type MarketStructureProbeState = {
  status: MarketStructureEngineStatus | "UNAVAILABLE" | "NOT CONFIGURED";
  detail: string;
  payload: MarketStructureV1 | null;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asFiniteNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function asInteger(value: unknown): number | null {
  const parsed = asFiniteNumber(value);
  return parsed === null ? null : Math.trunc(parsed);
}

function asString(value: unknown): string | null {
  return typeof value === "string" && value.trim() ? value : null;
}

function parseZone(value: unknown): MarketStructureZone | null {
  if (!isRecord(value)) return null;
  const center = asFiniteNumber(value.center);
  const kind = asString(value.kind);
  const touches = asInteger(value.touches);
  const strength = asString(value.strength);
  if (center === null || !kind || touches === null || touches < 1 || !strength) return null;
  return {
    center,
    kind,
    touches,
    distance_pct: asFiniteNumber(value.distance_pct),
    strength,
  };
}

function parseScale(value: unknown): MarketStructureScale | null {
  if (!isRecord(value)) return null;
  const scale = asString(value.scale);
  const fit = asString(value.fit);
  if (!scale || !fit || !SCALE_FITS.includes(fit as MarketStructureFit)) return null;
  const zones = Array.isArray(value.zones) ? value.zones.map(parseZone).filter((zone): zone is MarketStructureZone => zone !== null) : [];
  return {
    scale,
    fit: fit as MarketStructureFit,
    fit_reason: asString(value.fit_reason),
    observations: asInteger(value.observations),
    range_bps: asFiniteNumber(value.range_bps),
    median_spread_bps: asFiniteNumber(value.median_spread_bps),
    spread_to_range_ratio: asFiniteNumber(value.spread_to_range_ratio),
    max_gap_seconds: asFiniteNumber(value.max_gap_seconds),
    last_price: asFiniteNumber(value.last_price),
    zone_half_width: asFiniteNumber(value.zone_half_width),
    zones,
  };
}

function parsePersistentLevel(value: unknown): MarketStructurePersistentLevel | null {
  if (!isRecord(value)) return null;
  const center = asFiniteNumber(value.center);
  const kind = asString(value.kind);
  const persistence = asInteger(value.persistence);
  const touchesTotal = asInteger(value.touches_total);
  const strength = asString(value.strength);
  const scales = Array.isArray(value.scales)
    ? value.scales.filter((item): item is string => typeof item === "string" && item.length > 0)
    : [];
  if (center === null || !kind || persistence === null || persistence < 1 || touchesTotal === null || touchesTotal < 1 || !strength) {
    return null;
  }
  return {
    center,
    scales,
    persistence,
    kind,
    touches_total: touchesTotal,
    strength,
  };
}

export function parseMarketStructureV1(raw: unknown): MarketStructureV1 | null {
  if (!isRecord(raw)) return null;
  if (raw.schema_version !== SCHEMA_VERSION) return null;
  const generatedAt = asString(raw.generated_at);
  const status = asString(raw.status);
  const source = asString(raw.source);
  if (!generatedAt || !status || !ENGINE_STATUSES.includes(status as MarketStructureEngineStatus) || !source) {
    return null;
  }
  if (!Array.isArray(raw.scales) || !Array.isArray(raw.persistent_levels)) return null;
  const scales = raw.scales.map(parseScale).filter((scale): scale is MarketStructureScale => scale !== null);
  if (scales.length !== raw.scales.length) return null;
  const persistentLevels = raw.persistent_levels
    .map(parsePersistentLevel)
    .filter((level): level is MarketStructurePersistentLevel => level !== null);
  if (persistentLevels.length !== raw.persistent_levels.length) return null;
  return {
    schema_version: SCHEMA_VERSION,
    generated_at: generatedAt,
    status: status as MarketStructureEngineStatus,
    source,
    instrument: asString(raw.instrument),
    currency: asString(raw.currency),
    method: asString(raw.method),
    index_files_considered: asInteger(raw.index_files_considered),
    scales,
    persistent_levels: persistentLevels,
  };
}

export function resolveMarketStructureLatestUrl(configured: string, source = DEFAULT_SOURCE): string {
  const trimmed = configured.trim();
  const url = new URL(trimmed.includes("://") ? trimmed : `https://${trimmed}`);
  if (!url.pathname || url.pathname === "/") {
    url.pathname = LATEST_PATH;
  }
  if (url.pathname.includes(LATEST_PATH) && !url.searchParams.get("source")) {
    url.searchParams.set("source", source);
  }
  return url.toString();
}

function unavailable(detail: string): MarketStructureProbeState {
  return { status: "UNAVAILABLE", detail, payload: null };
}

export async function loadMarketStructureProbeState(): Promise<MarketStructureProbeState> {
  const configuredUrl = process.env.MARKET_STRUCTURE_ENGINE_URL?.trim();
  const token = process.env.MARKET_STRUCTURE_ENGINE_TOKEN?.trim();
  if (!configuredUrl || !token) {
    return {
      status: "NOT CONFIGURED",
      detail:
        "Set MARKET_STRUCTURE_ENGINE_URL + MARKET_STRUCTURE_ENGINE_TOKEN so Mission Control can read market-structure.v1 separately from capture health.",
      payload: null,
    };
  }

  let latestUrl: string;
  try {
    latestUrl = resolveMarketStructureLatestUrl(configuredUrl);
  } catch {
    return unavailable("Market-structure engine URL is not a valid HTTP(S) origin.");
  }

  try {
    const response = await fetch(latestUrl, {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/vnd.market-structure.v1+json",
      },
      cache: "no-store",
      signal: AbortSignal.timeout(7000),
    });
    if (response.status === 401) {
      return unavailable("Market-structure engine rejected the configured token.");
    }
    if (!response.ok) {
      return unavailable(`Market-structure engine returned HTTP ${response.status}.`);
    }
    const parsed = parseMarketStructureV1(await response.json());
    if (!parsed) {
      return {
        status: "ERROR",
        detail: "Engine response did not match market-structure.v1.",
        payload: null,
      };
    }
    const scaleSummary = parsed.scales.map((scale) => `${scale.scale} ${scale.fit}`).join(" · ") || "no scales";
    return {
      status: parsed.status,
      detail: `${parsed.schema_version} · ${parsed.status} · ${parsed.source} · ${scaleSummary}`,
      payload: parsed,
    };
  } catch {
    return unavailable("Could not reach the market-structure engine.");
  }
}
