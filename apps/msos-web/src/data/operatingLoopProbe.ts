export const operatingLoopProbe = {
  label: "Team Research Console v0",
  experiment: "Persistent-level forward validation v0",
  mode: "Live evidence / deterministic research / no execution",
  currentStage: "validate",
  stages: [
    { id: "detect", label: "Detect", status: "active" },
    { id: "validate", label: "Validate", status: "active" },
    { id: "strategy", label: "Strategy", status: "pending" },
    { id: "backtest", label: "Backtest", status: "pending" },
    { id: "trade", label: "Trade", status: "pending" },
  ],
  researchStatus: {
    status: "UNVALIDATED",
    headline: "No edge shown yet",
    summary:
      "The detector can find recurring multi-scale price levels, but the first historical validation did not show that those levels predict reactions better than matched control levels. We are still in research, not strategy deployment.",
    whatWeKnow:
      "The data pipeline, detector, controls, and historical replay all work end to end. The detector finds recurring structure across scales.",
    whatWeDoNotKnow:
      "Whether those detected levels contain useful forward information. The first 12 historical windows were too sparse for a PASS/FAIL verdict and controls were numerically ahead.",
    nextAction:
      "Run the predeclared prospective holdout unchanged. After that, predeclare a larger historical sample if the experiment is still underpowered.",
  },
  retrospectiveEvidence: {
    label: "RETROSPECTIVE v0",
    market: "SOL/CAD · NDAX",
    sample: "July 15–18, 2026",
    windows: 12,
    usableRows: "4,321 / 4,321 historical rows usable",
    detectedReactionRate: 0.1,
    controlReactionRate: 0.1818,
    delta: -0.0818,
    pass: 0,
    fail: 0,
    inconclusive: 12,
    interpretation:
      "This sample does not support the hypothesis. Detected levels reacted less often than the matched controls in the pooled descriptive counts, while each individual window lacked enough touches to make a formal PASS/FAIL call.",
    witnessUrl:
      "https://github.com/DanielTabakman/market-structure-engine/pull/13#issuecomment-5304784244",
    artifactUrl:
      "https://github.com/DanielTabakman/market-structure-engine/actions/runs/31915449009/artifacts/9254777343",
    artifactLabel: "retrospective-replay-v0.zip",
    artifactSha256: "00061c59fda327a279d87ceef08b838ad7a9e2e4791e547a51a60fb493ebefc9",
  },
  observe: {
    title: "Live market data",
    status: "LIVE",
    detail:
      "Signal Capture is producing continuously readable NDAX observations. Data freshness is no longer the current research blocker.",
  },
  understand: {
    title: "Does detected structure matter?",
    status: "VALIDATING",
    detail:
      "The current hypothesis is that persistent multi-scale price levels contain useful information about future price behavior. We test that against matched control levels before creating any trading rule.",
  },
  decide: {
    title: "Strategy expression",
    status: "NOT YET",
    detail:
      "Do not turn detected levels into a trading strategy until forward evidence beats the baseline. If the research survives validation, Hummingbot becomes the strategy-backtest layer.",
  },
  execute: {
    title: "Hummingbot backtest / execution",
    status: "NOT YET",
    detail:
      "Hummingbot is reserved for strategy backtesting, paper trading, and separately approved execution after the research hypothesis earns that step.",
  },
  learn: {
    title: "What we learned",
    status: "1 HISTORICAL BATCH COMPLETE",
    detail:
      "The first 12 historical windows produced no positive evidence. The experiment is sparse: only one or two qualifying persistent levels usually exist at a time, so individual four-hour windows rarely contain enough touches for a verdict.",
  },
  nextAction:
    "Run the prospective holdout with the detector and validation rules unchanged. Do not tune around the historical result.",
  successQuestion: "Do persistent multi-scale levels react more often than matched control levels out of sample?",
} as const;
