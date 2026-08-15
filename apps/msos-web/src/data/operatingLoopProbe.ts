export const operatingLoopProbe = {
  label: "Team Research Console v0",
  experiment: "Persistent-level forward validation v0",
  mode: "Live evidence / deterministic research / no execution",
  currentStage: "understand",
  stages: [
    { id: "observe", label: "Observe", status: "active" },
    { id: "understand", label: "Validate", status: "active" },
    { id: "decide", label: "Strategy", status: "pending" },
    { id: "execute", label: "Execute", status: "pending" },
    { id: "learn", label: "Learn", status: "pending" },
  ],
  observe: {
    title: "Market observations",
    status: "LIVE / VERIFYING FRESHNESS",
    detail: "Signal Capture owns normalized observations and freshness. The current blocker is keeping the active NDAX index continuously readable for short-horizon research.",
  },
  understand: {
    title: "Current research question",
    status: "FORWARD VALIDATION",
    detail:
      "Do persistent multi-scale price levels contain useful information about what price does afterward? Freeze the detector at time T, observe future reactions, and compare them with matched control levels.",
  },
  decide: {
    title: "Strategy expression",
    status: "NOT YET",
    detail:
      "Do not create a trading rule until the frozen structure hypothesis shows useful information versus the baseline. If it survives, Hummingbot becomes the strategy-backtest layer.",
  },
  execute: {
    title: "Hummingbot",
    status: "NOT AUTHORIZED",
    detail: "No live execution is part of Team Research Console v0. Hummingbot is reserved for later strategy backtesting, paper trading, and separately approved execution.",
  },
  learn: {
    title: "Saved experiment results",
    status: "WAITING FOR FIRST REAL RUN",
    detail:
      "Each run should preserve detector version, data source, detection time, forward window, baseline, raw counts, and PASS / FAIL / INCONCLUSIVE so the team can reproduce and discuss the evidence.",
  },
  nextAction: "Verify fresh NDAX observations, then run the frozen 4-hour persistent-level experiment against the matched baseline.",
  successQuestion: "Do persistent multi-scale levels react more often than matched control levels out of sample?",
} as const;
