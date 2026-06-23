"use client";

import type { CurveDisplayLabels } from "@/lib/chartCurveLabels";

type ChartCurveLegendProps = {
  labels: CurveDisplayLabels;
  showBelief?: boolean;
  showPayoff?: boolean;
  className?: string;
};

export function ChartCurveLegend({
  labels,
  showBelief = false,
  showPayoff = false,
  className = "chart-curve-legend",
}: ChartCurveLegendProps) {
  return (
    <div className={className} aria-label="Chart curve legend">
      <span className="legend-market">{labels.market_legend}</span>
      {showBelief ? <span className="legend-belief">{labels.belief_legend}</span> : null}
      {showPayoff ? <span className="legend-payoff">{labels.payoff_legend}</span> : null}
    </div>
  );
}
