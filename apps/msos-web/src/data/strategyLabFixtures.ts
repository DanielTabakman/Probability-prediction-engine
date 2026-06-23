/** Preview/fixture data for Strategy Lab (display only — no distribution math). */

export type LabMetric = {
  label: string;
  value: string;
  tone?: "teal" | "amber";
};

export const strategyLabMetrics: LabMetric[] = [
  { label: "Market", value: "BTC options (sample)" },
  { label: "Expiry", value: "30 days" },
  { label: "Spot", value: "Sample only", tone: "amber" },
  { label: "Market range", value: "6.8% (sample)", tone: "amber" },
  { label: "Your range", value: "5.4% (sample)", tone: "amber" },
  { label: "Data", value: "Sample · not live", tone: "amber" },
];

export const lensTiles = [
  {
    mark: "B",
    title: "BTC options",
    description: "Live implied distribution from Deribit — available now",
    status: "Live",
    live: true,
    href: "/strategy-lab",
  },
  {
    mark: "E",
    title: "ETH options",
    description: "Same workflow — coming next",
    status: "Soon",
    live: false,
  },
  {
    mark: "P",
    title: "Event markets",
    description: "Elections, macro events, and other outcome markets",
    status: "Planned",
    live: false,
  },
  {
    mark: "L",
    title: "Positioning & funding",
    description: "Open interest, funding, and crowding signals",
    status: "Planned",
    live: false,
  },
];

export const outcomeSummary = {
  tag: "Sample",
  tagTone: "amber" as const,
  delta: "21%",
  headline: "Sample outcome — not from live options.",
  body:
    "These numbers are placeholders for layout preview. When live Deribit data loads, spot, range, and curves update automatically.",
  scores: [
    { label: "Market", value: "Sample", tone: "amber" as const },
    { label: "Your view", value: "Sample", tone: "amber" as const },
    { label: "Gap", value: "Sample", tone: "amber" as const },
    { label: "Data", value: "Not live", tone: "amber" as const },
  ],
};
