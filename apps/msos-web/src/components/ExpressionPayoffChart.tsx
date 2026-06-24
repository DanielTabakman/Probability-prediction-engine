"use client";

/**
 * Expression payoff vs market — pre-computed arrays from Python only.
 */

import { ChartCurveLegend } from "@/components/ChartCurveLegend";
import {
  LABELED_CHART_LAYOUT,
  buildPayoffAxisTicks,
  buildPriceAxisTicks,
  chartInnerBox,
  formatAxisPayoff,
  formatAxisPrice,
  priceToChartX,
  seriesPathInLayout,
  seriesPathWithYRange,
  valueToChartY,
  CHART_AXIS_STYLE,
} from "@/lib/chartAxisDisplay";
import { DEFAULT_CURVE_LABELS, type CurveDisplayLabels } from "@/lib/chartCurveLabels";
import { useDisplayCurrency } from "@/lib/useDisplayCurrency";

type ExpressionPayoffChartProps = {
  pricesUsd: number[];
  marketPdfPct: number[];
  beliefPdfPct?: number[];
  payoffPct: number[];
  payoffUsd?: number[];
  spotUsd: number;
  expiryLabel: string;
  curveLabels?: CurveDisplayLabels;
  loading?: boolean;
  error?: string | null;
  className?: string;
};

const LAYOUT = LABELED_CHART_LAYOUT;
const GRID_STROKE = "rgba(255, 255, 255, 0.06)";
const AXIS_STROKE = "rgba(255, 255, 255, 0.14)";
const LABEL_FILL = "#8ea4bd";

export function ExpressionPayoffChart({
  pricesUsd,
  marketPdfPct,
  beliefPdfPct,
  payoffPct,
  payoffUsd,
  spotUsd,
  expiryLabel,
  curveLabels = DEFAULT_CURVE_LABELS,
  loading = false,
  error = null,
  className = "",
}: ExpressionPayoffChartProps) {
  const { currency, formatMoney } = useDisplayCurrency();
  if (loading) {
    return (
      <div className="expression-chart panel-sub" aria-live="polite">
        Loading trade vs market…
      </div>
    );
  }
  if (error) {
    return (
      <div className="expression-chart expression-chart-error" role="status">
        <div className="panel-sub">Trade vs market</div>
        <p>{error}</p>
        <p className="micro">
          Open Strategy Lab, pick an expiry, confirm your view, then return here. Hard-refresh if you
          just deployed.
        </p>
      </div>
    );
  }
  if (!pricesUsd.length || pricesUsd.length !== marketPdfPct.length) {
    return null;
  }

  const xMin = pricesUsd[0];
  const xMax = pricesUsd[pricesUsd.length - 1];
  const box = chartInnerBox(LAYOUT);
  const pdfPeak = Math.max(...marketPdfPct, ...(beliefPdfPct ?? []), 1);
  const usePayoffUsd =
    Array.isArray(payoffUsd) &&
    payoffUsd.length === pricesUsd.length &&
    payoffUsd.some((v) => Number.isFinite(v));
  const payoffMin = usePayoffUsd ? Math.min(...payoffUsd) : 0;
  const payoffMax = usePayoffUsd ? Math.max(...payoffUsd) : Math.max(...payoffPct, 1);

  const marketPath = seriesPathInLayout(pricesUsd, marketPdfPct, LAYOUT, pdfPeak);
  const beliefPath =
    beliefPdfPct && beliefPdfPct.length === pricesUsd.length
      ? seriesPathInLayout(pricesUsd, beliefPdfPct, LAYOUT, pdfPeak)
      : "";
  const payoffPath = usePayoffUsd
    ? seriesPathWithYRange(pricesUsd, payoffUsd, LAYOUT, payoffMin, payoffMax)
    : payoffPct.length === pricesUsd.length
      ? seriesPathInLayout(pricesUsd, payoffPct, LAYOUT, payoffMax)
      : "";

  const priceTicks = buildPriceAxisTicks(xMin, xMax, 5);
  const pdfTicks = [0, pdfPeak * 0.5, pdfPeak];
  const payoffTicks = usePayoffUsd
    ? buildPayoffAxisTicks(payoffMin, payoffMax, 4)
    : [0, payoffMax * 0.5, payoffMax];

  const spotX = priceToChartX(spotUsd, xMin, xMax, LAYOUT);

  return (
    <div className={`expression-chart ${className}`.trim()}>
      <div className="expression-chart-head">
        <div className="panel-sub">
          Suggested trade vs market at {expiryLabel}
          <span className="micro currency-badge"> · {currency}</span>
        </div>
        <ChartCurveLegend
          labels={curveLabels}
          showBelief={Boolean(beliefPath)}
          showPayoff={Boolean(payoffPath)}
          className="expression-chart-legend chart-curve-legend"
        />
      </div>
      <div
        className="graph graph-labeled"
        role="img"
        aria-label={`Payoff and distributions for ${expiryLabel}`}
      >
        <svg viewBox={`0 0 ${LAYOUT.width} ${LAYOUT.height}`} preserveAspectRatio="xMidYMid meet">
          {priceTicks.map((price) => {
            const x = priceToChartX(price, xMin, xMax, LAYOUT);
            return (
              <g key={`x-grid-${price}`}>
                <line x1={x} y1={box.y0} x2={x} y2={box.y1} stroke={GRID_STROKE} />
                <text
                  x={x}
                  y={box.y1 + 16}
                  fill={LABEL_FILL}
                  fontSize="10"
                  textAnchor="middle"
                >
                  {formatAxisPrice(price)}
                </text>
              </g>
            );
          })}

          {pdfTicks.map((tick, index) => {
            const y = valueToChartY(tick, pdfPeak, LAYOUT);
            const label = index === 0 ? "0" : index === pdfTicks.length - 1 ? "peak" : "½ peak";
            return (
              <g key={`pdf-y-${tick}`}>
                <line x1={box.x0} y1={y} x2={box.x1} y2={y} stroke={GRID_STROKE} />
                <text
                  x={box.x0 - 6}
                  y={y + 3}
                  fill={LABEL_FILL}
                  fontSize="9"
                  textAnchor="end"
                >
                  {label}
                </text>
              </g>
            );
          })}

          {payoffTicks.map((tick) => {
            if (!usePayoffUsd) return null;
            const span = payoffMax - payoffMin || 1;
            const y = box.y1 - ((tick - payoffMin) / span) * box.innerH;
            return (
              <g key={`payoff-y-${tick}`}>
                <text
                  x={box.x1 + 6}
                  y={y + 3}
                  fill="#4ade80"
                  fontSize="9"
                  textAnchor="start"
                >
                  {formatAxisPayoff(tick)}
                </text>
              </g>
            );
          })}

          <line x1={box.x0} y1={box.y1} x2={box.x1} y2={box.y1} stroke={AXIS_STROKE} />
          <line x1={box.x0} y1={box.y0} x2={box.x0} y2={box.y1} stroke={AXIS_STROKE} />
          <line x1={box.x1} y1={box.y0} x2={box.x1} y2={box.y1} stroke={AXIS_STROKE} />

          <text x={(box.x0 + box.x1) / 2} y={LAYOUT.height - 6} fill={LABEL_FILL} fontSize="10" textAnchor="middle">
            BTC price at expiry
          </text>
          <text
            x={12}
            y={(box.y0 + box.y1) / 2}
            fill={LABEL_FILL}
            fontSize="9"
            textAnchor="middle"
            transform={`rotate(-90 12 ${(box.y0 + box.y1) / 2})`}
          >
            Distribution ({curveLabels.market_method ?? "Black–Scholes lognormal"})
          </text>
          {usePayoffUsd ? (
            <text
              x={LAYOUT.width - 12}
              y={(box.y0 + box.y1) / 2}
              fill="#4ade80"
              fontSize="9"
              textAnchor="middle"
              transform={`rotate(90 ${LAYOUT.width - 12} ${(box.y0 + box.y1) / 2})`}
            >
              P&amp;L at expiry
            </text>
          ) : null}

          <path
            d={`${marketPath} L ${box.x1},${box.y1} L ${box.x0},${box.y1} Z`}
            stroke="#9e8bff"
            strokeWidth="2.5"
            fill="rgba(158, 139, 255, 0.12)"
          />
          {beliefPath ? (
            <path
              d={beliefPath}
              stroke="#2dd4bf"
              strokeWidth="2"
              strokeDasharray="6 4"
              fill="none"
            />
          ) : null}
          {payoffPath ? (
            <path
              d={payoffPath}
              stroke="#4ade80"
              strokeWidth="2.5"
              strokeDasharray="4 3"
              fill="none"
            />
          ) : null}
          <line
            x1={spotX}
            y1={box.y0}
            x2={spotX}
            y2={box.y1}
            stroke="#233c55"
            strokeDasharray="5 8"
          />
          <text x={spotX + 4} y={box.y0 + 12} fill={LABEL_FILL} fontSize="10">
            spot {formatMoney(spotUsd)}
          </text>
        </svg>
      </div>
    </div>
  );
}
