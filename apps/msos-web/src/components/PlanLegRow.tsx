import type { PlanLeg } from "@/data/expressionPlanningFixtures";
import { planLegTooltip } from "@/lib/planLegTooltips";

type PlanLegRowProps = {
  leg: PlanLeg;
  assetTicker?: string;
};

export function PlanLegRow({ leg, assetTicker }: PlanLegRowProps) {
  const tip = planLegTooltip(leg, assetTicker);
  return (
    <div
      className="leg leg-with-tip"
      title={tip}
      aria-label={tip}
    >
      <span className={leg.side === "BUY" ? "buy" : "sell"}>{leg.side}</span>
      <span>{leg.instrument}</span>
      <span>{leg.strike}</span>
      <span>{leg.tenor}</span>
      <span className="leg-tip-hint micro" aria-hidden="true">
        ?
      </span>
    </div>
  );
}
