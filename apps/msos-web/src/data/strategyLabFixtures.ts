/** Preview/fixture data for Strategy Lab (P4 — no PPE math; display only). */

export type LabMetric = {
  label: string;
  value: string;
  tone?: "teal" | "amber";
};

export const strategyLabMetrics: LabMetric[] = [
  { label: "Selected market", value: "BTC / Options" },
  { label: "Horizon", value: "30 days" },
  { label: "Spot", value: "$104,320" },
  { label: "Market width", value: "6.8%", tone: "amber" },
  { label: "Your range", value: "5.4%", tone: "teal" },
  { label: "Trust", value: "Good", tone: "teal" },
];

export const lensTiles = [
  {
    mark: "P",
    title: "Options Distribution Lens — BTC",
    description: "Live via PPE · BTC options preview enabled",
    status: "LIVE",
    live: true,
    href: "/strategy-lab",
  },
  {
    mark: "O",
    title: "Options Distribution Lens — ETH",
    description: "Planned: same PPE workflow for next asset",
    status: "Soon",
    live: false,
  },
  {
    mark: "E",
    title: "Event Probability Lens",
    description: "Planned: outcome markets and implied odds",
    status: "Planned",
    live: false,
  },
  {
    mark: "L",
    title: "Leverage & Positioning Lens",
    description: "Planned: funding, OI, crowding and perp pressure",
    status: "Planned",
    live: false,
  },
];

export const outcomeSummary = {
  tag: "Worth inspecting",
  tagTone: "amber" as const,
  delta: "21%",
  headline: "Your range is 21% narrower than market pricing.",
  body:
    "The options market implies a 6.8% 30-day range. Your stated thesis implies a 5.4% range. Difference: 1.4 points, or 20.6% of the market-implied width.",
  scores: [
    { label: "Market view", value: "Wider", tone: "amber" as const },
    { label: "Your thesis", value: "Narrower", tone: "teal" as const },
    { label: "Materiality", value: "Above threshold", tone: "teal" as const },
    { label: "Trust", value: "Good", tone: "teal" as const },
  ],
};
