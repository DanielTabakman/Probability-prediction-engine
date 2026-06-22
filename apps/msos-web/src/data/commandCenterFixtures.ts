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

export {
  commandCenterConnectedMarkets as connectedMarkets,
  commandCenterCurrentWork as currentWork,
  commandCenterHeadlines as headlines,
  commandCenterKpis as kpis,
  commandCenterLabTiles as labTiles,
  commandCenterNavItems as navItems,
  commandCenterReviewEvents as reviewEvents,
} from "@/content/commandCenter";

/** @deprecated Import from @/content/commandCenter — kept for legacy imports */
export { commandCenterCalibrationStrip as calibrationStrip } from "@/content/commandCenter";
