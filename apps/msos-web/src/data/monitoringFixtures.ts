/** Preview/fixture data for Monitor surface (P7 — no live fills). */

export const monitorHero = {
  title: "Thesis & expression monitor",
  subtitle: "Fixture state only — observed / saved / simulated distinctions; no live execution feed.",
  healthLabel: "Composite watch status",
  healthPct: 62,
};

export const watchPanels = [
  {
    id: "thesis-validity",
    title: "Thesis validity",
    body: "Confirmed BTC narrower-range thesis still within stated horizon. No automatic invalidation.",
    tone: "teal" as const,
  },
  {
    id: "expression-risk",
    title: "Expression risk",
    body: "Simulated range expression saved — margin and gap risk shown as preview placeholders only.",
    tone: "amber" as const,
  },
  {
    id: "data-trust",
    title: "Data & trust",
    body: "PPE embed healthy in preview. Trust context: Good (fixture). Refresh cadence not live.",
    tone: "teal" as const,
  },
];

export const monitorAlerts = [
  {
    title: "Review queue item",
    body: "Outcome review due tomorrow for narrower-range candidate.",
    tone: "teal" as const,
  },
  {
    title: "Trust check",
    body: "Confirm data freshness on one saved thesis before sharing externally.",
    tone: "amber" as const,
  },
];
