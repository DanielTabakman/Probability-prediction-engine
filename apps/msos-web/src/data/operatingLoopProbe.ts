export const operatingLoopProbe = {
  label: "Operating Loop Probe v0",
  experiment: "OCT / Hummingbot test",
  mode: "Hybrid live / read-only",
  currentStage: "understand",
  stages: [
    { id: "observe", label: "Observe", status: "active" },
    { id: "understand", label: "Understand", status: "active" },
    { id: "decide", label: "Decide", status: "pending" },
    { id: "execute", label: "Execute", status: "pending" },
    { id: "learn", label: "Learn", status: "active" },
  ],
  observe: {
    title: "Signal Capture",
    status: "LIVE",
    detail: "Condor is persistently capturing live market observations and exposing read-only status to shared staging.",
  },
  understand: {
    title: "Multi-scale research question",
    status: "TESTING ACROSS SCALES",
    detail:
      "The first 15-minute NDAX window was too noisy for fine-grained structure, but that does not make NDAX globally useless. We are now applying the same relative structure detector across 5m, 15m, 1h, 4h, and 1d to learn where the feed becomes informative and which levels persist across zoom levels.",
  },
  decide: {
    title: "Scale selection",
    status: "NOT YET",
    detail:
      "Do not choose one timeframe in advance. Use the multi-scale evidence to decide which horizons are informative for context, local structure, and later decision timing.",
  },
  execute: {
    title: "Hummingbot",
    status: "READ ONLY",
    detail: "Execution remains outside this experiment while the structure representation is being tested.",
  },
  learn: {
    title: "Result",
    status: "FIRST LESSON RETAINED",
    detail:
      "Data quality is scale-dependent. The permanent insight is not that NDAX is bad; it is that its first 15-minute window was too noisy relative to the movement visible at that scale.",
  },
  nextAction: "Inspect the first multi-scale NDAX map: where does the feed change from poor to usable, and which support/resistance zones persist across more than one horizon?",
  successQuestion: "Does the multi-scale view reveal useful structure without forcing an arbitrary timeframe choice?",
} as const;
