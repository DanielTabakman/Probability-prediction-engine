/**
 * Thesis confirmation copy — canon: docs/PRODUCT_COPY/packets/strategy-lab.v1.md
 */

import type { ThesisLifecycle } from "@/lib/thesisPersistence";

export const thesisConfirmPageHeader = {
  crumb: "Strategy Lab · Confirm",
  title: "Confirm your view",
  backToLab: "Back to lab",
} as const;

export const thesisConfirmHeadline = "Is this what you actually believe?";

export const thesisRestatement = {
  prefix: "I think BTC will",
  emphasis: "move in a tighter range",
  suffix: "than options are pricing over the next",
  horizon: "30 days",
} as const;

export const thesisCompareColumns = [
  { label: "What options imply", value: "6.8% range", tone: "amber" as const },
  { label: "Your view", value: "5.4% range", tone: "teal" as const },
  { label: "Difference", value: "1.4 pts (~21%)", tone: "teal" as const },
];

export const thesisContextLocks = {
  market: "Market",
  dataQuality: "Data quality",
  timeframe: "Timeframe",
} as const;

export const thesisConfirmChecklist = [
  { id: "reference", label: "Market data — live BTC options from Deribit" },
  { id: "trust", label: "Data looks current — quotes refreshed recently" },
  { id: "horizon", label: "Timeframe locked — BTC · 30 days" },
] as const;

export const thesisLifecycleSteps: { id: ThesisLifecycle; label: string }[] = [
  { id: "exploring", label: "Exploring" },
  { id: "draft", label: "Draft" },
  { id: "confirmed", label: "Confirmed" },
];

export const thesisConfirmSidebar = {
  beforeContinueTitle: "Before you continue",
  beforeContinueSub: "Quick sanity checks — no hidden “AI says buy.”",
  statusTitle: "Status",
  nextStepTitle: "Next step",
  nextStepBody: "Plan a paper trade after you confirm — no live orders on this demo.",
  saveDraft: "Save draft",
  confirmView: "Confirm view",
  planPaperTrade: "Plan a paper trade",
  confirmFirstTitle: "Confirm your view first",
} as const;
