/** Expression planning copy (display + paper-trade boundary). */

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
    title: "Watch only",
    description: "Track the idea without putting on risk.",
    tag: "Low risk",
    tagTone: "safe",
  },
  {
    id: "range",
    title: "Defined-risk range trade",
    description: "Fits a “calmer than the market” view with capped downside.",
    tag: "Best fit",
    tagTone: "selected",
  },
  {
    id: "premium",
    title: "Open-ended short vol",
    description: "Ruled out — unlimited loss under your constraints.",
    tag: "Excluded",
    tagTone: "excluded",
    dimmed: true,
  },
  {
    id: "perp",
    title: "Perp directional bet",
    description: "Poor match for a range-width view.",
    tag: "Alt",
    tagTone: "alt",
    dimmed: true,
  },
];

export const venueRails: VenueRail[] = [
  {
    id: "deribit",
    title: "Deribit options",
    description: "Eligible for this structure · connected",
    tag: "Connected",
  },
  {
    id: "hyperliquid",
    title: "Hyperliquid",
    description: "Perps rail — not for this options structure",
    tag: "Coming soon",
    dimmed: true,
  },
  {
    id: "manual",
    title: "Log elsewhere",
    description: "Record the trade in your own journal or broker",
    tag: "Available",
  },
];

export const optimizedPlan = {
  headline: "Defined-risk range trade",
  summary:
    "A structure that matches your confirmed view under the constraints you set. This is not a guarantee of profit — it is a starting point for discussion.",
};

export const planLegs: PlanLeg[] = [
  { side: "BUY", instrument: "BTC Put", strike: "Strike 96k", tenor: "30d" },
  { side: "SELL", instrument: "BTC Put", strike: "Strike 100k", tenor: "30d" },
  { side: "SELL", instrument: "BTC Call", strike: "Strike 109k", tenor: "30d" },
  { side: "BUY", instrument: "BTC Call", strike: "Strike 113k", tenor: "30d" },
];

export const statusGridPlanned: StatusCell[] = [
  { label: "View", value: "Confirmed", tone: "teal" },
  { label: "Trade plan", value: "Draft", tone: "amber" },
  { label: "Execution", value: "None" },
  { label: "Monitoring", value: "Ready" },
  { label: "Review", value: "At expiry" },
];

export const statusGridSimulated: StatusCell[] = [
  { label: "View", value: "Confirmed", tone: "teal" },
  { label: "Trade plan", value: "Paper", tone: "teal" },
  { label: "Execution", value: "None" },
  { label: "Monitoring", value: "Ready" },
  { label: "Review", value: "At expiry" },
];

export const optimizationBasis: OptimizationLine[] = [
  { label: "Fits your view", value: "Strong", tone: "teal" },
  { label: "Max loss", value: "Capped", tone: "teal" },
  { label: "Venue", value: "Deribit" },
  { label: "Liquidity / cost", value: "Estimate", tone: "amber" },
  { label: "Profit guarantee", value: "None", tone: "red" },
];

export const expressionRiskNote =
  "This is a suggested structure, not advice. You own the view and the final decision.";
