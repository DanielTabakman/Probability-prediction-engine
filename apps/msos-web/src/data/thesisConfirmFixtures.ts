/** Preview/fixture data for thesis confirmation (P5 — display + persistence boundary). */

import type { ThesisLifecycle, ThesisRecord } from "@/lib/thesisPersistence";

export type CompareColumn = {
  label: string;
  value: string;
  tone?: "teal" | "amber";
};

export type ChecklistItem = {
  id: string;
  label: string;
};

export const thesisConfirmHeadline = "Is this what you think is true?";

export const thesisRestatement = {
  prefix: "I believe BTC will",
  emphasis: "remain within a narrower range",
  suffix: "than the market prices over",
  horizon: "30 days",
};

export const compareColumns: CompareColumn[] = [
  { label: "Market view", value: "6.8% range", tone: "amber" },
  { label: "Your thesis", value: "5.4% range", tone: "teal" },
  { label: "Gap", value: "1.4 pts (21%)", tone: "teal" },
];

export const confirmationChecklist: ChecklistItem[] = [
  { id: "reference", label: "Reference named — BTC options distribution via PPE embed" },
  { id: "trust", label: "Trust context reviewed — Good (preview fixture)" },
  { id: "horizon", label: "Horizon and instrument locked — BTC / 30 days" },
];

export const lifecycleSteps: { id: ThesisLifecycle; label: string }[] = [
  { id: "exploring", label: "Exploring" },
  { id: "draft", label: "Draft" },
  { id: "confirmed", label: "Confirmed" },
];

/** Default thesis snapshot seeded from Strategy Lab fixtures (Phase A). */
export const defaultThesisRecord: ThesisRecord = {
  instrument: "BTC / Options",
  horizonDays: 30,
  marketRangePct: 6.8,
  thesisRangePct: 5.4,
  referenceLabel: "PPE distribution summary (embedded lab)",
  trustLabel: "Good",
  lifecycle: "exploring",
  updatedAt: "2026-06-11T00:00:00.000Z",
};
