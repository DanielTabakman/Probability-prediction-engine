/**
 * Command Center visitor copy — canon: docs/PRODUCT_COPY/packets/command-center.v1.md
 */

export const commandCenterMetadata = {
  title: "Command Center | Market Structure OS",
  description: "Track saved views and paper trades — reminders only, not trade advice.",
} as const;

export const commandCenterPageHeader = {
  crumb: "Home",
  title: "Command Center",
  shareButton: "Share",
  primaryCta: "Save a view",
} as const;

export const commandCenterStatusPills = {
  live: "Saved reads connected",
  empty: "No saved reads yet",
  degraded: "History offline",
} as const;

export const commandCenterCalibrationLinks = {
  history: "History",
  learn: "Learn",
} as const;

export const commandCenterCalibrationStrip = {
  title: "Track how your views hold up",
  bodyDefault:
    "Compare what you thought would happen with what actually happened — paper trading only for now.",
  bodyDegraded: "Saved history isn't connected yet — Strategy Lab live data still works.",
  bodyPending: (count: number) =>
    `${count} saved view${count === 1 ? "" : "s"} ready for review.`,
  cta: "Open Monitor",
  href: "/monitor",
} as const;

export const commandCenterStartHere = {
  title: "Start here",
  subtitle: "Open a market and compare it to your view.",
  tag: "Explore",
} as const;

export const commandCenterThesisPrompt = {
  title: "Have a view?",
  body: "Say what you think is mispriced. We'll keep your idea on file so you can plan and review later.",
  cta: "Save a view →",
} as const;

export const commandCenterRecentWork = {
  title: "Recent work",
  subtitle: "Saved market reads and review status.",
  degradedNote: "Saved history isn't loading yet. Strategy Lab still has live data.",
  emptyNote: "Nothing saved yet — start in Strategy Lab.",
} as const;

export const commandCenterContextPanel = {
  title: "Context & alerts",
  subtitle: "News and reminders that might change your view.",
  reviewLabel: "To review",
} as const;

export const commandCenterNavItems = [
  { id: "command-center", label: "Command Center", href: "/command-center" },
  { id: "strategy-lab", label: "Strategy Lab", href: "/strategy-lab" },
  { id: "theses", label: "Theses", href: "#", disabled: true },
  { id: "expression", label: "Plan a trade", href: "/strategy-lab/expression" },
  { id: "monitor", label: "Monitor", href: "/monitor" },
  { id: "history", label: "History", href: "/history" },
  { id: "learn", label: "Learn", href: "/learn" },
] as const;

export const commandCenterConnectedMarkets = [
  { label: "BTC options", status: "Live", live: true },
  { label: "ETH options", status: "Soon" },
  { label: "Event markets", status: "Planned" },
  { label: "Perp positioning", status: "Planned" },
] as const;

export const commandCenterKpis = [
  { label: "Draft ideas", value: "3", tone: "amber" as const, sub: "Pick up where you left off" },
  { label: "Confirmed views", value: "2", tone: "teal" as const, sub: "1 waiting for review" },
  { label: "Paper / live", value: "1 / 0", sub: "No live trades connected" },
  { label: "Reviews due", value: "4", tone: "red" as const, sub: "Check stale data on one idea" },
];

export const commandCenterLabTiles = [
  {
    mark: "B",
    title: "Strategy Lab",
    description: "Compare your view to what BTC options are pricing — live now",
    cta: "Try the lab",
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
] as const;

export const commandCenterCurrentWork = [
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
] as const;

export const commandCenterHeadlines = [
  {
    title: "Volatility picked up",
    body: "BTC option ranges widened versus last week.",
  },
  {
    title: "Macro calendar",
    body: "Two high-impact releases this week — worth a glance before sizing.",
  },
] as const;

export const commandCenterReviewEvents = [
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
] as const;
