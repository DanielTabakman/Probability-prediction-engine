/** Preview/fixture data for Command Center (fallback when live feeds are empty). */

export type NavItem = {
  id: string;
  label: string;
  href: string;
  active?: boolean;
  disabled?: boolean;
};

export type ModuleCard = {
  mark: string;
  title: string;
  description: string;
  cta: string;
  href: string;
  live?: boolean;
};

export type PlannedModule = {
  label: string;
  status: string;
};

export const navItems: NavItem[] = [
  { id: "command-center", label: "Command Center", href: "/command-center" },
  { id: "strategy-lab", label: "Strategy Lab", href: "/strategy-lab" },
  { id: "monitor", label: "Monitor", href: "/monitor" },
  { id: "history", label: "History", href: "/history" },
];

/** Secondary destinations — linked from sidebar footer, not primary nav. */
export const secondaryNavItems: NavItem[] = [
  { id: "exposure", label: "Exposure menu", href: "/exposure" },
  { id: "options-horizon", label: "Options Horizon", href: "/options-horizon" },
  { id: "forward-consistency", label: "Forward consistency", href: "/forward-consistency" },
  { id: "learn", label: "Learn", href: "/learn" },
];

/** Registry-aligned module launch cards — one card per tool, not per asset. */
export const moduleCards: ModuleCard[] = [
  {
    mark: "L",
    title: "Strategy Lab",
    description: "Compare your view to what options are pricing",
    cta: "Open lab",
    href: "/strategy-lab",
    live: true,
  },
  {
    mark: "H",
    title: "Options Horizon",
    description: "Chart price × time and drag a region you care about",
    cta: "Open chart",
    href: "/options-horizon",
    live: true,
  },
  {
    mark: "E",
    title: "Exposure menu",
    description: "Paths to express your view — spot, options, and more",
    cta: "Browse paths",
    href: "/exposure",
    live: true,
  },
];

/** Future modules — progressive disclosure on home, not primary launch cards. */
export const plannedModules: PlannedModule[] = [
  { label: "Event markets", status: "Planned" },
  { label: "Perp positioning", status: "Planned" },
];
