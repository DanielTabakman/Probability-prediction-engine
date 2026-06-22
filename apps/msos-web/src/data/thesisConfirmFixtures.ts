/** Thesis confirmation fixtures (persistence boundary + re-exports from content). */

import type { ThesisRecord } from "@/lib/thesisPersistence";

export type CompareColumn = {
  label: string;
  value: string;
  tone?: "teal" | "amber";
};

export type ChecklistItem = {
  id: string;
  label: string;
};

export {
  thesisCompareColumns as compareColumns,
  thesisConfirmChecklist as confirmationChecklist,
  thesisConfirmHeadline,
  thesisLifecycleSteps as lifecycleSteps,
  thesisRestatement,
} from "@/content/thesisConfirm";

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
