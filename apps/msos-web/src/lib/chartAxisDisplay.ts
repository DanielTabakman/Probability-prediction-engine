/**
 * Chart axis display helpers — linear scale only (no distribution math).
 */

import { formatUsd } from "@/lib/ppeDisplayPayload";

export type ChartLayout = {
  width: number;
  height: number;
  padLeft: number;
  padRight: number;
  padTop: number;
  padBottom: number;
};

export const DEFAULT_CHART_LAYOUT: ChartLayout = {
  width: 700,
  height: 280,
  padLeft: 20,
  padRight: 20,
  padTop: 20,
  padBottom: 20,
};

/** Room for axis tick labels on expression / payoff charts. */
export const LABELED_CHART_LAYOUT: ChartLayout = {
  width: 700,
  height: 318,
  padLeft: 58,
  padRight: 58,
  padTop: 18,
  padBottom: 42,
};

export type ChartInnerBox = {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
  innerW: number;
  innerH: number;
};

export function chartInnerBox(layout: ChartLayout): ChartInnerBox {
  const x0 = layout.padLeft;
  const y0 = layout.padTop;
  const x1 = layout.width - layout.padRight;
  const y1 = layout.height - layout.padBottom;
  return {
    x0,
    y0,
    x1,
    y1,
    innerW: x1 - x0,
    innerH: y1 - y0,
  };
}

export function priceToChartX(
  price: number,
  xMin: number,
  xMax: number,
  layout: ChartLayout,
): number {
  const box = chartInnerBox(layout);
  return box.x0 + ((price - xMin) / (xMax - xMin || 1)) * box.innerW;
}

export function valueToChartY(
  value: number,
  yMax: number,
  layout: ChartLayout,
): number {
  const box = chartInnerBox(layout);
  return box.y1 - (value / (yMax || 1)) * box.innerH;
}

export function formatAxisPrice(value: number): string {
  const abs = Math.abs(value);
  if (abs >= 1_000_000) {
    return `$${(value / 1_000_000).toFixed(1)}M`;
  }
  if (abs >= 10_000) {
    return `$${Math.round(value / 1000)}k`;
  }
  if (abs >= 1000) {
    return `$${(value / 1000).toFixed(1)}k`;
  }
  return formatUsd(value);
}

export function formatAxisPayoff(value: number): string {
  const abs = Math.abs(value);
  if (abs >= 10_000) {
    return `$${Math.round(value / 1000)}k`;
  }
  if (abs >= 1000) {
    return `$${(value / 1000).toFixed(1)}k`;
  }
  return formatUsd(value);
}

function niceStep(span: number, targetTicks: number): number {
  if (span <= 0) return 1;
  const rough = span / Math.max(targetTicks - 1, 1);
  const magnitude = 10 ** Math.floor(Math.log10(rough));
  const normalized = rough / magnitude;
  let nice = 1;
  if (normalized > 5) nice = 10;
  else if (normalized > 2) nice = 5;
  else if (normalized > 1) nice = 2;
  return nice * magnitude;
}

export function buildPriceAxisTicks(xMin: number, xMax: number, count = 5): number[] {
  const span = xMax - xMin;
  if (span <= 0) return [xMin];
  const step = niceStep(span, count);
  const start = Math.ceil(xMin / step) * step;
  const ticks: number[] = [];
  for (let value = start; value <= xMax + step * 0.01; value += step) {
    ticks.push(value);
    if (ticks.length >= count + 1) break;
  }
  if (!ticks.length) ticks.push(xMin, xMax);
  return ticks;
}

export function buildPayoffAxisTicks(min: number, max: number, count = 5): number[] {
  if (min === max) {
    return [min];
  }
  const span = max - min;
  const step = niceStep(span, count);
  const start = Math.floor(min / step) * step;
  const ticks: number[] = [];
  for (let value = start; value <= max + step * 0.01; value += step) {
    if (value >= min - step * 0.01 || ticks.length === 0) {
      ticks.push(value);
    }
    if (ticks.length >= count + 2) break;
  }
  if (!ticks.length) return [min, max];
  return ticks;
}

export function seriesPathInLayout(
  prices: number[],
  values: number[],
  layout: ChartLayout,
  yMax?: number,
): string {
  if (!prices.length || prices.length !== values.length) return "";
  const xMin = prices[0];
  const xMax = prices[prices.length - 1];
  const peak = yMax ?? Math.max(...values, 1);
  const points = prices.map((price, index) => {
    const x = priceToChartX(price, xMin, xMax, layout);
    const y = valueToChartY(values[index], peak, layout);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  return `M ${points.join(" L ")}`;
}

export function seriesPathWithYRange(
  prices: number[],
  values: number[],
  layout: ChartLayout,
  yMin: number,
  yMax: number,
): string {
  if (!prices.length || prices.length !== values.length) return "";
  const xMin = prices[0];
  const xMax = prices[prices.length - 1];
  const span = yMax - yMin || 1;
  const box = chartInnerBox(layout);
  return `M ${points.join(" L ")}`;
}

/** Distribution-only layout (Strategy Lab) — left Y + bottom X, no P&L axis. */
export const LABELED_DISTRIBUTION_LAYOUT: ChartLayout = {
  width: 700,
  height: 318,
  padLeft: 58,
  padRight: 16,
  padTop: 18,
  padBottom: 42,
};

export const CHART_AXIS_STYLE = {
  gridStroke: "rgba(255, 255, 255, 0.06)",
  axisStroke: "rgba(255, 255, 255, 0.14)",
  labelFill: "#8ea4bd",
} as const;
