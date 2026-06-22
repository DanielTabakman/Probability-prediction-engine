/** History surface fallback copy. */

export type HistoryState = "observed" | "saved" | "simulated" | "executed" | "reviewed";

export type HistoryEntry = {
  id: string;
  title: string;
  state: HistoryState;
  timestamp: string;
  detail: string;
};

export const historyIntro =
  "Your trail from first look → saved view → paper trade → post-mortem. Live fills will appear here when connected.";

export const historyEntries: HistoryEntry[] = [
  {
    id: "h1",
    title: "BTC range — first look",
    state: "observed",
    timestamp: "Jun 10 · Strategy Lab",
    detail: "Browsed the options curve; nothing saved yet.",
  },
  {
    id: "h2",
    title: "Calmer-than-market view",
    state: "saved",
    timestamp: "Jun 11 · Thesis confirmation",
    detail: "View saved to your workspace.",
  },
  {
    id: "h3",
    title: "Range trade — paper",
    state: "simulated",
    timestamp: "Jun 11 · Expression planning",
    detail: "Paper plan only — no order sent.",
  },
  {
    id: "h4",
    title: "Tail hedge post-mortem",
    state: "reviewed",
    timestamp: "Jun 9 · Command Center",
    detail: "Review marked complete.",
  },
];

export const stateLabels: Record<HistoryState, string> = {
  observed: "Looked",
  saved: "Saved",
  simulated: "Paper",
  executed: "Live",
  reviewed: "Reviewed",
};
