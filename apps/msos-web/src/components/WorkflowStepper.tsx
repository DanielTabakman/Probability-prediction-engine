import Link from "next/link";

import {
  STRATEGY_LAB_WORKFLOW_STEPS,
  buildWorkflowStepHref,
  workflowStepIndex,
  type StrategyLabWorkflowStep,
} from "@/lib/strategyLabWorkflow";
import type { LabAssetId } from "@/lib/ppeDisplayPayload";

type WorkflowStepperProps = {
  currentStep: StrategyLabWorkflowStep;
  assetId?: LabAssetId;
};

export function WorkflowStepper({ currentStep, assetId }: WorkflowStepperProps) {
  const currentIndex = workflowStepIndex(currentStep);

  return (
    <nav className="workflow-stepper" aria-label="Strategy Lab workflow" data-tour="lab-workflow-review">
      {STRATEGY_LAB_WORKFLOW_STEPS.map((step, index) => {
        const active = step.id === currentStep;
        const complete = index < currentIndex;
        const className = [
          "workflow-step",
          active ? "active" : undefined,
          complete ? "done" : undefined,
        ]
          .filter(Boolean)
          .join(" ");

        return (
          <Link
            key={step.id}
            href={buildWorkflowStepHref(step.id, assetId)}
            className={className}
            aria-current={active ? "step" : undefined}
          >
            <span className="workflow-step-num" aria-hidden="true">
              {index + 1}
            </span>
            {step.label}
          </Link>
        );
      })}
    </nav>
  );
}
