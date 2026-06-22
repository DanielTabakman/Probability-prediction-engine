/** Learn / reflection page copy. */

export const conclusionHeadline = "What did you take away?";

export const conclusionNarrative = {
  lead: "Compare what you believe with what the market is pricing — then plan, paper-trade, and review.",
  body:
    "You walked through the market read, stated a view, sketched a paper trade, and checked Monitor and History. The goal is clarity, not hot tips.",
};

export const learnLoopSteps = [
  { id: "read", label: "Read the market", detail: "Strategy Lab · live BTC options" },
  { id: "thesis", label: "State your view", detail: "Confirm in plain language" },
  { id: "express", label: "Plan a trade", detail: "Paper only — no live order" },
  { id: "monitor", label: "Watch & review", detail: "Track ideas over time" },
  { id: "learn", label: "Reflect", detail: "Note what clicked and what didn't" },
];

export const testerMetricsTemplate = [
  {
    metric: "Clarity",
    prompt: "Could you explain the main chart to a friend in five minutes?",
    fixture: "Your notes",
  },
  {
    metric: "Honesty",
    prompt: "Did the confirmation step feel straightforward — no hidden “AI says buy”?",
    fixture: "Your notes",
  },
  {
    metric: "Would return",
    prompt: "Would you open Monitor or History again this week?",
    fixture: "Your notes",
  },
  {
    metric: "Worth paying for",
    prompt: "Would beta access or a research brief be worth it? (optional)",
    fixture: "Optional — tell us in feedback",
  },
];

export const nextSelectionRecommendation = {
  title: "What's next",
  recommendation:
    "Keep exploring the live demo. Share feedback on anything confusing — we're prioritizing clarity for new options traders.",
  notNow: "Live brokerage routing and paid tiers are not open yet.",
};
