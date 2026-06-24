/** First-run platform tour — Strategy Lab walkthrough (display only). */

export const PLATFORM_TUTORIAL_STORAGE_KEY = "msos.platform.tutorial.completed.v1";
export const PLATFORM_TUTORIAL_QUERY = "tutorial";

export type PlatformTutorialStep = {
  id: string;
  title: string;
  body: string;
  /** CSS selector for anchor element on Strategy Lab */
  anchor: string;
};

export const PLATFORM_TUTORIAL_STEPS: PlatformTutorialStep[] = [
  {
    id: "expiry",
    title: "Pick an expiry",
    body: "Choose when your view applies. The chart and metrics update to that BTC options expiry.",
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

export function strategyLabTutorialHref(force = false): string {
  if (force || !isPlatformTutorialComplete()) {
    return `/strategy-lab?${PLATFORM_TUTORIAL_QUERY}=1`;
  }
  return "/strategy-lab";
}
