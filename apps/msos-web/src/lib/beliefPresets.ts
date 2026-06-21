/**
 * Strategy Lab belief presets — UX copy and persistence only (no distribution math).
 */

import type { DisplayPayload, LabOutcomeSummary } from "@/lib/ppeDisplayPayload";
import { buildOutcomeFromPayload } from "@/lib/ppeDisplayPayload";

export type BeliefPresetId = "higher" | "lower" | "more_volatility" | "less_volatility";

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
    directionPhrase: "finish above where options imply",
    volatilityPhrase: "similar volatility to the market",
  },
  {
    id: "lower",
    label: "Lower",
    directionPhrase: "finish below where options imply",
    volatilityPhrase: "similar volatility to the market",
  },
  {
    id: "more_volatility",
    label: "More volatility",
    directionPhrase: "move in a wider band than options price",
    volatilityPhrase: "more volatility than the market",
  },
  {
    id: "less_volatility",
    label: "Less volatility",
    directionPhrase: "stay in a tighter band than options price",
    volatilityPhrase: "less volatility than the market",
  },
];

export const BELIEF_STORAGE_KEY = "msos.belief.preset.v1";

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

export function loadStoredBeliefPresetId(): BeliefPresetId | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(BELIEF_STORAGE_KEY);
    return isBeliefPresetId(raw) ? raw : null;
  } catch {
    return null;
  }
}

export function saveBeliefPresetId(id: BeliefPresetId): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(BELIEF_STORAGE_KEY, id);
}

export function buildBeliefSentence(preset: BeliefPreset, expiryLabel: string): string {
  return `I believe BTC will ${preset.directionPhrase} over ${expiryLabel}.`;
}

function marketWidthFromPayload(payload: DisplayPayload | null | undefined): string {
  const rows = payload?.summary?.table_rows ?? [];
  const lognormal = rows.find((row) => {
    const method = (row.Method ?? row.method ?? "").toLowerCase();
    return method.includes("lognormal") || method.includes("reference");
  });
  return lognormal?.["Implied range width (IQR)"] ?? "the market-implied range";
}

function expiryLabelFromPayload(payload: DisplayPayload | null | undefined): string {
  const primary = payload?.series_by_expiry?.[0];
  return primary?.expiry_date ?? "the selected expiry";
}

export function buildOutcomeFromBelief(
  presetId: BeliefPresetId,
  payload: DisplayPayload | null | undefined,
  live: boolean,
): LabOutcomeSummary {
  const preset = findBeliefPreset(presetId);
  if (!preset) {
    throw new Error(`Unknown belief preset: ${presetId}`);
  }
  if (live && payload) {
    const marketWidth = marketWidthFromPayload(payload);
    const expiry = expiryLabelFromPayload(payload);
    const base = buildOutcomeFromPayload(payload);

    const headlines: Record<BeliefPresetId, string> = {
      higher: "You expect BTC higher than the options-implied center.",
      lower: "You expect BTC lower than the options-implied center.",
      more_volatility: "You expect more movement than options are pricing.",
      less_volatility: "You expect a calmer path than options are pricing.",
    };

    const bodies: Record<BeliefPresetId, string> = {
      higher: `For ${expiry}, the market-implied distribution centers on live Deribit quotes. Your preset (${preset.label}): you think spot finishes above where the curve peaks. Market interquartile width: ${marketWidth}. Confirm when this matches your view.`,
      lower: `For ${expiry}, options imply a distribution from live Deribit data. Your preset (${preset.label}): you think spot finishes below where the curve peaks. Market interquartile width: ${marketWidth}. Confirm when ready.`,
      more_volatility: `For ${expiry}, the market prices an interquartile width of ${marketWidth}. Your preset (${preset.label}): you think realized movement could exceed that band. Shape disagreement only — not a trade signal.`,
      less_volatility: `For ${expiry}, the market prices an interquartile width of ${marketWidth}. Your preset (${preset.label}): you think price may stay tighter than options imply. Exploratory until you confirm the thesis.`,
    };

    const scoreMarket: Record<BeliefPresetId, string> = {
      higher: "Center skew up",
      lower: "Center skew down",
      more_volatility: "Wider band",
      less_volatility: "Narrower band",
    };

    return {
      tag: "Belief selected",
      tagTone: "teal",
      delta: "—",
      headline: headlines[preset.id],
      body: bodies[preset.id],
      scores: [
        { label: "Market view", value: scoreMarket[preset.id], tone: "amber" },
        { label: "Your thesis", value: preset.label, tone: "teal" },
        { label: "Materiality", value: "Inspect on confirm", tone: "teal" },
        { label: "Data", value: base.scores[3]?.value ?? "Live feed", tone: "teal" },
      ],
    };
  }

  const fixtureHeadlines: Record<BeliefPresetId, string> = {
    higher: "You expect BTC to finish higher than the market center.",
    lower: "You expect BTC to finish lower than the market center.",
    more_volatility: "You expect wider swings than the market is pricing.",
    less_volatility: "Your range is narrower than market pricing.",
  };

  return {
    tag: "Belief selected",
    tagTone: "teal",
    delta: preset.id === "less_volatility" ? "21%" : "—",
    headline: fixtureHeadlines[preset.id],
    body: `Preset: ${preset.label}. ${preset.directionPhrase}; ${preset.volatilityPhrase}. Adjust or confirm when this matches what you think.`,
    scores: [
      { label: "Market view", value: "From options", tone: "amber" },
      { label: "Your thesis", value: preset.label, tone: "teal" },
      { label: "Materiality", value: "Preview", tone: "teal" },
      { label: "Trust", value: "Fixture", tone: "teal" },
    ],
  };
}
