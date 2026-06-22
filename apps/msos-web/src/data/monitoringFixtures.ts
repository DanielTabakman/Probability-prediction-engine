/** Monitor surface fallback copy (no live fills). */

export const monitorHero = {
  title: "Monitor",
  subtitle: "Watch your saved views and paper trades — no live order feed yet.",
  healthLabel: "Overall watch status",
  healthPct: 62,
};

export const watchPanels = [
  {
    id: "thesis-validity",
    title: "Your view still valid?",
    body: "Your “calmer than market” view is still inside the range you set.",
    tone: "teal" as const,
  },
  {
    id: "expression-risk",
    title: "Structure risk",
    body: "Paper range trade on file — margin and gap risk shown as placeholders.",
    tone: "amber" as const,
  },
  {
    id: "data-trust",
    title: "Market data",
    body: "Options quotes look healthy. Refresh cadence is demo-mode.",
    tone: "teal" as const,
  },
];

export const monitorAlerts = [
  {
    title: "Review due",
    body: "Check whether your range idea still matches the market — due tomorrow.",
    tone: "teal" as const,
  },
  {
    title: "Data check",
    body: "Confirm quotes are fresh on one saved idea before sharing it.",
    tone: "amber" as const,
  },
];
