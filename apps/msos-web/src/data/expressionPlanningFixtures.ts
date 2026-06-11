/** Preview/fixture data for expression planning (P6 — display + sim-only boundary). */

export type FamilyTag = "safe" | "selected" | "excluded" | "alt";

export type ExpressionFamily = {
  id: string;
  title: string;
  description: string;
  tag: string;
  tagTone: FamilyTag;
  dimmed?: boolean;
};

export type VenueRail = {
  id: string;
  title: string;
  description: string;
  tag: string;
  dimmed?: boolean;
};

export type PlanLeg = {
  side: "BUY" | "SELL";
  instrument: string;
  strike: string;
  tenor: string;
};

export type StatusCell = {
  label: string;
  value: string;
  tone?: "teal" | "amber";
};

export type OptimizationLine = {
  label: string;
  value: string;
  tone?: "teal" | "amber" | "red";
};

export const expressionFamilies: ExpressionFamily[] = [
  {
    id: "observe",
    title: "Observe only",
    description: "Lowest action risk; monitor thesis without exposure.",
    tag: "Safe",
    tagTone: "safe",
  },
  {
    id: "range",
    title: "Defined-risk range structure",
    description: "Best fit under constraints for narrower-range thesis.",
    tag: "Selected",
    tagTone: "selected",
  },
  {
    id: "premium",
    title: "Unbounded premium selling",
    description: "Excluded by max-loss constraint.",
    tag: "Excluded",
    tagTone: "excluded",
    dimmed: true,
  },
  {
    id: "perp",
    title: "Perp directional proxy",
    description: "Poor thesis fit for range-width claim.",
    tag: "Alt",
    tagTone: "alt",
    dimmed: true,
  },
];

export const venueRails: VenueRail[] = [
  {
    id: "deribit",
    title: "Deribit Options",
    description: "Eligible for options structure · connected",
    tag: "Connected",
  },
  {
    id: "hyperliquid",
    title: "Hyperliquid",
    description: "Pending: future perps / positioning rail, not this options structure",
    tag: "Pending",
    dimmed: true,
  },
  {
    id: "manual",
    title: "Manual / external log",
    description: "Record execution elsewhere",
    tag: "Available",
  },
];

export const optimizedPlan = {
  headline: "Defined-risk range structure",
  summary:
    "Best-fit available structure for the confirmed thesis under selected constraints, available venue and current market data. This is not optimized for guaranteed profit.",
};

export const planLegs: PlanLeg[] = [
  { side: "BUY", instrument: "BTC Put", strike: "Strike 96k", tenor: "30d" },
  { side: "SELL", instrument: "BTC Put", strike: "Strike 100k", tenor: "30d" },
  { side: "SELL", instrument: "BTC Call", strike: "Strike 109k", tenor: "30d" },
  { side: "BUY", instrument: "BTC Call", strike: "Strike 113k", tenor: "30d" },
];

export const statusGridPlanned: StatusCell[] = [
  { label: "Thesis", value: "Confirmed", tone: "teal" },
  { label: "Expression", value: "Planned", tone: "amber" },
  { label: "Execution", value: "None" },
  { label: "Monitoring", value: "Ready" },
  { label: "Review", value: "Expiry" },
];

export const statusGridSimulated: StatusCell[] = [
  { label: "Thesis", value: "Confirmed", tone: "teal" },
  { label: "Expression", value: "Simulated", tone: "teal" },
  { label: "Execution", value: "None" },
  { label: "Monitoring", value: "Ready" },
  { label: "Review", value: "Expiry" },
];

export const optimizationBasis: OptimizationLine[] = [
  { label: "Thesis fit", value: "Strong", tone: "teal" },
  { label: "Max loss constraint", value: "Bounded", tone: "teal" },
  { label: "Available venue", value: "Deribit" },
  { label: "Liquidity / cost", value: "Estimate", tone: "amber" },
  { label: "Profit guarantee", value: "None", tone: "red" },
];

export const expressionRiskNote =
  "Suggested expression means best fit under the assumptions shown. The user still owns the thesis and final decision.";
