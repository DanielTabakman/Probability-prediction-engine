/** Shared feedback form constants — visitor surfaces + API validation. */

export const CONFUSION_CATEGORIES = [
  "naming confusion",
  "market-read confusion",
  "trust/provenance confusion",
  "belief-control confusion",
  "candidate/recommendation confusion",
  "no-trade/watch-only confusion",
  "layout/visual hierarchy confusion",
  "value/desirability signal",
  "feature request / later-scope item",
] as const;

export type ConfusionCategory = (typeof CONFUSION_CATEGORIES)[number];

export const LIKERT_MIN = 1;
export const LIKERT_MAX = 5;

export const LIKERT_LABELS: Record<number, string> = {
  1: "Low",
  2: "Somewhat low",
  3: "Neutral",
  4: "Somewhat high",
  5: "High",
};

export type FeedbackSubmitPayload = {
  source: string;
  tester_profile?: string;
  comprehension?: string;
  thesis_confirm?: string;
  return_intent?: string;
  paid_interest?: string;
  confusion_category: string;
  usefulness: number;
  repeat_use_intent: number;
  objections_text?: string;
  session_note?: string;
  reality_check_row?: string;
};

export function isConfusionCategory(value: string): value is ConfusionCategory {
  return (CONFUSION_CATEGORIES as readonly string[]).includes(value);
}

/** Map operator debrief Y/N fields to API likert scores. */
export function ynToLikert(value: "Y" | "N" | ""): number {
  if (value === "Y") return 5;
  if (value === "N") return 1;
  return 3;
}
