export const operatingLoopProbe = {
  label: "Operating Loop Probe v0",
  experiment: "OCT / Hummingbot test",
  mode: "Hybrid live / read-only",
  currentStage: "decide",
  stages: [
    { id: "observe", label: "Observe", status: "active" },
    { id: "understand", label: "Understand", status: "active" },
    { id: "decide", label: "Decide", status: "active" },
    { id: "execute", label: "Execute", status: "pending" },
    { id: "learn", label: "Learn", status: "pending" },
  ],
  observe: {
    title: "Signal Capture",
    status: "LIVE",
    detail: "Condor is persistently capturing live market observations and exposing read-only status to shared staging.",
  },
  understand: {
    title: "Research conclusion",
    status: "FIRST CONCLUSION RECORDED",
    detail:
      "The OCT pipeline is successfully capturing and surfacing live SOL market data. In the first reviewed 15-minute NDAX window, the median spread was about 62 bps while the entire mid-price range was about 10 bps, with a 0.16 Hz L1 update rate and gaps up to about 25 seconds. That window is too wide and sparse for NDAX to be the primary feed for fine-grained support/resistance or execution timing. This is a first-window finding, not a permanent verdict on NDAX.",
  },
  decide: {
    title: "Signal / conclusion",
    status: "NO TRADE / CHANGE INPUT",
    detail:
      "Do not generate a trade from this window. Keep NDAX as a secondary venue-specific observation, and test support/resistance against a more liquid SOL reference feed before wiring strategy output to execution.",
  },
  execute: {
    title: "Hummingbot",
    status: "READ ONLY",
    detail: "Execution remains intentionally disabled. The next execution integration is health, portfolio, positions, and orders only.",
  },
  learn: {
    title: "Result",
    status: "FIRST LESSON",
    detail:
      "A live feed is not automatically a useful decision feed. Market quality must be measured before strategy logic is allowed to depend on it.",
  },
  nextAction: "Add or restore a more liquid SOL reference feed, then compare its 15-minute market quality with NDAX before starting support/resistance research.",
  successQuestion: "Does this screen make it easier to understand what we are doing, what is blocked, and what happens next?",
} as const;
