/**
 * Strategy Lab asset selection — session + thesis aware (display only).
 * Prefer last-selected / confirmed asset over registry default.
 */

import {
  LAB_ASSET_QUERY_PARAM,
  SYSTEM_DEFAULT_ASSET_ID,
  type LabAssetId,
} from "@/lib/ppeDisplayPayload";

export const STRATEGY_LAB_ASSET_STORAGE_KEY = "msos.strategy_lab.asset.v1";

/** Last-resort UI fallback when catalog + session are unavailable. */
export const ABSOLUTE_FALLBACK_ASSET_ID = SYSTEM_DEFAULT_ASSET_ID;

const LAB_ASSET_ID_PATTERN = /^[A-Z][A-Z0-9._-]{0,11}$/;

export function isValidLabAssetId(value: string | null | undefined): value is string {
  const upper = (value ?? "").trim().toUpperCase();
  return Boolean(upper && LAB_ASSET_ID_PATTERN.test(upper));
}

export function loadStoredLabAssetId(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    const raw = window.localStorage.getItem(STRATEGY_LAB_ASSET_STORAGE_KEY);
    return isValidLabAssetId(raw) ? raw.trim().toUpperCase() : null;
  } catch {
    return null;
  }
}

export function saveStoredLabAssetId(assetId: string): void {
  if (typeof window === "undefined") {
    return;
  }
  const upper = assetId.trim().toUpperCase();
  if (!isValidLabAssetId(upper)) {
    return;
  }
  window.localStorage.setItem(STRATEGY_LAB_ASSET_STORAGE_KEY, upper);
}

export function pickAllowedLabAssetId(
  value: string | null | undefined,
  allowedIds?: readonly string[],
): string | null {
  if (!isValidLabAssetId(value)) {
    return null;
  }
  const upper = value.trim().toUpperCase();
  if (allowedIds && allowedIds.length > 0) {
    const allowed = new Set(allowedIds.map((id) => id.toUpperCase()));
    return allowed.has(upper) ? upper : null;
  }
  return upper;
}

export type ResolveLabAssetOptions = {
  query?: string | null;
  allowedIds?: readonly string[];
  catalogDefault?: string | null;
  thesisAssetId?: string | null;
  /** False on SSR — localStorage is client-only. */
  useStored?: boolean;
};

export const TOUR_LAB_ASSET_IDS = ["BTC", "ETH"] as const;

/** Tour entry — crypto only; ignores last-session stock picks (e.g. NVDA). */
export function resolveTourLabAssetId(options: {
  query?: string | null;
  allowedIds?: readonly string[];
}): LabAssetId {
  const fromQuery = pickAllowedLabAssetId(options.query, options.allowedIds);
  if (
    fromQuery &&
    TOUR_LAB_ASSET_IDS.includes(fromQuery as (typeof TOUR_LAB_ASSET_IDS)[number])
  ) {
    return fromQuery;
  }
  for (const preferred of TOUR_LAB_ASSET_IDS) {
    const picked = pickAllowedLabAssetId(preferred, options.allowedIds);
    if (picked) {
      return picked;
    }
  }
  return ABSOLUTE_FALLBACK_ASSET_ID;
}

/** Resolution order: URL → thesis → last session → catalog default → allowlist[0] → ETH. */
export function resolveLabAssetId(options: ResolveLabAssetOptions = {}): LabAssetId {
  const useStored = options.useStored !== false;
  const sources: Array<string | null | undefined> = [
    options.query,
    options.thesisAssetId,
    useStored ? loadStoredLabAssetId() : null,
    options.catalogDefault,
    options.allowedIds?.[0],
  ];

  for (const raw of sources) {
    const picked = pickAllowedLabAssetId(raw, options.allowedIds);
    if (picked) {
      return picked;
    }
  }

  const catalogOnly = pickAllowedLabAssetId(options.catalogDefault, undefined);
  if (catalogOnly) {
    return catalogOnly;
  }

  return ABSOLUTE_FALLBACK_ASSET_ID;
}
