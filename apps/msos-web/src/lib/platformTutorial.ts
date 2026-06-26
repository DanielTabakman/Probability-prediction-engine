/** First-run platform tour — Strategy Lab walkthrough (display only). */

export const PLATFORM_TUTORIAL_STORAGE_KEY = "msos.platform.tutorial.completed.v1";
export const PLATFORM_TUTORIAL_QUERY = "tutorial";
export const PLATFORM_TUTORIAL_BEGINNER_QUERY = "beginner";

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

export function strategyLabTutorialHref(force = false): string {
  if (force || !isPlatformTutorialComplete()) {
    return `/strategy-lab?${PLATFORM_TUTORIAL_QUERY}=1`;
  }
  return "/strategy-lab";
}
