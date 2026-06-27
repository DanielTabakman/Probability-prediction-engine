"use client";

/**
 * Labeled distribution chart — pre-computed price/pdf arrays only (no math in TS).
 */

import { ChartCurveLegend } from "@/components/ChartCurveLegend";
import {
  CHART_AXIS_STYLE,
  LABELED_DISTRIBUTION_LAYOUT,
  type ChartLayout,
  buildPriceAxisTicks,
  chartInnerBox,
  formatAxisPrice,
  priceToChartX,
  seriesPathInLayout,
  valueToChartY,
} from "@/lib/chartAxisDisplay";
import { DEFAULT_CURVE_LABELS, type CurveDisplayLabels } from "@/lib/chartCurveLabels";
import { useDisplayCurrency } from "@/lib/useDisplayCurrency";

type LabeledDistributionChartProps = {
  pricesUsd: number[];
  marketPdfPct: number[];
  beliefPdfPct?: number[] | null;
  spotUsd: number;
  ariaLabel: string;
  curveLabels?: CurveDisplayLabels;
  priceAxisLabel?: string;
  layout?: ChartLayout;
};

function filledAreaInLayout(linePath: string, layout: ChartLayout): string {
  if (!linePath) return "";
  const box = chartInnerBox(layout);
  return `${linePath} L ${box.x1},${box.y1} L ${box.x0},${box.y1} Z`;
}

export function LabeledDistributionChart({
  pricesUsd,
  marketPdfPct,
  beliefPdfPct,
  spotUsd,
  ariaLabel,
  curveLabels = DEFAULT_CURVE_LABELS,
  priceAxisLabel = "BTC price at expiry",
  layout = LABELED_DISTRIBUTION_LAYOUT,
}: LabeledDistributionChartProps) {
  const { currency, formatMoney } = useDisplayCurrency();
  if (!pricesUsd.length || pricesUsd.length !== marketPdfPct.length) {
    return null;
  }

  const xMin = pricesUsd[0];
  const xMax = pricesUsd[pricesUsd.length - 1];
  const box = chartInnerBox(layout);
  const pdfPeak = Math.max(...marketPdfPct, ...(beliefPdfPct ?? []), 1);
  const marketPath = seriesPathInLayout(pricesUsd, marketPdfPct, layout, pdfPeak);
  const beliefPath =
    beliefPdfPct && beliefPdfPct.length === pricesUsd.length
      ? seriesPathInLayout(pricesUsd, beliefPdfPct, layout, pdfPeak)
      : "";
  const priceTicks = buildPriceAxisTicks(xMin, xMax, 5);
  const pdfTicks = [0, pdfPeak * 0.5, pdfPeak];
  const spotX = priceToChartX(spotUsd, xMin, xMax, layout);
  const { gridStroke, axisStroke, labelFill } = CHART_AXIS_STYLE;

  return (
    <div className="labeled-distribution-chart">
      <ChartCurveLegend labels={curveLabels} showBelief={Boolean(beliefPath)} />
      <div className="graph graph-labeled" role="img" aria-label={ariaLabel}>
      <svg viewBox={`0 0 ${layout.width} ${layout.height}`} preserveAspectRatio="xMidYMid meet">
        {priceTicks.map((price) => {
          const x = priceToChartX(price, xMin, xMax, layout);
          return (
            <g key={`x-grid-${price}`}>
              <line x1={x} y1={box.y0} x2={x} y2={box.y1} stroke={gridStroke} />
              <text x={x} y={box.y1 + 16} fill={labelFill} fontSize="10" textAnchor="middle">
                {formatAxisPrice(price, currency)}
              </text>
            </g>
          );
        })}

        {pdfTicks.map((tick, index) => {
          const y = valueToChartY(tick, pdfPeak, layout);
          const label = index === 0 ? "0" : index === pdfTicks.length - 1 ? "peak" : "½ peak";
          return (
            <g key={`pdf-y-${tick}`}>
              <line x1={box.x0} y1={y} x2={box.x1} y2={y} stroke={gridStroke} />
              <text x={box.x0 - 6} y={y + 3} fill={labelFill} fontSize="9" textAnchor="end">
                {label}
              </text>
            </g>
          );
        })}

        <line x1={box.x0} y1={box.y1} x2={box.x1} y2={box.y1} stroke={axisStroke} />
        <line x1={box.x0} y1={box.y0} x2={box.x0} y2={box.y1} stroke={axisStroke} />

        <text
          x={(box.x0 + box.x1) / 2}
          y={layout.height - 6}
          fill={labelFill}
          fontSize="10"
          textAnchor="middle"
        >
          {priceAxisLabel}
        </text>
        <text
          x={12}
          y={(box.y0 + box.y1) / 2}
          fill={labelFill}
          fontSize="9"
          textAnchor="middle"
          transform={`rotate(-90 12 ${(box.y0 + box.y1) / 2})`}
        >
          Distribution ({curveLabels.market_method ?? "Black–Scholes lognormal"})
        </text>

        <path
          d={filledAreaInLayout(marketPath, layout)}
          stroke="#9e8bff"
          strokeWidth="3"
          fill="rgba(158, 139, 255, 0.14)"
        />
        {beliefPath ? (
          <path
            d={filledAreaInLayout(beliefPath, layout)}
            stroke="#2dd4bf"
            strokeWidth="2.5"
            strokeDasharray="6 4"
            fill="rgba(45, 212, 191, 0.16)"
          />
        ) : null}
        <line x1={spotX} y1={box.y0} x2={spotX} y2={box.y1} stroke="#233c55" strokeDasharray="5 8" />
        <text x={spotX + 4} y={box.y0 + 12} fill={labelFill} fontSize="10">
          spot {formatMoney(spotUsd)}
        </text>
      </svg>
      </div>
    </div>
  );
}
