/** Preview/fixture data for History surface (P7). */

export type HistoryState = "observed" | "saved" | "simulated" | "executed" | "reviewed";

export type HistoryEntry = {
  id: string;
  title: string;
  state: HistoryState;
  timestamp: string;
  detail: string;
};

export const historyIntro =
  "Lifecycle history uses preview fixtures — executed rows are empty until live routing exists.";

export const historyEntries: HistoryEntry[] = [
  {
    id: "h1",
    title: "BTC range premium — distribution observed",
    state: "observed",
    timestamp: "2026-06-10 · Strategy Lab",
    detail: "PPE embed session; no thesis saved yet.",
  },
  {
    id: "h2",
    title: "Narrower-range thesis draft",
    state: "saved",
    timestamp: "2026-06-11 · Thesis confirmation",
    detail: "Preview persistence in browser only.",
  },
  {
    id: "h3",
    title: "Range expression simulation",
    state: "simulated",
    timestamp: "2026-06-11 · Expression planning",
    detail: "Sim-only save — order not transmitted.",
  },
  {
    id: "h4",
    title: "Downside tail hedge review",
    state: "reviewed",
    timestamp: "2026-06-09 · Command Center",
    detail: "Steward review marked complete (fixture).",
  },
];

export const stateLabels: Record<HistoryState, string> = {
  observed: "Observed",
  saved: "Saved",
  simulated: "Simulated",
  executed: "Executed",
  reviewed: "Reviewed",
};
