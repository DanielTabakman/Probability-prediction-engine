/** Preview/fixture data for Command Center (P3 — no live APIs). */

export type NavItem = {
  id: string;
  label: string;
  href: string;
  active?: boolean;
  disabled?: boolean;
};

export type MarketAsset = {
  label: string;
  status: string;
  live?: boolean;
};

export const navItems: NavItem[] = [
  { id: "command-center", label: "Command Center", href: "/command-center" },
  { id: "strategy-lab", label: "Strategy Lab", href: "/strategy-lab" },
  { id: "theses", label: "Theses", href: "#", disabled: true },
  { id: "expression", label: "Expression & Execution", href: "#", disabled: true },
  { id: "monitor", label: "Monitor", href: "#", disabled: true },
  { id: "history", label: "History", href: "#", disabled: true },
];

export const connectedMarkets: MarketAsset[] = [
  { label: "BTC / Options", status: "LIVE", live: true },
  { label: "ETH / Options", status: "Soon" },
  { label: "Event Markets", status: "Planned" },
  { label: "Perp Positioning", status: "Planned" },
];

export const kpis = [
  { label: "Draft theses", value: "3", tone: "amber" as const, sub: "Resume research" },
  { label: "Confirmed theses", value: "2", tone: "teal" as const, sub: "1 awaiting review" },
  { label: "Simulations / live", value: "1 / 0", sub: "No connected live positions" },
  { label: "Reviews due", value: "4", tone: "red" as const, sub: "1 trust warning" },
];

export const labTiles = [
  {
    mark: "P",
    title: "Strategy Lab — PPE Tool",
    description: "Live now: options distribution lens · BTC enabled in preview",
    cta: "Open PPE",
    enabled: true,
  },
  {
    mark: "O",
    title: "Options Distribution Lens — ETH",
    description: "Planned: same PPE workflow for next asset",
    tag: "Soon",
    enabled: false,
  },
  {
    mark: "E",
    title: "Event Probability Lens",
    description: "Planned: outcome markets and implied odds",
    tag: "Planned",
    enabled: false,
  },
  {
    mark: "L",
    title: "Leverage & Positioning Lens",
    description: "Planned: funding, OI, crowding and perp pressure",
    tag: "Planned",
    enabled: false,
  },
];

export const currentWork = [
  {
    name: "BTC range premium",
    tag: "Draft thesis",
    tagTone: "amber" as const,
    detail: "Exploring in PPE · expression not selected.",
  },
  {
    name: "Downside tail hedge",
    tag: "Confirmed",
    detail: "Expression saved · monitoring rules pending.",
  },
  {
    name: "Narrower-range thesis",
    tag: "Simulation",
    detail: "Simulated only · no live position connected.",
  },
];

export const headlines = [
  {
    title: "Volatility surface update",
    body: "BTC options width increased versus reference horizon.",
  },
  {
    title: "News context",
    body: "Macro calendar: two high-impact releases this week.",
  },
];

export const reviewEvents = [
  {
    title: "Review range candidate",
    body: "Outcome review due tomorrow.",
    tone: "teal" as const,
  },
  {
    title: "Trust warning",
    body: "Confirm data freshness on one saved thesis.",
    tone: "amber" as const,
  },
];
