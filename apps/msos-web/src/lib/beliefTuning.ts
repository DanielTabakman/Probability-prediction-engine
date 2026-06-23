/**
 * Strategy Lab belief fine-tuning — display/proxy only (math in Python).
 */

import type { BeliefPresetId, BeliefView } from "@/lib/beliefPresets";
import {
  BELIEF_DIRECTION_MULT,
  BELIEF_VOL_LESS_MULT,
  BELIEF_VOL_MORE_MULT,
  BELIEF_PRESET_MULTS,
  presetIdFromView,
} from "@/lib/beliefPresets";

export const PPE_BELIEF_OVERLAY_API_URL = (
  process.env.NEXT_PUBLIC_PPE_BELIEF_OVERLAY_API_URL ?? "/ppe-display-api/belief-overlay.json"
).trim();

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

export type BeliefOverlayResponse = {
  kind: "belief_overlay" | "belief_overlay_error";
  pdf_pct?: number[];
  forward_mult?: number;
  vol_mult?: number;
  error?: string;
};

export function tuningFromView(view: BeliefView): BeliefTuning {
  let forward_mult = 1.0;
  if (view.direction === "higher") forward_mult = BELIEF_DIRECTION_MULT;
  if (view.direction === "lower") forward_mult = 2 - BELIEF_DIRECTION_MULT;

  let vol_mult = 1.0;
  if (view.volatility === "more") vol_mult = BELIEF_VOL_MORE_MULT;
  if (view.volatility === "less") vol_mult = BELIEF_VOL_LESS_MULT;

  return {
    forward_mult: clampTuningValue("forward_mult", forward_mult),
    vol_mult: clampTuningValue("vol_mult", vol_mult),
  };
}

export function tuningFromPreset(presetId: BeliefPresetId): BeliefTuning {
  const mults = BELIEF_PRESET_MULTS[presetId];
  return { forward_mult: mults.forward_mult, vol_mult: mults.vol_mult };
}

export function clampTuningValue(key: keyof BeliefTuning, value: number): number {
  const bounds = BELIEF_TUNING_BOUNDS[key];
  return Math.min(bounds.max, Math.max(bounds.min, value));
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

export function buildBeliefOverlayFetchUrl(
  expiry: string,
  tuning: BeliefTuning,
  baseUrl = PPE_BELIEF_OVERLAY_API_URL,
): string {
  const params = new URLSearchParams({
    expiry,
    forward_mult: String(tuning.forward_mult),
    vol_mult: String(tuning.vol_mult),
  });
  const separator = baseUrl.includes("?") ? "&" : "?";
  return `${baseUrl}${separator}${params.toString()}`;
}

export async function fetchBeliefOverlayPdf(
  expiry: string,
  tuning: BeliefTuning,
): Promise<number[] | null> {
  if (!expiry) return null;
  try {
    const res = await fetch(buildBeliefOverlayFetchUrl(expiry, tuning), {
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

export function tuningMatchesView(view: BeliefView, tuning: BeliefTuning): boolean {
  const expected = tuningFromView(view);
  return (
    Math.abs(expected.forward_mult - tuning.forward_mult) < 0.0001 &&
    Math.abs(expected.vol_mult - tuning.vol_mult) < 0.0001
  );
}

export function presetIdForTuningCache(view: BeliefView, tuning: BeliefTuning): BeliefPresetId | null {
  const presetId = presetIdFromView(view);
  if (!presetId) return null;
  return tuningMatchesPreset(presetId, tuning) ? presetId : null;
}

export function tuningMatchesPreset(presetId: BeliefPresetId, tuning: BeliefTuning): boolean {
  const preset = BELIEF_PRESET_MULTS[presetId];
  return (
    Math.abs(preset.forward_mult - tuning.forward_mult) < 0.0001 &&
    Math.abs(preset.vol_mult - tuning.vol_mult) < 0.0001
  );
}
