export const operatingLoopProbe = {
  label: "Team Research Console v0",
  experiment: "Persistent-level forward validation v0",
  mode: "Live evidence / deterministic research / no execution",
  currentStage: "validate",
  stages: [
    { id: "detect", label: "Detect", status: "done", detail: "Recurring multi-scale levels found" },
    { id: "validate", label: "Validate", status: "done", detail: "No predictive edge demonstrated" },
    { id: "strategy", label: "Strategy", status: "blocked", detail: "v0 does not advance" },
    { id: "backtest", label: "Backtest", status: "blocked", detail: "No validated strategy" },
    { id: "trade", label: "Trade", status: "blocked", detail: "Not authorized" },
  ],
  researchStatus: {
    status: "NOT VALIDATED",
    headline: "V0 did not demonstrate an edge",
    summary:
      "We successfully detected recurring multi-scale price levels and then tested them against matched control levels. In the first complete batch with enough touches, our detected levels reacted slightly less often than the controls. The confidence interval is wide enough that we cannot call a formal FAIL, but v0 has not earned promotion to a trading strategy.",
    whatWeKnow:
      "The data pipeline, detector, historical replay, controls, prospective holdout, and batch test all work. We now have a complete 168-window sample with enough touches to run the predeclared inference.",
    whatWeDoNotKnow:
      "Whether a different market-structure hypothesis contains an edge. V0 only tested this specific persistent-level definition and reaction rule; it does not disprove support/resistance in general.",
    nextAction:
      "Stop v0 here. Preserve the evidence. If research continues, define a genuinely new v1 hypothesis before looking at another test sample rather than tuning v0 after the result.",
  },
  primaryEvidence: {
    label: "PRIMARY UNTOUCHED BATCH v0.1",
    market: "SOL/CAD · NDAX",
    sample: "July 18–August 14, 2026",
    windows: 168,
    usableRows: "41,761 / 41,761 historical rows usable",
    detectedTouched: 144,
    detectedReacted: 24,
    detectedReactionRate: 0.1667,
    controlTouched: 137,
    controlReacted: 26,
    controlReactionRate: 0.1898,
    delta: -0.0231,
    ciLower: -0.105642,
    ciUpper: 0.058834,
    verdict: "INCONCLUSIVE",
    interpretation:
      "This was the first complete batch with enough events to judge v0. Detected levels reacted 16.7% of the time after touch versus 19.0% for matched controls. The point estimate is negative and the 95% interval crosses zero, so v0 shows no demonstrated edge and does not advance to Hummingbot.",
    witnessUrl:
      "https://github.com/DanielTabakman/market-structure-engine/issues/15#issuecomment-5305887336",
    artifactUrl:
      "https://github.com/DanielTabakman/market-structure-engine/actions/runs/31928722113/artifacts/9258661760",
    artifactLabel: "untouched-jul18-aug14-batch-v0.1.zip",
    artifactSha256: "8b7168bd485a852bdc2a6f9d345a93800eb153415e751de37594aefe5dc91b00",
  },
  priorEvidence: [
    {
      label: "Historical pilot · July 15–18",
      result: "UNDERPOWERED · NO EDGE SHOWN",
      detail: "12 windows. Detected levels reacted 10.0% after touch versus 18.2% for controls. Too few touches per window for a formal PASS/FAIL call.",
    },
    {
      label: "Prospective holdout · August 15",
      result: "UNDERPOWERED",
      detail: "Clean future window completed with valid data, but neither detected levels nor controls were touched. This tested the live loop, not the hypothesis strongly enough.",
    },
    {
      label: "June expansion attempt",
      result: "DATA UNAVAILABLE",
      detail: "NDAX historical retention covered only 36 of 180 predeclared windows. The partial subset was not used for a scientific conclusion.",
    },
  ],
  observe: {
    title: "Live market data",
    status: "LIVE",
    detail:
      "Signal Capture is producing continuously readable NDAX observations. Live detected levels remain research observations, not validated signals.",
  },
  understand: {
    title: "Does detected structure matter?",
    status: "V0 COMPLETE",
    detail:
      "For v0, the answer is: no edge demonstrated. A complete 168-window sample put the detector slightly behind matched controls and the confidence interval crossed zero.",
  },
  decide: {
    title: "Strategy expression",
    status: "BLOCKED FOR V0",
    detail:
      "Do not create a trading rule from v0. If a newly predeclared v1 research hypothesis later survives validation, Hummingbot becomes the strategy-backtest layer.",
  },
  execute: {
    title: "Hummingbot backtest / execution",
    status: "BLOCKED FOR V0",
    detail:
      "There is no validated v0 signal to backtest or trade. Hummingbot remains downstream of research validation.",
  },
  learn: {
    title: "What we learned",
    status: "V0 COMPLETE",
    detail:
      "Recurring-looking market structure is not enough. When v0 was tested against a matched baseline with enough events, it did not outperform. The research console is doing its job by stopping weak ideas before strategy deployment.",
  },
  nextAction:
    "Archive v0 as NOT VALIDATED / NO EDGE DEMONSTRATED. If continuing, write a new v1 hypothesis before inspecting another sample.",
  successQuestion: "Do persistent multi-scale levels react more often than matched control levels out of sample?",
} as const;
