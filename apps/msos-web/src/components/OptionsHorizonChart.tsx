"use client";

import { useCallback, useMemo, useRef, useState } from "react";

import {
  CHART_AXIS_STYLE,
  LABELED_CHART_LAYOUT,
  buildPriceAxisTicks,
  chartInnerBox,
  formatAxisPrice,
} from "@/lib/chartAxisDisplay";
import type { HorizonChartPayload } from "@/lib/horizonChartPayload";
import type { HorizonRegionIntent } from "@/lib/horizonRegion";

const LAYOUT = { ...LABELED_CHART_LAYOUT, height: 360 };

type OptionsHorizonChartProps = {
  payload: HorizonChartPayload;
  region: HorizonRegionIntent | null;
  onRegionChange: (region: HorizonRegionIntent["region"] | null) => void;
};

type TimeScale = {
  tMin: number;
  tMax: number;
};

function parseMs(iso: string): number {
  return new Date(iso).getTime();
}

function buildTimeScale(payload: HorizonChartPayload): TimeScale {
  const stamps: number[] = [];
  for (const row of payload.historical.series) {
    stamps.push(parseMs(row.timestamp_utc));
  }
  for (const row of payload.forward.curve) {
    stamps.push(parseMs(row.expiry_utc));
  }
  if (payload.implied?.expiry_date) {
    stamps.push(parseMs(`${payload.implied.expiry_date}T00:00:00Z`));
  }
  const now = Date.now();
  stamps.push(now);
  const tMin = Math.min(...stamps);
  const tMax = Math.max(...stamps, now + 7 * 86400000);
  return { tMin, tMax };
}

function timeToX(t: number, scale: TimeScale): number {
  const box = chartInnerBox(LAYOUT);
  return box.x0 + ((t - scale.tMin) / (scale.tMax - scale.tMin || 1)) * box.innerW;
}

function priceToY(price: number, yMin: number, yMax: number): number {
  const box = chartInnerBox(LAYOUT);
  return box.y1 - ((price - yMin) / (yMax - yMin || 1)) * box.innerH;
}

function yToPrice(y: number, yMin: number, yMax: number): number {
  const box = chartInnerBox(LAYOUT);
  const ratio = (box.y1 - y) / (box.innerH || 1);
  return yMin + ratio * (yMax - yMin);
}

function xToTime(x: number, scale: TimeScale): number {
  const box = chartInnerBox(LAYOUT);
  const ratio = (x - box.x0) / (box.innerW || 1);
  return scale.tMin + ratio * (scale.tMax - scale.tMin);
}

function formatTimeTick(ms: number): string {
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" }).format(new Date(ms));
}

function buildTimeTicks(scale: TimeScale, count = 5): number[] {
  const span = scale.tMax - scale.tMin;
  if (span <= 0) return [scale.tMin];
  return Array.from({ length: count }, (_, index) => scale.tMin + (span * index) / (count - 1));
}

export function OptionsHorizonChart({ payload, region, onRegionChange }: OptionsHorizonChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [drag, setDrag] = useState<{ x0: number; y0: number; x1: number; y1: number } | null>(null);

  const scale = useMemo(() => buildTimeScale(payload), [payload]);
  const prices = payload.historical.series.map((r) => r.close_usd);
  const forwardPrices = payload.forward.curve.map((r) => r.mark_price_usd);
  const impliedPrices = payload.implied?.prices_usd ?? [];
  const allPrices = [...prices, ...forwardPrices, ...impliedPrices, payload.spot_usd];
  const yMin = Math.min(...allPrices) * 0.92;
  const yMax = Math.max(...allPrices) * 1.08;
  const box = chartInnerBox(LAYOUT);
  const nowX = timeToX(Date.now(), scale);
  const priceTicks = useMemo(() => buildPriceAxisTicks(yMin, yMax, 5), [yMin, yMax]);
  const timeTicks = useMemo(() => buildTimeTicks(scale, 5), [scale]);

  const histPath = useMemo(() => {
    const pts = payload.historical.series;
    if (!pts.length) return "";
    return pts
      .map((row, i) => {
        const x = timeToX(parseMs(row.timestamp_utc), scale);
        const y = priceToY(row.close_usd, yMin, yMax);
        return `${i === 0 ? "M" : "L"}${x},${y}`;
      })
      .join(" ");
  }, [payload.historical.series, scale, yMin, yMax]);

  const onPointerDown = useCallback(
    (e: React.PointerEvent<SVGSVGElement>) => {
      const svg = svgRef.current;
      if (!svg) return;
      const rect = svg.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      setDrag({ x0: x, y0: y, x1: x, y1: y });
    },
    [],
  );

  const onPointerMove = useCallback(
    (e: React.PointerEvent<SVGSVGElement>) => {
      if (!drag) return;
      const svg = svgRef.current;
      if (!svg) return;
      const rect = svg.getBoundingClientRect();
      setDrag({ ...drag, x1: e.clientX - rect.left, y1: e.clientY - rect.top });
    },
    [drag],
  );

  const onPointerUp = useCallback(() => {
    if (!drag) return;
    const left = Math.min(drag.x0, drag.x1);
    const right = Math.max(drag.x0, drag.x1);
    const top = Math.min(drag.y0, drag.y1);
    const bottom = Math.max(drag.y0, drag.y1);
    if (right - left < 8 || bottom - top < 8) {
      setDrag(null);
      return;
    }
    const t0 = xToTime(left, scale);
    const t1 = xToTime(right, scale);
    const pLo = yToPrice(bottom, yMin, yMax);
    const pHi = yToPrice(top, yMin, yMax);
    onRegionChange({
      time_start_utc: new Date(t0).toISOString(),
      time_end_utc: new Date(t1).toISOString(),
      price_min_usd: Math.min(pLo, pHi),
      price_max_usd: Math.max(pLo, pHi),
    });
    setDrag(null);
  }, [drag, onRegionChange, scale, yMin, yMax]);

  const regionRect = useMemo(() => {
    if (!region) return null;
    const box = region.region;
    const x0 = timeToX(parseMs(box.time_start_utc), scale);
    const x1 = timeToX(parseMs(box.time_end_utc), scale);
    const yTop = priceToY(box.price_max_usd, yMin, yMax);
    const yBot = priceToY(box.price_min_usd, yMin, yMax);
    return { x: Math.min(x0, x1), y: Math.min(yTop, yBot), w: Math.abs(x1 - x0), h: Math.abs(yBot - yTop) };
  }, [region, scale, yMin, yMax]);

  const volMax = Math.max(...payload.historical.series.map((r) => r.volume ?? 0), 1);
  const impliedPdfPeak = Math.max(...(payload.implied?.pdf_pct ?? []), 0);
  const impliedExpiryX = payload.implied ? timeToX(parseMs(`${payload.implied.expiry_date}T00:00:00Z`), scale) : null;

  return (
    <div className="options-horizon-chart-wrap">
      <svg
        ref={svgRef}
        className="options-horizon-chart"
        viewBox={`0 0 ${LAYOUT.width} ${LAYOUT.height}`}
        role="img"
        aria-label="BTC price chart with options-implied forward curve"
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
        onPointerLeave={onPointerUp}
      >
        <rect x={0} y={0} width={LAYOUT.width} height={LAYOUT.height} fill="transparent" />
        <rect
          x={box.x0}
          y={box.y0}
          width={box.innerW}
          height={box.innerH}
          fill="rgba(255,255,255,0.012)"
          stroke={CHART_AXIS_STYLE.axisStroke}
        />
        {priceTicks.map((tick) => {
          const y = priceToY(tick, yMin, yMax);
          return (
            <g key={`price-${tick}`}>
              <line x1={box.x0} x2={box.x1} y1={y} y2={y} stroke={CHART_AXIS_STYLE.gridStroke} />
              <text x={box.x0 - 8} y={y + 4} textAnchor="end" fill={CHART_AXIS_STYLE.labelFill} fontSize={10}>
                {formatAxisPrice(tick)}
              </text>
            </g>
          );
        })}
        {timeTicks.map((tick) => {
          const x = timeToX(tick, scale);
          return (
            <g key={`time-${tick}`}>
              <line x1={x} x2={x} y1={box.y0} y2={box.y1} stroke={CHART_AXIS_STYLE.gridStroke} />
              <text x={x} y={box.y1 + 20} textAnchor="middle" fill={CHART_AXIS_STYLE.labelFill} fontSize={10}>
                {formatTimeTick(tick)}
              </text>
            </g>
          );
        })}
        {payload.historical.series.map((row) => {
          const x = timeToX(parseMs(row.timestamp_utc), scale);
          const v = row.volume ?? 0;
          const h = (v / volMax) * 34;
          return (
            <rect
              key={row.timestamp_utc}
              x={x - 1.5}
              y={box.y1 - h}
              width={3}
              height={h}
              fill="rgba(85, 187, 255, 0.2)"
            />
          );
        })}
        <line
          x1={nowX}
          x2={nowX}
          y1={box.y0}
          y2={box.y1}
          stroke="rgba(242, 182, 87, 0.35)"
          strokeDasharray="4 4"
        />
        <text x={nowX + 6} y={box.y0 + 14} fill="#f2b657" fontSize={10}>
          Now
        </text>
        {histPath ? (
          <path d={histPath} fill="none" stroke="rgba(85, 187, 255, 0.95)" strokeWidth={2.4} />
        ) : null}
        {payload.forward.curve.length > 1 ? (
          <polyline
            points={payload.forward.curve
              .map((pt) => {
                const x = timeToX(parseMs(pt.expiry_utc), scale);
                const y = priceToY(pt.mark_price_usd, yMin, yMax);
                return `${x},${y}`;
              })
              .join(" ")}
            fill="none"
            stroke="rgba(242, 182, 87, 0.78)"
            strokeWidth={2}
            strokeDasharray="7 5"
          />
        ) : null}
        {payload.forward.curve.map((pt) => {
          const x = timeToX(parseMs(pt.expiry_utc), scale);
          const y = priceToY(pt.mark_price_usd, yMin, yMax);
          return (
            <g key={pt.expiry_date}>
              <circle cx={x} cy={y} r={4.5} fill="#f2b657" stroke="#07111c" strokeWidth={1.2} />
              <text x={x + 7} y={y - 7} fill="#c6d5e4" fontSize={9}>
                {pt.expiry_date.slice(5)}
              </text>
            </g>
          );
        })}
        {payload.implied && impliedExpiryX !== null && impliedPdfPeak > 0
          ? payload.implied.prices_usd.map((price, index) => {
              const pdf = payload.implied?.pdf_pct[index] ?? 0;
              const y = priceToY(price, yMin, yMax);
              const width = 4 + (pdf / impliedPdfPeak) * 32;
              return (
                <line
                  key={`implied-contour-${price}-${index}`}
                  x1={impliedExpiryX - width}
                  x2={impliedExpiryX + width}
                  y1={y}
                  y2={y}
                  stroke="rgba(158, 139, 255, 0.34)"
                  strokeWidth={1.2}
                />
              );
            })
          : null}
        {regionRect ? (
          <rect
            x={regionRect.x}
            y={regionRect.y}
            width={regionRect.w}
            height={regionRect.h}
            fill="rgba(80, 200, 160, 0.12)"
            stroke="rgba(80, 200, 160, 0.85)"
            strokeWidth={1.5}
          />
        ) : null}
        {drag ? (
          <rect
            x={Math.min(drag.x0, drag.x1)}
            y={Math.min(drag.y0, drag.y1)}
            width={Math.abs(drag.x1 - drag.x0)}
            height={Math.abs(drag.y1 - drag.y0)}
            fill="rgba(80, 200, 160, 0.08)"
            stroke="rgba(80, 200, 160, 0.6)"
            strokeDasharray="4 3"
          />
        ) : null}
        <g className="options-horizon-svg-legend">
          <circle cx={box.x0} cy={LAYOUT.height - 12} r={3} fill="#55bbff" />
          <text x={box.x0 + 9} y={LAYOUT.height - 8} fill="#8ea4bd" fontSize={10}>
            Spot history
          </text>
          <line
            x1={box.x0 + 98}
            x2={box.x0 + 120}
            y1={LAYOUT.height - 12}
            y2={LAYOUT.height - 12}
            stroke="#f2b657"
            strokeWidth={2}
            strokeDasharray="7 5"
          />
          <text x={box.x0 + 127} y={LAYOUT.height - 8} fill="#8ea4bd" fontSize={10}>
            Forward curve
          </text>
          <rect x={box.x0 + 230} y={LAYOUT.height - 18} width={14} height={8} fill="rgba(85, 187, 255, 0.2)" />
          <text x={box.x0 + 251} y={LAYOUT.height - 8} fill="#8ea4bd" fontSize={10}>
            Volume
          </text>
          <line
            x1={box.x0 + 310}
            x2={box.x0 + 332}
            y1={LAYOUT.height - 12}
            y2={LAYOUT.height - 12}
            stroke="rgba(158, 139, 255, 0.72)"
            strokeWidth={2}
          />
          <text x={box.x0 + 339} y={LAYOUT.height - 8} fill="#8ea4bd" fontSize={10}>
            Implied expiry
          </text>
        </g>
      </svg>
      <p className="micro">Drag on the chart to draw a thesis region (simulation only).</p>
    </div>
  );
}
