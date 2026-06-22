/** Preview/fixture data for Command Center (fallback when live feeds are empty). */

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
  { id: "expression", label: "Expression & Execution", href: "/strategy-lab/expression" },
  { id: "monitor", label: "Monitor", href: "/monitor" },
  { id: "history", label: "History", href: "/history" },
  { id: "learn", label: "Learn", href: "/learn" },
];

export const calibrationStrip = {
  title: "Track how your views hold up",
  body: "Compare what you thought would happen with what actually happened — paper trading only for now.",
  cta: "Open monitor",
  href: "/monitor",
};

export const connectedMarkets: MarketAsset[] = [
  { label: "BTC options", status: "Live", live: true },
  { label: "ETH options", status: "Soon" },
  { label: "Event markets", status: "Planned" },
  { label: "Perp positioning", status: "Planned" },
];

export const kpis = [
  { label: "Draft ideas", value: "3", tone: "amber" as const, sub: "Pick up where you left off" },
  { label: "Confirmed views", value: "2", tone: "teal" as const, sub: "1 waiting for review" },
  { label: "Paper / live", value: "1 / 0", sub: "No live trades connected" },
  { label: "Reviews due", value: "4", tone: "red" as const, sub: "Check stale data on one idea" },
];

export const labTiles = [
  {
    mark: "B",
    title: "Strategy Lab",
    description: "Compare your view to what BTC options are pricing — live now",
    cta: "Open lab",
    enabled: true,
  },
  {
    mark: "E",
    title: "ETH options",
    description: "Same workflow — coming next",
    tag: "Soon",
    enabled: false,
  },
  {
    mark: "P",
    title: "Event markets",
    description: "Outcome markets and implied odds",
    tag: "Planned",
    enabled: false,
  },
  {
    mark: "L",
    title: "Positioning & funding",
    description: "Funding, open interest, and crowding",
    tag: "Planned",
    enabled: false,
  },
];

export const currentWork = [
  {
    name: "BTC range — vol looks rich",
    tag: "Draft",
    tagTone: "amber" as const,
    detail: "Exploring in Strategy Lab · no trade plan yet",
  },
  {
    name: "Downside tail hedge",
    tag: "Confirmed",
    detail: "Trade structure saved · alerts not set up yet",
  },
  {
    name: "Calmer-than-market view",
    tag: "Paper only",
    detail: "Simulated — not connected to a broker",
  },
];

export const headlines = [
  {
    title: "Volatility picked up",
    body: "BTC option ranges widened versus last week.",
  },
  {
    title: "Macro calendar",
    body: "Two high-impact releases this week — worth a glance before sizing.",
  },
];

export const reviewEvents = [
  {
    title: "Range trade idea",
    body: "Time to check whether your view still holds — review due tomorrow.",
    tone: "teal" as const,
  },
  {
    title: "Stale quote check",
    body: "One saved idea may be using older market data — refresh before sharing.",
    tone: "amber" as const,
  },
];
