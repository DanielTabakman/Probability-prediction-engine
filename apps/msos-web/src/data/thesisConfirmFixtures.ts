/** Thesis confirmation copy (display + persistence boundary). */

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

export const thesisConfirmHeadline = "Is this what you actually believe?";

export const thesisRestatement = {
  prefix: "I think BTC will",
  emphasis: "move in a tighter range",
  suffix: "than options are pricing over the next",
  horizon: "30 days",
};

export const compareColumns: CompareColumn[] = [
  { label: "Options market", value: "6.8% range", tone: "amber" },
  { label: "Your view", value: "5.4% range", tone: "teal" },
  { label: "Difference", value: "1.4 pts (~21%)", tone: "teal" },
];

export const confirmationChecklist: ChecklistItem[] = [
  { id: "reference", label: "Market reference — live BTC options from Deribit" },
  { id: "trust", label: "Data looks current — quotes refreshed recently" },
  { id: "horizon", label: "Timeframe locked — BTC · 30 days" },
];

export const lifecycleSteps = [
  { id: "pending", label: "Pending" },
  { id: "confirmed", label: "Confirmed" },
] as const;

export type LifecycleDisplayId = (typeof lifecycleSteps)[number]["id"];

export function lifecycleDisplayId(lifecycle: ThesisLifecycle): LifecycleDisplayId {
  return lifecycle === "confirmed" ? "confirmed" : "pending";
}

export const defaultThesisRecord: ThesisRecord = {
  instrument: "BTC options",
  horizonDays: 30,
  marketRangePct: 6.8,
  thesisRangePct: 5.4,
  referenceLabel: "BTC options · live implied distribution",
  trustLabel: "Good",
  lifecycle: "exploring",
  updatedAt: "2026-06-11T00:00:00.000Z",
};
