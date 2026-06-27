/**
 * Strategy Lab belief controls — UX copy only (no distribution math).
 */

import type { DisplayAssetMeta, DisplayPayload, LabOutcomeSummary } from "@/lib/ppeDisplayPayload";
import { buildOutcomeFromPayload, optionsSourceLabel, resolveDisplayAssetMeta } from "@/lib/ppeDisplayPayload";

export type BeliefPresetId = "higher" | "lower" | "more_volatility" | "less_volatility";

export type BeliefDirection = "higher" | "lower";
export type BeliefVolatility = "more" | "less";

export type BeliefView = {
  direction: BeliefDirection | null;
  volatility: BeliefVolatility | null;
};

/** Mirror Python BELIEF_PRESET_DISPLAY_SHIFTS — display routing only. */
export const BELIEF_PRESET_MULTS: Record<
  BeliefPresetId,
  { forward_mult: number; vol_mult: number }
> = {
  higher: { forward_mult: 1.06, vol_mult: 1.0 },
  lower: { forward_mult: 0.94, vol_mult: 1.0 },
  more_volatility: { forward_mult: 1.0, vol_mult: 1.35 },
  less_volatility: { forward_mult: 1.0, vol_mult: 0.65 },
};

export const BELIEF_DIRECTION_MULT = 1.06;
export const BELIEF_VOL_MORE_MULT = 1.35;
export const BELIEF_VOL_LESS_MULT = 0.65;

export const EMPTY_BELIEF_VIEW: BeliefView = { direction: null, volatility: null };

export type BeliefPreset = {
  id: BeliefPresetId;
  label: string;
  directionPhrase: string;
  volatilityPhrase: string;
};

export const BELIEF_PRESETS: BeliefPreset[] = [
  {
    id: "higher",
    label: "Higher",
    directionPhrase: "finish higher than options imply",
    volatilityPhrase: "similar vol to the market",
  },
  {
    id: "lower",
    label: "Lower",
    directionPhrase: "finish lower than options imply",
    volatilityPhrase: "similar vol to the market",
  },
  {
    id: "more_volatility",
    label: "More vol",
    directionPhrase: "swing in a wider range than options price",
    volatilityPhrase: "more vol than the market",
  },
  {
    id: "less_volatility",
    label: "Less vol",
    directionPhrase: "stay in a tighter range than options price",
    volatilityPhrase: "less vol than the market",
  },
];

export const BELIEF_STORAGE_KEY = "msos.belief.view.v2";
export const BELIEF_STORAGE_KEY_LEGACY = "msos.belief.preset.v1";

export function hasBeliefView(view: BeliefView): boolean {
  return view.direction !== null || view.volatility !== null;
}

export function toggleBeliefDirection(
  view: BeliefView,
  direction: BeliefDirection,
): BeliefView {
  return {
    ...view,
    direction: view.direction === direction ? null : direction,
  };
}

export function toggleBeliefVolatility(
  view: BeliefView,
  volatility: BeliefVolatility,
): BeliefView {
  return {
    ...view,
    volatility: view.volatility === volatility ? null : volatility,
  };
}

export function presetIdFromView(view: BeliefView): BeliefPresetId | null {
  if (view.direction === "higher" && view.volatility === null) return "higher";
  if (view.direction === "lower" && view.volatility === null) return "lower";
  if (view.direction === null && view.volatility === "more") return "more_volatility";
  if (view.direction === null && view.volatility === "less") return "less_volatility";
  return null;
}

export function viewFromPresetId(id: BeliefPresetId): BeliefView {
  switch (id) {
    case "higher":
      return { direction: "higher", volatility: null };
    case "lower":
      return { direction: "lower", volatility: null };
    case "more_volatility":
      return { direction: null, volatility: "more" };
    case "less_volatility":
      return { direction: null, volatility: "less" };
  }
}

export function tuningFromView(view: BeliefView): {
  forward_mult: number;
  vol_mult: number;
} {
  let forward_mult = 1.0;
  if (view.direction === "higher") forward_mult = BELIEF_DIRECTION_MULT;
  if (view.direction === "lower") forward_mult = 2 - BELIEF_DIRECTION_MULT;

  let vol_mult = 1.0;
  if (view.volatility === "more") vol_mult = BELIEF_VOL_MORE_MULT;
  if (view.volatility === "less") vol_mult = BELIEF_VOL_LESS_MULT;

  return { forward_mult, vol_mult };
}

export function buildBeliefViewLabel(view: BeliefView): string {
  const parts: string[] = [];
  if (view.direction === "higher") parts.push("Higher");
  if (view.direction === "lower") parts.push("Lower");
  if (view.volatility === "more") parts.push("More vol");
  if (view.volatility === "less") parts.push("Less vol");
  return parts.join(" · ");
}

export function buildBeliefViewPhrase(view: BeliefView): string {
  const parts: string[] = [];
  if (view.direction === "higher") parts.push("finish higher than options imply");
  if (view.direction === "lower") parts.push("finish lower than options imply");
  if (view.volatility === "more") parts.push("with more vol than the market");
  if (view.volatility === "less") parts.push("with less vol than the market");
  return parts.join(" ");
}

export function findBeliefPreset(id: BeliefPresetId | null | undefined): BeliefPreset | null {
  if (!id) return null;
  return BELIEF_PRESETS.find((p) => p.id === id) ?? null;
}

export function isBeliefPresetId(value: unknown): value is BeliefPresetId {
  return (
    value === "higher" ||
    value === "lower" ||
    value === "more_volatility" ||
    value === "less_volatility"
  );
}

function isBeliefView(value: unknown): value is BeliefView {
  if (!value || typeof value !== "object") return false;
  const view = value as Partial<BeliefView>;
  const directionOk =
    view.direction === null || view.direction === "higher" || view.direction === "lower";
  const volOk = view.volatility === null || view.volatility === "more" || view.volatility === "less";
  return directionOk && volOk;
}

export function loadStoredBeliefView(): BeliefView {
  if (typeof window === "undefined") return EMPTY_BELIEF_VIEW;
  try {
    const raw = window.localStorage.getItem(BELIEF_STORAGE_KEY);
    if (raw) {
      const parsed: unknown = JSON.parse(raw);
      if (isBeliefView(parsed)) return parsed;
    }
    const legacy = window.localStorage.getItem(BELIEF_STORAGE_KEY_LEGACY);
    if (isBeliefPresetId(legacy)) return viewFromPresetId(legacy);
  } catch {
    return EMPTY_BELIEF_VIEW;
  }
  return EMPTY_BELIEF_VIEW;
}

export function saveBeliefView(view: BeliefView): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(BELIEF_STORAGE_KEY, JSON.stringify(view));
}

export function buildBeliefSentence(
  view: BeliefView,
  expiryLabel: string,
  assetMeta?: DisplayAssetMeta,
): string {
  const asset = assetMeta ?? resolveDisplayAssetMeta(null);
  const phrase = buildBeliefViewPhrase(view);
  if (!phrase) {
    return `Pick how you disagree with options by ${expiryLabel}.`;
  }
  return `I think ${asset.id} will ${phrase} by ${expiryLabel}.`;
}

function marketWidthFromPayload(payload: DisplayPayload | null | undefined): string {
  const rows = payload?.summary?.table_rows ?? [];
  const lognormal = rows.find((row) => {
    const method = (row.Method ?? row.method ?? "").toLowerCase();
    return method.includes("lognormal") || method.includes("reference");
  });
  return lognormal?.["Implied range width (IQR)"] ?? "the range options imply";
}

function expiryLabelFromPayload(
  payload: DisplayPayload | null | undefined,
  expiryDate?: string,
): string {
  if (payload && expiryDate) {
    const match = payload.series_by_expiry.find((series) => series.expiry_date === expiryDate);
    if (match?.expiry_date) {
      return match.expiry_date;
    }
  }
  const primary = payload?.series_by_expiry?.[0];
  return primary?.expiry_date ?? expiryDate ?? "the selected expiry";
}

export function buildOutcomeFromBelief(
  presetId: BeliefPresetId,
  payload: DisplayPayload | null | undefined,
  live: boolean,
  expiryDate?: string,
): LabOutcomeSummary {
  return buildOutcomeFromView(viewFromPresetId(presetId), payload, live, expiryDate);
}

export function buildOutcomeFromView(
  view: BeliefView,
  payload: DisplayPayload | null | undefined,
  live: boolean,
  expiryDate?: string,
  assetMeta?: DisplayAssetMeta,
): LabOutcomeSummary {
  return buildOutcomeFromTuning(tuningFromView(view), payload, live, expiryDate, assetMeta);
}

export function buildOutcomeFromTuning(
  tuning: { forward_mult: number; vol_mult: number },
  payload: DisplayPayload | null | undefined,
  live: boolean,
  expiryDate?: string,
  assetMeta?: DisplayAssetMeta,
): LabOutcomeSummary {
  const asset = assetMeta ?? resolveDisplayAssetMeta(payload);
  const sourceLabel = optionsSourceLabel(asset);
  const forwardHigh = tuning.forward_mult > 1.002;
  const forwardLow = tuning.forward_mult < 0.998;
  const volHigh = tuning.vol_mult > 1.02;
  const volLow = tuning.vol_mult < 0.98;
  const labelParts: string[] = [];
  if (forwardHigh) labelParts.push("Higher");
  if (forwardLow) labelParts.push("Lower");
  if (volHigh) labelParts.push("More vol");
  if (volLow) labelParts.push("Less vol");
  const label = labelParts.length ? labelParts.join(" · ") : "Custom view";

  const phraseParts: string[] = [];
  if (forwardHigh) phraseParts.push("finish higher than options imply");
  if (forwardLow) phraseParts.push("finish lower than options imply");
  if (volHigh) phraseParts.push("with more vol than the market");
  if (volLow) phraseParts.push("with less vol than the market");
  const phrase = phraseParts.length ? phraseParts.join(" ") : "differ from what options imply";

  if (live && payload) {
    const marketWidth = marketWidthFromPayload(payload);
    const expiry = expiryLabelFromPayload(payload, expiryDate);
    const base = buildOutcomeFromPayload(payload, expiryDate, undefined, asset);

    let headline = "Your view differs from what options are pricing.";
    if (forwardHigh && !volHigh && !volLow) {
      headline = "You're bullish versus what options are pricing.";
    } else if (forwardLow && !volHigh && !volLow) {
      headline = "You're bearish versus what options are pricing.";
    } else if (!forwardHigh && !forwardLow && volHigh) {
      headline = "You expect bigger moves than the market is pricing.";
    } else if (!forwardHigh && !forwardLow && volLow) {
      headline = "You expect a calmer path than the market is pricing.";
    } else if ((forwardHigh || forwardLow) && (volHigh || volLow)) {
      headline = "You're disagreeing on both price level and range width.";
    }

    const body = `For ${expiry}, live ${sourceLabel} set the baseline. Your view is **${label}** — you think ${asset.id} will ${phrase}. The market's middle-50% range is about ${marketWidth}. Confirm when that matches your view.`;

    const marketScore = forwardHigh
      ? "Skewed up"
      : forwardLow
        ? "Skewed down"
        : volHigh
          ? "Wider"
          : volLow
            ? "Tighter"
            : "Mixed";

    return {
      tag: "Your view",
      tagTone: "teal",
      delta: "—",
      headline,
      body: body.replace(/\*\*(.*?)\*\*/g, "$1"),
      scores: [
        { label: "Market", value: marketScore, tone: "amber" },
        { label: "You", value: label, tone: "teal" },
        { label: "Next step", value: "Confirm view", tone: "teal" },
        { label: "Data", value: base.scores[3]?.value ?? "Live", tone: "teal" },
      ],
    };
  }

  return {
    tag: "Your view",
    tagTone: "teal",
    delta: volLow && !forwardHigh && !forwardLow ? "21%" : "—",
    headline: `You think ${asset.id} will ${phrase}.`,
    body: `Your view: ${label}. Confirm when this matches what you actually believe.`,
    scores: [
      { label: "Market", value: "From options", tone: "amber" },
      { label: "You", value: label, tone: "teal" },
      { label: "Gap", value: "Demo", tone: "teal" },
      { label: "Data", value: "Demo", tone: "teal" },
    ],
  };
}
