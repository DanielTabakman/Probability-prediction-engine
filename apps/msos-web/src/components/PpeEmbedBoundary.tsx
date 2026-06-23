"use client";

/**
 * PPE embed boundary — display/proxy only; no distribution math in TypeScript.
 */

import type { BeliefPresetId } from "@/lib/beliefPresets";
import {
  PPE_EMBED_ONLY_PARAM,
  type DisplayPayload,
  type DisplaySeries,
  formatUsd,
  findSeriesByExpiry,
  isDisplaySeries,
  PPE_EMBED_URL,
} from "@/lib/ppeDisplayPayload";

export const PPE_EMBED_ANCHOR_ID = "distribution-summary";

function buildChromelessEmbedSrc(baseUrl: string): string {
  const withoutHash = baseUrl.replace(/#.*$/, "");
  const [path, query = ""] = withoutHash.split("?");
  const params = new URLSearchParams(query);
  params.set(PPE_EMBED_ONLY_PARAM, "1");
  const qs = params.toString();
  return qs ? `${path}?${qs}` : `${path}?${PPE_EMBED_ONLY_PARAM}=1`;
}

/** Map pre-computed price/pdf arrays to SVG path (linear scale only — no new math). */
function seriesToSvgPath(
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

function filledAreaPath(linePath: string): string {
  if (!linePath) return "";
  return `${linePath} L 680,250 L 20,250 Z`;
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
  const marketPath = seriesToSvgPath(series.prices_usd, series.pdf_pct, 700, 280, 20);
  const beliefPath =
    beliefPdfPct && beliefPdfPct.length === series.prices_usd.length
      ? seriesToSvgPath(series.prices_usd, beliefPdfPct, 700, 280, 20)
      : "";
  const spotX =
    series.prices_usd.length > 1
      ? 20 +
        ((spotUsd - series.prices_usd[0]) /
          (series.prices_usd[series.prices_usd.length - 1] - series.prices_usd[0] || 1)) *
          660
      : 350;

  const ariaLabel = beliefLabel
    ? `Distribution curves for ${series.expiry_date} — market vs your ${beliefLabel} view`
    : `Distribution curve for ${series.expiry_date}`;

  return (
    <>
      <div className="graph" role="img" aria-label={ariaLabel}>
        <svg viewBox="0 0 700 280" preserveAspectRatio="none">
          <path
            d={filledAreaPath(marketPath)}
            stroke="#9e8bff"
            strokeWidth="4"
            fill="rgba(158, 139, 255, 0.14)"
          />
          {beliefPath ? (
            <path
              d={filledAreaPath(beliefPath)}
              stroke="#2dd4bf"
              strokeWidth="3"
              strokeDasharray="6 4"
              fill="rgba(45, 212, 191, 0.16)"
            />
          ) : null}
          <line x1={spotX} y1="38" x2={spotX} y2="250" stroke="#233c55" strokeDasharray="5 8" />
          <text x={spotX + 4} y="54" fill="#8ea4bd" fontSize="12">
            spot
          </text>
        </svg>
      </div>
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
  selectedExpiry?: string | null;
  beliefPresetId?: BeliefPresetId | null;
  beliefLabel?: string | null;
};

export function PpeEmbedBoundary({
  payload,
  selectedExpiry = null,
  beliefPresetId = null,
  beliefLabel = null,
}: PpeEmbedBoundaryProps) {
  if (payload) {
    const primary =
      (selectedExpiry && findSeriesByExpiry(payload, selectedExpiry)) ||
      payload.series_by_expiry.find(isDisplaySeries);
    if (!primary) {
      return null;
    }
    const beliefOverlay =
      beliefPresetId && primary.belief_presets
        ? primary.belief_presets[beliefPresetId]?.pdf_pct
        : beliefPresetId && payload.belief_presets
          ? payload.belief_presets[beliefPresetId]?.pdf_pct
          : null;

    return (
      <div className="ppe-chart-region" role="region" aria-label="BTC options distribution">
        <p className="ppe-embed-live-note">
          <span className="tag teal">Live</span> From Deribit options — updated with market quotes.
          {beliefOverlay ? (
            <>
              {" "}
              <span className="tag teal">Your view</span> Teal dashed curve = your belief preset.
            </>
          ) : null}
        </p>
        <NativeDistributionChart
          series={primary}
          spotUsd={payload.spot_usd}
          beliefPdfPct={beliefOverlay}
          beliefLabel={beliefLabel}
        />
      </div>
    );
  }

  if (!PPE_EMBED_URL) {
    return (
      <div className="ppe-embed ppe-embed-degraded" role="region" aria-label="Options chart">
        <div className="ppe-embed-placeholder">
          <span className="tag amber">Loading</span>
          <h3>Chart unavailable</h3>
          <p>Live options data could not be loaded. Try refreshing the page.</p>
        </div>
      </div>
    );
  }

  const embedSrc = buildChromelessEmbedSrc(PPE_EMBED_URL);

  return (
    <div className="ppe-embed ppe-embed-chromeless" role="region" aria-label="Options chart">
      <p className="ppe-embed-live-note">
        <span className="tag teal">Live</span> Interactive chart from live options data.
      </p>
      <iframe
        title="BTC options distribution"
        src={embedSrc}
        className="ppe-embed-frame ppe-embed-frame-chromeless"
        loading="lazy"
        referrerPolicy="strict-origin-when-cross-origin"
      />
    </div>
  );
}
