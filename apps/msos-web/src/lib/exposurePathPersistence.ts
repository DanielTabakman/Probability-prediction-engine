/**
 * Saved exposure path bookmark (preview) — browser localStorage only.
 * Sim / research support; not order routing.
 */

import type { ExposureDirection, ExposurePathRecord, HorizonChip } from "@/lib/ppeExposureMenu";

export const EXPOSURE_PATH_STORAGE_KEY = "msos.exposure_path.preview.v1";

export const EXPOSURE_PATH_SAVE_LABEL =
  "Path saved to your workspace for later — comparison only, not a trade.";

export type SavedExposurePath = {
  assetId: string;
  direction: ExposureDirection;
  horizon: HorizonChip;
  pathId: string;
  label: string;
  headline: string;
  trustBadge: ExposurePathRecord["trust_badge"];
  savedAt: string;
};

function isSavedExposurePath(value: unknown): value is SavedExposurePath {
  if (!value || typeof value !== "object") {
    return false;
  }
  const row = value as Partial<SavedExposurePath>;
  return (
    typeof row.assetId === "string" &&
    typeof row.pathId === "string" &&
    typeof row.label === "string" &&
    typeof row.savedAt === "string"
  );
}

export function loadSavedExposurePath(): SavedExposurePath | null {
  if (typeof window === "undefined") {
    return null;
  }
  try {
    const raw = window.localStorage.getItem(EXPOSURE_PATH_STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed: unknown = JSON.parse(raw);
    return isSavedExposurePath(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

export function saveExposurePathBookmark(input: {
  assetId: string;
  direction: ExposureDirection;
  horizon: HorizonChip;
  path: ExposurePathRecord;
}): SavedExposurePath {
  const record: SavedExposurePath = {
    assetId: input.assetId.trim().toUpperCase(),
    direction: input.direction,
    horizon: input.horizon,
    pathId: input.path.path_id,
    label: input.path.label,
    headline: input.path.headline,
    trustBadge: input.path.trust_badge,
    savedAt: new Date().toISOString(),
  };
  if (typeof window !== "undefined") {
    window.localStorage.setItem(EXPOSURE_PATH_STORAGE_KEY, JSON.stringify(record));
  }
  return record;
}

export function clearSavedExposurePath(): void {
  if (typeof window !== "undefined") {
    window.localStorage.removeItem(EXPOSURE_PATH_STORAGE_KEY);
  }
}

export function buildExposurePageHrefFromSaved(saved: SavedExposurePath): string {
  const params = new URLSearchParams({
    asset: saved.assetId,
    direction: saved.direction,
    horizon: saved.horizon,
  });
  return `/exposure?${params.toString()}`;
}
