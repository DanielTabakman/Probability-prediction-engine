/** First-run platform tour — Strategy Lab walkthrough (display only). */

import { LAB_ASSET_QUERY_PARAM } from "@/lib/ppeDisplayPayload";

export const PLATFORM_TUTORIAL_STORAGE_KEY = "msos.platform.tutorial.completed.v1";
export const PLATFORM_TUTORIAL_QUERY = "tutorial";
export const PLATFORM_TUTORIAL_BEGINNER_QUERY = "beginner";
export const PLATFORM_TUTORIAL_QUICK_QUERY = "quick";
export const PLATFORM_TUTORIAL_FULL_QUERY = "full";
export const PLATFORM_TUTORIAL_FEEDBACK_FROM_QUERY = "from";
export const PLATFORM_TUTORIAL_FEEDBACK_FROM_TOUR = "tour";
export const PLATFORM_TUTORIAL_RETURN_TO_QUERY = "returnTo";

/** Guided tour always starts on a crypto lab asset (never last session stock pick). */
export const PLATFORM_TOUR_DEFAULT_ASSET = "BTC";

export type PlatformTutorialPlayAction = "belief-nudge";

export type PlatformTutorialMode = "standard" | "beginner" | "quick" | "full";

export type PlatformTutorialStep = {
  id: string;
  title: string;
  body: string;
  /** Shown after playAction is satisfied (tutorial through play). */
  bodyAfterPlay?: string;
  /** CSS selector for anchor element on Strategy Lab */
  anchor: string;
  /** When set, Next is disabled until the user performs the action in the lab. */
  playAction?: PlatformTutorialPlayAction;
  /** Hint when playAction is pending */
  playHint?: string;
};

const BELIEF_PLAY: Pick<
  PlatformTutorialStep,
  "playAction" | "playHint" | "bodyAfterPlay"
> = {
  playAction: "belief-nudge",
  playHint: "Tap Higher, Lower, or a vol button in the spotlight to continue.",
  bodyAfterPlay:
    "Teal moved — that's your disagreement with the purple market curve. Sliders fine-tune if needed.",
};

export const PLATFORM_TUTORIAL_STEPS: PlatformTutorialStep[] = [
  {
    id: "asset",
    title: "BTC or ETH",
    body: "Switch crypto asset here — the same implied-distribution workflow runs for BTC and ETH options on Deribit.",
    anchor: "[data-tour='lab-asset']",
  },
  {
    id: "expiry",
    title: "Pick an expiry",
    body: "Choose when your view applies. You'll see today's price, what options imply for that date, and the typical range — then the chart updates.",
    anchor: "[data-tour='lab-expiry']",
  },
  {
    id: "belief",
    title: "State your disagreement",
    body: "Tap Higher/Lower for price and More/Less vol. Each push nudges the teal belief curve versus purple market.",
    anchor: "[data-tour='lab-belief']",
    ...BELIEF_PLAY,
  },
  {
    id: "chart",
    title: "Read the curves",
    body: "Purple = what options imply today. Teal dashed = your belief overlay — look for gap or overlap.",
    anchor: "[data-tour='lab-chart']",
  },
  {
    id: "tuning",
    title: "Fine-tune if needed",
    body: "Sliders stay within demo-safe bounds — they re-scale forward and ATM vol on the market curve, not a custom tail model.",
    anchor: "[data-tour='lab-tuning']",
  },
  {
    id: "confirm",
    title: "Confirm when ready",
    body: "Save your view, then explore paper-trade structures that fit your thesis.",
    anchor: "[data-tour='lab-confirm']",
  },
];

export const PLATFORM_TUTORIAL_BEGINNER_STEPS: PlatformTutorialStep[] = [
  {
    id: "asset",
    title: "Pick BTC or ETH",
    body: "Both use the same tour — switch anytime if you care about ETH options instead of BTC.",
    anchor: "[data-tour='lab-asset']",
  },
  {
    id: "expiry",
    title: "Pick a date",
    body: "Choose when your idea applies. You'll see today's price and what the market expects on that date.",
    anchor: "[data-tour='lab-expiry']",
  },
  {
    id: "belief",
    title: "Say how you disagree",
    body: "Tap Higher/Lower if you think price lands above or below what options imply. Tap More/Less vol if you expect a wider or calmer range.",
    anchor: "[data-tour='lab-belief']",
    ...BELIEF_PLAY,
    bodyAfterPlay:
      "Teal moved — that's your view on the chart. You don't need every detail — just whether it looks similar or different from purple.",
  },
  {
    id: "chart",
    title: "Read the chart",
    body: "Purple = what the market believes. Teal = your view.",
    anchor: "[data-tour='lab-chart']",
  },
  {
    id: "confirm",
    title: "Lock your view",
    body: "When the chart matches your thinking, confirm — then we'll sketch a paper trade that fits. No real money moves.",
    anchor: "[data-tour='lab-confirm']",
  },
];

/** ~15s wedge — expiry, one belief nudge, chart, confirm (BTC default asset). */
export const PLATFORM_TUTORIAL_QUICK_STEPS: PlatformTutorialStep[] = [
  {
    id: "expiry",
    title: "Pick when your view applies",
    body: "Choose an expiry — the chart and headline read update for that date.",
    anchor: "[data-tour='lab-expiry']",
  },
  {
    id: "belief",
    title: "One disagreement tap",
    body: "Tap Higher or Lower once — watch the teal curve move against purple market.",
    anchor: "[data-tour='lab-belief']",
    ...BELIEF_PLAY,
    bodyAfterPlay: "That's the wedge — market-implied versus your view on one screen.",
  },
  {
    id: "chart",
    title: "Read the gap",
    body: "Purple = market. Teal = you. Similar curves = aligned; separated = disagreement to explore.",
    anchor: "[data-tour='lab-chart']",
  },
  {
    id: "confirm",
    title: "Save when it matches",
    body: "Confirm locks the view for paper-trade planning — still no live orders.",
    anchor: "[data-tour='lab-confirm']",
  },
];

/** Spine extension — full trader loop (opt-in via ?tutorial=full). */
export const PLATFORM_TUTORIAL_SPINE_STEPS: PlatformTutorialStep[] = [
  {
    id: "horizon",
    title: "Region thesis on Horizon",
    body: "Chart a price × time region on Options Horizon — drag a box, read implied mass, then return here to express the thesis.",
    anchor: "[data-tour='lab-horizon-nav']",
  },
  {
    id: "export",
    title: "Download distribution stats",
    body: "Export CSV for your journal or offline research — requires live chain data.",
    anchor: "[data-tour='lab-distribution-export']",
  },
  {
    id: "review-loop",
    title: "Save, then review later",
    body: "After you confirm a view, use Monitor and History to track reads and post-mortem reviews — come back without a scheduled demo.",
    anchor: "[data-tour='lab-workflow-review']",
  },
];

export function resolveTutorialSteps(mode: PlatformTutorialMode): PlatformTutorialStep[] {
  switch (mode) {
    case "beginner":
      return PLATFORM_TUTORIAL_BEGINNER_STEPS;
    case "quick":
      return PLATFORM_TUTORIAL_QUICK_STEPS;
    case "full":
      return [...PLATFORM_TUTORIAL_STEPS, ...PLATFORM_TUTORIAL_SPINE_STEPS];
    default:
      return PLATFORM_TUTORIAL_STEPS;
  }
}

export function isPlatformTutorialComplete(): boolean {
  if (typeof window === "undefined") return true;
  try {
    return window.localStorage.getItem(PLATFORM_TUTORIAL_STORAGE_KEY) === "1";
  } catch {
    return true;
  }
}

export function markPlatformTutorialComplete(): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(PLATFORM_TUTORIAL_STORAGE_KEY, "1");
  } catch {
    /* ignore quota */
  }
}

export function clearPlatformTutorialComplete(): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(PLATFORM_TUTORIAL_STORAGE_KEY);
  } catch {
    /* ignore */
  }
}

export function hasTutorialSearchParams(searchParams: URLSearchParams): boolean {
  return (
    searchParams.has(PLATFORM_TUTORIAL_QUERY) ||
    searchParams.has(PLATFORM_TUTORIAL_BEGINNER_QUERY) ||
    searchParams.has(PLATFORM_TUTORIAL_QUICK_QUERY) ||
    searchParams.has(PLATFORM_TUTORIAL_FULL_QUERY)
  );
}

export function stripTutorialSearchParams(searchParams: URLSearchParams): URLSearchParams {
  const next = new URLSearchParams(searchParams.toString());
  next.delete(PLATFORM_TUTORIAL_QUERY);
  next.delete(PLATFORM_TUTORIAL_BEGINNER_QUERY);
  next.delete(PLATFORM_TUTORIAL_QUICK_QUERY);
  next.delete(PLATFORM_TUTORIAL_FULL_QUERY);
  return next;
}

export function resolveTutorialBeginnerMode(searchParams: URLSearchParams): boolean {
  return (
    searchParams.get(PLATFORM_TUTORIAL_BEGINNER_QUERY) === "1" ||
    searchParams.get(PLATFORM_TUTORIAL_QUERY) === "beginner"
  );
}

export function resolveTutorialMode(searchParams: URLSearchParams): PlatformTutorialMode {
  if (resolveTutorialBeginnerMode(searchParams)) {
    return "beginner";
  }
  const tutorial = searchParams.get(PLATFORM_TUTORIAL_QUERY)?.trim().toLowerCase();
  if (tutorial === "quick" || searchParams.get(PLATFORM_TUTORIAL_QUICK_QUERY) === "1") {
    return "quick";
  }
  if (tutorial === "full" || searchParams.get(PLATFORM_TUTORIAL_FULL_QUERY) === "1") {
    return "full";
  }
  return "standard";
}

/** Strategy Lab entry — first visit auto-opens tour via localStorage. */
export function strategyLabTutorialHref(): string {
  return "/strategy-lab";
}

function isSafeReturnPath(path: string): boolean {
  return path.startsWith("/") && !path.startsWith("//");
}

/** Post-tour feedback — optional; includes return path so skip brings user back. */
export function platformTourFeedbackHref(returnTo?: string): string {
  const params = new URLSearchParams();
  params.set(PLATFORM_TUTORIAL_FEEDBACK_FROM_QUERY, PLATFORM_TUTORIAL_FEEDBACK_FROM_TOUR);
  if (returnTo && isSafeReturnPath(returnTo)) {
    params.set(PLATFORM_TUTORIAL_RETURN_TO_QUERY, returnTo);
  }
  return `/feedback?${params.toString()}`;
}

export function isTourFeedbackEntry(searchParams: URLSearchParams): boolean {
  return searchParams.get(PLATFORM_TUTORIAL_FEEDBACK_FROM_QUERY) === PLATFORM_TUTORIAL_FEEDBACK_FROM_TOUR;
}

export function resolveTourFeedbackReturnTo(
  searchParams: URLSearchParams,
  fallback = "/strategy-lab",
): string {
  const raw = searchParams.get(PLATFORM_TUTORIAL_RETURN_TO_QUERY)?.trim();
  if (raw && isSafeReturnPath(raw)) {
    return raw;
  }
  return fallback;
}

export function buildTourReturnPath(pathname: string, searchParams: URLSearchParams): string {
  const next = stripTutorialSearchParams(searchParams);
  const qs = next.toString();
  return qs ? `${pathname}?${qs}` : pathname;
}

export type ForcedTourOptions = {
  beginner?: boolean;
  quick?: boolean;
  full?: boolean;
};

/** Force guided tour (homepage CTAs, restart). */
export function strategyLabForcedTourHref(options: ForcedTourOptions = {}): string {
  const params = new URLSearchParams();
  params.set(LAB_ASSET_QUERY_PARAM, PLATFORM_TOUR_DEFAULT_ASSET);
  if (options.beginner) {
    params.set(PLATFORM_TUTORIAL_BEGINNER_QUERY, "1");
  } else if (options.quick) {
    params.set(PLATFORM_TUTORIAL_QUERY, "quick");
  } else if (options.full) {
    params.set(PLATFORM_TUTORIAL_QUERY, "full");
  } else {
    params.set(PLATFORM_TUTORIAL_QUERY, "1");
  }
  return `/strategy-lab?${params.toString()}`;
}
