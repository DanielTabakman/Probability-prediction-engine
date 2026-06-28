import {
  DEFAULT_LAB_ASSET_ID,
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
  assetId: LabAssetId = DEFAULT_LAB_ASSET_ID,
): string {
  const path = STEP_PATHS[step];
  if (assetId === DEFAULT_LAB_ASSET_ID) {
    return path;
  }
  return `${path}?${LAB_ASSET_QUERY_PARAM}=${encodeURIComponent(assetId)}`;
}

export function workflowStepIndex(step: StrategyLabWorkflowStep): number {
  return STRATEGY_LAB_WORKFLOW_STEPS.findIndex((item) => item.id === step);
}
