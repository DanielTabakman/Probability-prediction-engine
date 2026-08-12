export const operatingLoopProbe = {
  label: "Operating Loop Probe v0",
  experiment: "OCT / Hummingbot test",
  mode: "Fixture-backed / read-only",
  currentStage: "observe",
  stages: [
    { id: "observe", label: "Observe", status: "active" },
    { id: "understand", label: "Understand", status: "pending" },
    { id: "decide", label: "Decide", status: "pending" },
    { id: "execute", label: "Execute", status: "pending" },
    { id: "learn", label: "Learn", status: "pending" },
  ],
  observe: {
    title: "Signal Capture",
    status: "READY",
    detail: "oct-signal-capture is present locally. Live capture has not run yet.",
  },
  understand: {
    title: "Research question",
    status: "WAITING FOR DATA",
    detail: "Can the OCT signal pipeline capture useful live SOL market information and hand it cleanly toward execution?",
  },
  decide: {
    title: "Signal / conclusion",
    status: "NONE YET",
    detail: "No decision should be produced until the first live observation is captured and reviewed.",
  },
  execute: {
    title: "Hummingbot",
    status: "READ ONLY",
    detail: "Execution is intentionally disabled for this probe. The next integration is health, portfolio, positions, and orders only.",
  },
  learn: {
    title: "Result",
    status: "NO RESULT YET",
    detail: "We will record what happened only after one paper or deliberately tiny controlled execution reaches this stage.",
  },
  nextAction: "Start live signal capture from the normal Ubuntu/WSL shell.",
  successQuestion: "Does this screen make it easier to understand what we are doing, what is blocked, and what happens next?",
} as const;
