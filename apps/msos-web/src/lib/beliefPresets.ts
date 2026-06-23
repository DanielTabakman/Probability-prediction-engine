/**
 * Strategy Lab belief presets — UX copy only (no distribution math).
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
    label: "More volatility",
    directionPhrase: "swing in a wider range than options price",
    volatilityPhrase: "more vol than the market",
  },
  {
    id: "less_volatility",
    label: "Less volatility",
    directionPhrase: "stay in a tighter range than options price",
    volatilityPhrase: "less vol than the market",
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
  return `I think BTC will ${preset.directionPhrase} by ${expiryLabel}.`;
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
  const preset = findBeliefPreset(presetId);
  if (!preset) {
    throw new Error(`Unknown belief preset: ${presetId}`);
  }
  if (live && payload) {
    const marketWidth = marketWidthFromPayload(payload);
    const expiry = expiryLabelFromPayload(payload, expiryDate);
    const base = buildOutcomeFromPayload(payload);

    const headlines: Record<BeliefPresetId, string> = {
      higher: "You're bullish versus what options are pricing.",
      lower: "You're bearish versus what options are pricing.",
      more_volatility: "You expect bigger moves than the market is pricing.",
      less_volatility: "You expect a calmer path than the market is pricing.",
    };

    const bodies: Record<BeliefPresetId, string> = {
      higher: `For ${expiry}, live Deribit options set the baseline. You picked **${preset.label}** — you think spot finishes above where the curve peaks. The market's middle-50% range is about ${marketWidth}. Confirm when that matches your view.`,
      lower: `For ${expiry}, the chart shows what BTC options imply today. You picked **${preset.label}** — you think spot finishes below that center. Middle-50% range: ${marketWidth}.`,
      more_volatility: `For ${expiry}, options price a range of about ${marketWidth}. You picked **${preset.label}** — you think realized moves could exceed that. This flags a disagreement in shape, not a trade signal.`,
      less_volatility: `For ${expiry}, options price a range of about ${marketWidth}. You picked **${preset.label}** — you think price may chop inside a tighter band. Save the view when you're ready to plan a trade.`,
    };

    const scoreMarket: Record<BeliefPresetId, string> = {
      higher: "Skewed up",
      lower: "Skewed down",
      more_volatility: "Wider",
      less_volatility: "Tighter",
    };

    return {
      tag: "Your view",
      tagTone: "teal",
      delta: "—",
      headline: headlines[preset.id],
      body: bodies[preset.id].replace(/\*\*(.*?)\*\*/g, "$1"),
      scores: [
        { label: "Market", value: scoreMarket[preset.id], tone: "amber" },
        { label: "You", value: preset.label, tone: "teal" },
        { label: "Next step", value: "Confirm view", tone: "teal" },
        { label: "Data", value: base.scores[3]?.value ?? "Live", tone: "teal" },
      ],
    };
  }

  const fixtureHeadlines: Record<BeliefPresetId, string> = {
    higher: "You think BTC ends higher than the market center.",
    lower: "You think BTC ends lower than the market center.",
    more_volatility: "You think swings will be wider than options imply.",
    less_volatility: "You think price will be calmer than options imply.",
  };

  return {
    tag: "Your view",
    tagTone: "teal",
    delta: preset.id === "less_volatility" ? "21%" : "—",
    headline: fixtureHeadlines[preset.id],
    body: `You selected ${preset.label}. ${preset.directionPhrase.charAt(0).toUpperCase()}${preset.directionPhrase.slice(1)}. Confirm when this matches what you actually believe.`,
    scores: [
      { label: "Market", value: "From options", tone: "amber" },
      { label: "You", value: preset.label, tone: "teal" },
      { label: "Gap", value: "Demo", tone: "teal" },
      { label: "Data", value: "Demo", tone: "teal" },
    ],
  };
}
