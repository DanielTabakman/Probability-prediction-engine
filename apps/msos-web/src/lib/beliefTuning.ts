/**
 * Strategy Lab belief fine-tuning — display/proxy only (math in Python).
 */

import type { BeliefPresetId } from "@/lib/beliefPresets";
import { BELIEF_PRESET_MULTS } from "@/lib/beliefPresets";
import { DEFAULT_LAB_ASSET_ID, LAB_ASSET_QUERY_PARAM } from "@/lib/ppeDisplayPayload";

export const PPE_BELIEF_OVERLAY_API_URL = (
  process.env.NEXT_PUBLIC_PPE_BELIEF_OVERLAY_API_URL ?? "/ppe-display-api/belief-overlay.json"
).trim();

export const BELIEF_TUNING_STORAGE_KEY = "msos.belief.tuning.v3";

export const COARSE_FORWARD_STEP = 0.02;
export const COARSE_VOL_STEP = 0.05;

export type BeliefTuningBounds = {
  min: number;
  max: number;
  market: number;
};

export const BELIEF_TUNING_BOUNDS: Record<"forward_mult" | "vol_mult", BeliefTuningBounds> = {
  forward_mult: { min: 0.88, max: 1.12, market: 1.0 },
  vol_mult: { min: 0.55, max: 1.45, market: 1.0 },
};

export type BeliefTuning = {
  forward_mult: number;
  vol_mult: number;
};

export const MARKET_TUNING: BeliefTuning = {
  forward_mult: BELIEF_TUNING_BOUNDS.forward_mult.market,
  vol_mult: BELIEF_TUNING_BOUNDS.vol_mult.market,
};

export type BeliefNudgeAxis = "higher" | "lower" | "more_vol" | "less_vol";

export type BeliefOverlayResponse = {
  kind: "belief_overlay" | "belief_overlay_error";
  pdf_pct?: number[];
  forward_mult?: number;
  vol_mult?: number;
  error?: string;
};

function isBeliefTuning(value: unknown): value is BeliefTuning {
  if (!value || typeof value !== "object") return false;
  const row = value as Partial<BeliefTuning>;
  return typeof row.forward_mult === "number" && typeof row.vol_mult === "number";
}

export function clampTuningValue(key: keyof BeliefTuning, value: number): number {
  const bounds = BELIEF_TUNING_BOUNDS[key];
  return Math.min(bounds.max, Math.max(bounds.min, value));
}

export function normalizeTuning(tuning: BeliefTuning): BeliefTuning {
  return {
    forward_mult: clampTuningValue("forward_mult", tuning.forward_mult),
    vol_mult: clampTuningValue("vol_mult", tuning.vol_mult),
  };
}

export function isMarketTuning(tuning: BeliefTuning): boolean {
  return (
    Math.abs(tuning.forward_mult - MARKET_TUNING.forward_mult) < 0.0005 &&
    Math.abs(tuning.vol_mult - MARKET_TUNING.vol_mult) < 0.0005
  );
}

export function nudgeTuning(tuning: BeliefTuning, axis: BeliefNudgeAxis): BeliefTuning {
  switch (axis) {
    case "higher":
      return normalizeTuning({
        ...tuning,
        forward_mult: tuning.forward_mult + COARSE_FORWARD_STEP,
      });
    case "lower":
      return normalizeTuning({
        ...tuning,
        forward_mult: tuning.forward_mult - COARSE_FORWARD_STEP,
      });
    case "more_vol":
      return normalizeTuning({
        ...tuning,
        vol_mult: tuning.vol_mult + COARSE_VOL_STEP,
      });
    case "less_vol":
      return normalizeTuning({
        ...tuning,
        vol_mult: tuning.vol_mult - COARSE_VOL_STEP,
      });
  }
}

export function loadStoredBeliefTuning(): BeliefTuning {
  if (typeof window === "undefined") return MARKET_TUNING;
  try {
    const raw = window.localStorage.getItem(BELIEF_TUNING_STORAGE_KEY);
    if (raw) {
      const parsed: unknown = JSON.parse(raw);
      if (isBeliefTuning(parsed)) {
        return normalizeTuning(parsed);
      }
    }
    const legacyViewRaw = window.localStorage.getItem("msos.belief.view.v2");
    if (legacyViewRaw) {
      const parsed: unknown = JSON.parse(legacyViewRaw);
      if (parsed && typeof parsed === "object") {
        const view = parsed as { direction?: string | null; volatility?: string | null };
        let forward_mult = 1.0;
        if (view.direction === "higher") forward_mult = 1.06;
        if (view.direction === "lower") forward_mult = 0.94;
        let vol_mult = 1.0;
        if (view.volatility === "more") vol_mult = 1.35;
        if (view.volatility === "less") vol_mult = 0.65;
        return normalizeTuning({ forward_mult, vol_mult });
      }
    }
  } catch {
    return MARKET_TUNING;
  }
  return MARKET_TUNING;
}

export function saveBeliefTuning(tuning: BeliefTuning): void {
  if (typeof window === "undefined") return;
  const next = normalizeTuning(tuning);
  window.localStorage.setItem(BELIEF_TUNING_STORAGE_KEY, JSON.stringify(next));
}

export function formatCenterShiftLabel(forwardMult: number): string {
  const pct = Math.round((forwardMult - 1) * 100);
  if (pct === 0) return "At market center";
  return pct > 0 ? `${pct}% above market` : `${Math.abs(pct)}% below market`;
}

export function formatRangeWidthLabel(volMult: number): string {
  const pct = Math.round(volMult * 100);
  if (pct === 100) return "Market width";
  return `${pct}% of market vol`;
}

export function buildTuningLabel(tuning: BeliefTuning): string {
  if (isMarketTuning(tuning)) return "At market";
  const parts: string[] = [];
  if (tuning.forward_mult > 1.002) parts.push("Higher");
  if (tuning.forward_mult < 0.998) parts.push("Lower");
  if (tuning.vol_mult > 1.02) parts.push("More vol");
  if (tuning.vol_mult < 0.98) parts.push("Less vol");
  if (!parts.length) {
    parts.push(formatCenterShiftLabel(tuning.forward_mult));
    parts.push(formatRangeWidthLabel(tuning.vol_mult));
  }
  return parts.join(" · ");
}

export function buildTuningPhrase(tuning: BeliefTuning): string {
  if (isMarketTuning(tuning)) return "match what options imply";
  const parts: string[] = [];
  if (tuning.forward_mult > 1.002) parts.push("finish higher than options imply");
  if (tuning.forward_mult < 0.998) parts.push("finish lower than options imply");
  if (tuning.vol_mult > 1.02) parts.push("with more vol than the market");
  if (tuning.vol_mult < 0.98) parts.push("with less vol than the market");
  if (!parts.length) {
    parts.push(
      `center ${formatCenterShiftLabel(tuning.forward_mult).toLowerCase()} and ${formatRangeWidthLabel(tuning.vol_mult).toLowerCase()}`,
    );
  }
  return parts.join(" ");
}

export function buildBeliefOverlayFetchUrl(
  expiry: string,
  tuning: BeliefTuning,
  assetId: string = DEFAULT_LAB_ASSET_ID,
  baseUrl = PPE_BELIEF_OVERLAY_API_URL,
): string {
  const params = new URLSearchParams({
    expiry,
    forward_mult: String(tuning.forward_mult),
    vol_mult: String(tuning.vol_mult),
  });
  const normalizedAsset = assetId.trim().toUpperCase();
  if (normalizedAsset && normalizedAsset !== DEFAULT_LAB_ASSET_ID) {
    params.set(LAB_ASSET_QUERY_PARAM, normalizedAsset);
  }
  const separator = baseUrl.includes("?") ? "&" : "?";
  return `${baseUrl}${separator}${params.toString()}`;
}

export async function fetchBeliefOverlayPdf(
  expiry: string,
  tuning: BeliefTuning,
  assetId: string = DEFAULT_LAB_ASSET_ID,
): Promise<number[] | null> {
  if (!expiry || isMarketTuning(tuning)) return null;
  try {
    const res = await fetch(buildBeliefOverlayFetchUrl(expiry, tuning, assetId), {
      cache: "no-store",
      headers: { Accept: "application/json", "User-Agent": "msos-web/1" },
    });
    if (!res.ok) return null;
    const data = (await res.json()) as BeliefOverlayResponse;
    if (data.kind !== "belief_overlay" || !Array.isArray(data.pdf_pct)) {
      return null;
    }
    return data.pdf_pct;
  } catch {
    return null;
  }
}

export function tuningMatchesPreset(presetId: BeliefPresetId, tuning: BeliefTuning): boolean {
  const preset = BELIEF_PRESET_MULTS[presetId];
  return (
    Math.abs(preset.forward_mult - tuning.forward_mult) < 0.0001 &&
    Math.abs(preset.vol_mult - tuning.vol_mult) < 0.0001
  );
}

export function presetIdForTuning(tuning: BeliefTuning): BeliefPresetId | null {
  const ids: BeliefPresetId[] = ["higher", "lower", "more_volatility", "less_volatility"];
  for (const id of ids) {
    if (tuningMatchesPreset(id, tuning)) return id;
  }
  return null;
}

export function tuningFromPreset(presetId: BeliefPresetId): BeliefTuning {
  const mults = BELIEF_PRESET_MULTS[presetId];
  return normalizeTuning({ forward_mult: mults.forward_mult, vol_mult: mults.vol_mult });
}
