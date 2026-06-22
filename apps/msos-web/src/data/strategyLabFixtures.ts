/** Preview/fixture data for Strategy Lab (display only — no distribution math). */

export type LabMetric = {
  label: string;
  value: string;
  tone?: "teal" | "amber";
};

export const strategyLabMetrics: LabMetric[] = [
  { label: "Market", value: "BTC options" },
  { label: "Expiry", value: "30 days" },
  { label: "Spot", value: "$104,320" },
  { label: "Market range", value: "6.8%", tone: "amber" },
  { label: "Your range", value: "5.4%", tone: "teal" },
  { label: "Data", value: "Demo", tone: "teal" },
];

export {
  strategyLabDefaultOutcome as outcomeSummary,
  strategyLabLensTiles as lensTiles,
} from "@/content/strategyLab";
