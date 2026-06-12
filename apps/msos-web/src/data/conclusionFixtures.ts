/** Preview/fixture data for conclusion / learn loop (P8 — friends-first tester release). */

export const conclusionHeadline = "What did you learn from this run?";

export const conclusionNarrative = {
  lead: "MSOS is a research demo — capture comprehension signals before widening scope or commercial packaging.",
  body:
    "You moved from market read → thesis → expression plan → monitor/history. The learn loop closes when a tester can explain the disagreement readout without jargon.",
};

export const learnLoopSteps = [
  { id: "read", label: "Read surfaces", detail: "Strategy Lab + PPE embed" },
  { id: "thesis", label: "State thesis", detail: "Confirm what you think is true" },
  { id: "express", label: "Plan expression", detail: "Sim-only — no live order" },
  { id: "monitor", label: "Monitor & review", detail: "Fixture watch panels" },
  { id: "learn", label: "Learn loop", detail: "Record signals below" },
];

export const testerMetricsTemplate = [
  {
    metric: "Comprehension",
    prompt: "Could the tester name the main object in ~5 min?",
    fixture: "Pending — log in VALIDATION_REALITY_CHECKS; rollup in MSOS_P8_VALIDATION_REPORT_V1",
  },
  {
    metric: "Thesis confirm",
    prompt: "Did confirmation copy feel honest (no hidden authority)?",
    fixture: "Pending",
  },
  {
    metric: "Return monitoring",
    prompt: "Would they open monitor/history again within a week?",
    fixture: "Pending",
  },
  {
    metric: "Paid interest",
    prompt: "Willingness to pay for beta/brief/call (steward call required)",
    fixture: "Not recorded — no auto-widening",
  },
];

export const nextSelectionRecommendation = {
  title: "Next SELECTION recommendation (preview)",
  recommendation:
    "Hold MSOS scope at friends-first tester release. Run guided sessions; log rows in VALIDATION_REALITY_CHECKS; complete MSOS_P8_VALIDATION_REPORT_V1 when the cohort checkpoint is met.",
  notNow: "No paywall or execution program expansion without new steward SELECTION.",
};
