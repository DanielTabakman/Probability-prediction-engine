/**
 * Strategy Lab visitor copy — canon: docs/PRODUCT_COPY/packets/strategy-lab.v1.md
 */

import type { LabOutcomeSummary } from "@/lib/ppeDisplayPayload";

export const strategyLabMetadata = {
  title: "Strategy Lab | Market Structure OS",
  description: "Compare your view to what BTC options imply — live Deribit data on the demo.",
} as const;

export const strategyLabPageHeader = {
  crumb: "Strategy Lab · BTC options",
  title: "Strategy Lab",
  liveDataPill: "Live market data",
  demoDataPill: "Demo data",
  shareButton: "Share",
  saveViewCta: "Save your view",
} as const;

export const strategyLabBeliefBuilder = {
  title: "What do you believe?",
  pickOnePrefix: "Pick one —",
  pickOneSuffix: "than options imply.",
  pickOneChips: ["higher", "lower", "more vol", "less vol"] as const,
  hintSelected: "This compares your view to the market curve — not a trade recommendation.",
  hintDefault: "Tap a button to see how your view differs from what options price.",
} as const;

export const strategyLabChartPanel = {
  title: "Market vs your view",
  subtitle: "Purple curve = what BTC options imply today. Your pick shows where you disagree.",
  tag: "Options",
  beliefBannerPrefix: "Your view:",
  beliefBannerSuffix: "— compare to the chart below.",
  legendMarket: "Options market",
  legendReference: "Reference curve",
  legendBeliefPrefix: "Your view",
  controlsAriaLabel: "Fine-tuning (coming soon)",
  rangeWidthLabel: "Range width",
  tailWeightLabel: "Tail weight",
} as const;

export const strategyLabLensSection = {
  title: "Other markets",
  subtitle: "BTC options are live. More assets coming.",
} as const;

export const strategyLabLensTiles = [
  {
    mark: "B",
    title: "BTC options",
    description: "Live BTC options from Deribit — try it now",
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
] as const;

export const strategyLabDefaultOutcome: LabOutcomeSummary = {
  tag: "Worth a look",
  tagTone: "amber",
  delta: "21%",
  headline: "You think BTC will move less than options are pricing.",
  body: "Options imply about a 6.8% range over 30 days. Your view is closer to 5.4% — roughly 21% tighter than the market's implied band.",
  scores: [
    { label: "Market", value: "Wider range", tone: "amber" },
    { label: "Your view", value: "Tighter range", tone: "teal" },
    { label: "Gap", value: "Meaningful", tone: "teal" },
    { label: "Data", value: "Demo", tone: "teal" },
  ],
};

export const strategyLabOutcomePanel = {
  title: "What this means",
  subtitle: "Decision support — not financial advice.",
  decisionNextWithPreset: (label: string) => `Next: confirm your “${label.toLowerCase()}” view`,
  decisionNextDefault: "Next: pick how you disagree with the market",
  decisionBody: "Then explore trade structures that fit — paper only on this demo.",
  confirmCta: "Confirm view →",
} as const;
