/** Preview/fixture data for Strategy Lab (display only — no distribution math). */

export type LabMetric = {
  label: string;
  value: string;
  tone?: "teal" | "amber";
};

export const strategyLabMetrics: LabMetric[] = [
  { label: "Market", value: "BTC options" },
  { label: "Expiry", value: "30 days" },
  { label: "Spot", value: "$104,320" },
  { label: "Market range", value: "6.8%", tone: "amber" },
  { label: "Your range", value: "5.4%", tone: "teal" },
  { label: "Data", value: "Demo", tone: "teal" },
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
  tag: "Worth a look",
  tagTone: "amber" as const,
  delta: "21%",
  headline: "You think BTC will move less than options are pricing.",
  body:
    "Options imply about a 6.8% range over 30 days. Your view is closer to 5.4% — roughly 21% tighter than the market's implied band.",
  scores: [
    { label: "Market", value: "Wider range", tone: "amber" as const },
    { label: "Your view", value: "Tighter range", tone: "teal" as const },
    { label: "Gap", value: "Meaningful", tone: "teal" as const },
    { label: "Data", value: "Demo", tone: "teal" as const },
  ],
};
