"use client";

/**
 * PPE embed boundary — display/proxy only; no distribution math in TypeScript.
 */

import { resolveCurveLabels } from "@/lib/chartCurveLabels";
import type { BeliefPresetId } from "@/lib/beliefPresets";
import type { LabDataMode } from "@/lib/strategyLabCopy";
import { LabeledDistributionChart } from "@/components/LabeledDistributionChart";
import {
  type DisplayPayload,
  type DisplaySeries,
  formatUsd,
  findSeriesByExpiry,
  isDisplaySeries,
} from "@/lib/ppeDisplayPayload";

export const PPE_EMBED_ANCHOR_ID = "distribution-summary";

/** Map pre-computed price/pdf arrays to SVG path (linear scale only — no new math). */
export function seriesToSvgPath(
  prices: number[],
  pdf: number[],
  width: number,
  height: number,
  pad: number,
): string {
  if (!prices.length || prices.length !== pdf.length) {
    return "";
  }
  const xMin = prices[0];
  const xMax = prices[prices.length - 1];
  const xSpan = xMax - xMin || 1;
  const yMax = Math.max(...pdf, 1);
  const innerW = width - pad * 2;
  const innerH = height - pad * 2;
  const points = prices.map((price, index) => {
    const x = pad + ((price - xMin) / xSpan) * innerW;
    const y = pad + innerH - (pdf[index] / yMax) * innerH;
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  return `M ${points.join(" L ")}`;
}

type NativeDistributionChartProps = {
  series: DisplaySeries;
  spotUsd: number;
  beliefPdfPct?: number[] | null;
  beliefLabel?: string | null;
};

function NativeDistributionChart({
  series,
  spotUsd,
  beliefPdfPct,
  beliefLabel,
}: NativeDistributionChartProps) {
  const ariaLabel = beliefLabel
    ? `Distribution curves for ${series.expiry_date} — market vs your ${beliefLabel} view`
    : `Distribution curve for ${series.expiry_date}`;
  const curveLabels = resolveCurveLabels(series.curve_labels);

  return (
    <>
      <LabeledDistributionChart
        pricesUsd={series.prices_usd}
        marketPdfPct={series.pdf_pct}
        beliefPdfPct={beliefPdfPct}
        spotUsd={spotUsd}
        ariaLabel={ariaLabel}
        curveLabels={curveLabels}
      />
      {series.mean_usd !== undefined && series.quartiles_usd ? (
        <div className="ppe-summary-table" aria-label="PPE display payload summary">
          <span>Mean {formatUsd(series.mean_usd)}</span>
          <span>Q1 {formatUsd(series.quartiles_usd.q1_usd)}</span>
          <span>Median {formatUsd(series.quartiles_usd.median_usd)}</span>
          <span>Q3 {formatUsd(series.quartiles_usd.q3_usd)}</span>
        </div>
      ) : null}
    </>
  );
}

type PpeEmbedBoundaryProps = {
  payload: DisplayPayload | null;
  live?: boolean;
  dataMode?: LabDataMode;
  selectedExpiry?: string | null;
  beliefPresetId?: BeliefPresetId | null;
  beliefLabel?: string | null;
  beliefPdfPct?: number[] | null;
};

export function PpeEmbedBoundary({
  payload,
  live = false,
  dataMode = "demo",
  selectedExpiry = null,
  beliefPresetId = null,
  beliefLabel = null,
  beliefPdfPct = null,
}: PpeEmbedBoundaryProps) {
  if (dataMode === "loading") {
    return (
      <div className="ppe-embed ppe-embed-degraded" role="region" aria-label="Options chart">
        <div className="ppe-embed-placeholder">
          <span className="tag teal">Loading</span>
          <h3>Loading live chart</h3>
          <p>Fetching BTC options distribution from Deribit…</p>
        </div>
      </div>
    );
  }

  if (!live || !payload) {
    return (
      <div className="ppe-embed ppe-embed-degraded" role="region" aria-label="Options chart">
        <div className="ppe-embed-placeholder">
          <span className="tag amber">Sample</span>
          <h3>Placeholder chart</h3>
          <p>
            This view uses sample fixtures — not live Deribit quotes. Refresh when you are online;
            live data loads automatically when the display API is reachable.
          </p>
        </div>
      </div>
    );
  }

  if (payload) {
    const primary =
      (selectedExpiry && findSeriesByExpiry(payload, selectedExpiry)) ||
      payload.series_by_expiry.find(isDisplaySeries);
    if (!primary) {
      return null;
    }
    const beliefOverlay =
      beliefPdfPct ??
      (beliefPresetId && primary.belief_presets
        ? primary.belief_presets[beliefPresetId]?.pdf_pct
        : beliefPresetId && payload.belief_presets
          ? payload.belief_presets[beliefPresetId]?.pdf_pct
          : null);

    return (
      <div className="ppe-chart-region" role="region" aria-label="BTC options distribution">
        <p className="ppe-embed-live-note">
          <span className="tag teal">Live</span> From Deribit options — updated with market quotes.
          Purple curve = {resolveCurveLabels(primary.curve_labels ?? payload.curve_labels).market_legend}.
          {beliefOverlay ? (
            <>
              {" "}
              Teal dashed = {resolveCurveLabels(primary.curve_labels ?? payload.curve_labels).belief_legend}.
            </>
          ) : null}
        </p>
        <NativeDistributionChart
          series={{ ...primary, curve_labels: primary.curve_labels ?? payload.curve_labels }}
          spotUsd={payload.spot_usd}
          beliefPdfPct={beliefOverlay}
          beliefLabel={beliefLabel}
        />
      </div>
    );
  }

  return null;
}
