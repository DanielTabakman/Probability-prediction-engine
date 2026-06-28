import {
  LAB_ASSET_QUERY_PARAM,
  type LabAssetId,
} from "@/lib/ppeDisplayPayload";

export type StrategyLabWorkflowStep = "compare" | "confirm" | "plan";

const STEP_PATHS: Record<StrategyLabWorkflowStep, string> = {
  compare: "/strategy-lab",
  confirm: "/strategy-lab/confirm",
  plan: "/strategy-lab/expression",
};

export const STRATEGY_LAB_WORKFLOW_STEPS: { id: StrategyLabWorkflowStep; label: string }[] = [
  { id: "compare", label: "Compare view" },
  { id: "confirm", label: "Confirm view" },
  { id: "plan", label: "Plan paper trade" },
];

export function buildWorkflowStepHref(
  step: StrategyLabWorkflowStep,
  assetId?: LabAssetId,
): string {
  const path = STEP_PATHS[step];
  const normalized = (assetId ?? "").trim().toUpperCase();
  if (!normalized) {
    return path;
  }
  return `${path}?${LAB_ASSET_QUERY_PARAM}=${encodeURIComponent(normalized)}`;
}

export function workflowStepIndex(step: StrategyLabWorkflowStep): number {
  return STRATEGY_LAB_WORKFLOW_STEPS.findIndex((item) => item.id === step);
}
