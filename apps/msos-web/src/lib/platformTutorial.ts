/** First-run platform tour — Strategy Lab walkthrough (display only). */

import { LAB_ASSET_QUERY_PARAM } from "@/lib/ppeDisplayPayload";

export const PLATFORM_TUTORIAL_STORAGE_KEY = "msos.platform.tutorial.completed.v1";
export const PLATFORM_TUTORIAL_QUERY = "tutorial";
export const PLATFORM_TUTORIAL_BEGINNER_QUERY = "beginner";
export const PLATFORM_TUTORIAL_FEEDBACK_FROM_QUERY = "from";
export const PLATFORM_TUTORIAL_FEEDBACK_FROM_TOUR = "tour";
export const PLATFORM_TUTORIAL_RETURN_TO_QUERY = "returnTo";

/** Guided tour always starts on a crypto lab asset (never last session stock pick). */
export const PLATFORM_TOUR_DEFAULT_ASSET = "BTC";

export type PlatformTutorialStep = {
  id: string;
  title: string;
  body: string;
  /** CSS selector for anchor element on Strategy Lab */
  anchor: string;
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
  },
  {
    id: "chart",
    title: "Read the curves",
    body: "Purple = what options imply today (Black–Scholes lognormal). Teal dashed = your belief overlay.",
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
  },
  {
    id: "chart",
    title: "Read the chart",
    body: "Purple = what the market believes. Teal = your view. You don't need every detail — just whether they look similar or different.",
    anchor: "[data-tour='lab-chart']",
  },
  {
    id: "confirm",
    title: "Lock your view",
    body: "When the chart matches your thinking, confirm — then we'll sketch a paper trade that fits. No real money moves.",
    anchor: "[data-tour='lab-confirm']",
  },
];

export function resolveTutorialSteps(beginner: boolean): PlatformTutorialStep[] {
  return beginner ? PLATFORM_TUTORIAL_BEGINNER_STEPS : PLATFORM_TUTORIAL_STEPS;
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
    searchParams.has(PLATFORM_TUTORIAL_QUERY) || searchParams.has(PLATFORM_TUTORIAL_BEGINNER_QUERY)
  );
}

export function stripTutorialSearchParams(searchParams: URLSearchParams): URLSearchParams {
  const next = new URLSearchParams(searchParams.toString());
  next.delete(PLATFORM_TUTORIAL_QUERY);
  next.delete(PLATFORM_TUTORIAL_BEGINNER_QUERY);
  return next;
}

export function resolveTutorialBeginnerMode(searchParams: URLSearchParams): boolean {
  return (
    searchParams.get(PLATFORM_TUTORIAL_BEGINNER_QUERY) === "1" ||
    searchParams.get(PLATFORM_TUTORIAL_QUERY) === "beginner"
  );
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

/** Force guided tour (homepage CTAs, restart). */
export function strategyLabForcedTourHref(beginner = false): string {
  const params = new URLSearchParams();
  params.set(LAB_ASSET_QUERY_PARAM, PLATFORM_TOUR_DEFAULT_ASSET);
  if (beginner) {
    params.set(PLATFORM_TUTORIAL_BEGINNER_QUERY, "1");
  } else {
    params.set(PLATFORM_TUTORIAL_QUERY, "1");
  }
  return `/strategy-lab?${params.toString()}`;
}
