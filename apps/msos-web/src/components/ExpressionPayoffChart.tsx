"use client";

/**
 * Expression payoff vs market — pre-computed arrays from Python only.
 */

import { seriesToSvgPath } from "@/components/PpeEmbedBoundary";
import { formatUsd } from "@/lib/ppeDisplayPayload";

type ExpressionPayoffChartProps = {
  pricesUsd: number[];
  marketPdfPct: number[];
  beliefPdfPct?: number[];
  payoffPct: number[];
  spotUsd: number;
  expiryLabel: string;
  loading?: boolean;
  error?: string | null;
};

export function ExpressionPayoffChart({
  pricesUsd,
  marketPdfPct,
  beliefPdfPct,
  payoffPct,
  spotUsd,
  expiryLabel,
  loading = false,
  error = null,
}: ExpressionPayoffChartProps) {
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

  const marketPath = seriesToSvgPath(pricesUsd, marketPdfPct, 700, 280, 20);
  const beliefPath =
    beliefPdfPct && beliefPdfPct.length === pricesUsd.length
      ? seriesToSvgPath(pricesUsd, beliefPdfPct, 700, 280, 20)
      : "";
  const payoffPath =
    payoffPct.length === pricesUsd.length
      ? seriesToSvgPath(pricesUsd, payoffPct, 700, 280, 20)
      : "";
  const xMin = pricesUsd[0];
  const xMax = pricesUsd[pricesUsd.length - 1];
  const spotX =
    pricesUsd.length > 1
      ? 20 + ((spotUsd - xMin) / (xMax - xMin || 1)) * 660
      : 350;

  return (
    <div className="expression-chart">
      <div className="expression-chart-head">
        <div className="panel-sub">Suggested trade vs market at {expiryLabel}</div>
        <div className="expression-chart-legend" aria-hidden="true">
          <span className="legend-market">Market</span>
          {beliefPath ? <span className="legend-belief">Your view</span> : null}
          {payoffPath ? <span className="legend-payoff">Payoff at expiry</span> : null}
        </div>
      </div>
      <div className="graph" role="img" aria-label={`Payoff and distributions for ${expiryLabel}`}>
        <svg viewBox="0 0 700 280" preserveAspectRatio="none">
          <path
            d={`${marketPath} L 680,250 L 20,250 Z`}
            stroke="#9e8bff"
            strokeWidth="3"
            fill="rgba(158, 139, 255, 0.12)"
          />
          {beliefPath ? (
            <path
              d={beliefPath}
              stroke="#2dd4bf"
              strokeWidth="2.5"
              strokeDasharray="6 4"
              fill="none"
            />
          ) : null}
          {payoffPath ? (
            <path
              d={payoffPath}
              stroke="#4ade80"
              strokeWidth="3"
              strokeDasharray="4 3"
              fill="none"
            />
          ) : null}
          <line x1={spotX} y1="38" x2={spotX} y2="250" stroke="#233c55" strokeDasharray="5 8" />
          <text x={spotX + 4} y="54" fill="#8ea4bd" fontSize="12">
            spot {formatUsd(spotUsd)}
          </text>
        </svg>
      </div>
    </div>
  );
}
