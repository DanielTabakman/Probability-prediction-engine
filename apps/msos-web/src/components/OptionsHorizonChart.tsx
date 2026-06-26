"use client";

import { useCallback, useMemo, useRef, useState } from "react";

import {
  LABELED_CHART_LAYOUT,
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
  dates: string[];
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
  return { tMin, tMax, dates: [] };
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

export function OptionsHorizonChart({ payload, region, onRegionChange }: OptionsHorizonChartProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [drag, setDrag] = useState<{ x0: number; y0: number; x1: number; y1: number } | null>(null);

  const scale = useMemo(() => buildTimeScale(payload), [payload]);
  const prices = payload.historical.series.map((r) => r.close_usd);
  const forwardPrices = payload.forward.curve.map((r) => r.mark_price_usd);
  const allPrices = [...prices, ...forwardPrices, payload.spot_usd];
  const yMin = Math.min(...allPrices) * 0.92;
  const yMax = Math.max(...allPrices) * 1.08;
  const nowX = timeToX(Date.now(), scale);

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
    const x0 = timeToX(parseMs(region.time_start_utc), scale);
    const x1 = timeToX(parseMs(region.time_end_utc), scale);
    const yTop = priceToY(region.price_max_usd, yMin, yMax);
    const yBot = priceToY(region.price_min_usd, yMin, yMax);
    return { x: Math.min(x0, x1), y: Math.min(yTop, yBot), w: Math.abs(x1 - x0), h: Math.abs(yBot - yTop) };
  }, [region, scale, yMin, yMax]);

  const volMax = Math.max(...payload.historical.series.map((r) => r.volume ?? 0), 1);

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
        {payload.historical.series.map((row) => {
          const x = timeToX(parseMs(row.timestamp_utc), scale);
          const v = row.volume ?? 0;
          const h = (v / volMax) * 24;
          const box = chartInnerBox(LAYOUT);
          return (
            <rect
              key={row.timestamp_utc}
              x={x - 1}
              y={box.y1 - h}
              width={2}
              height={h}
              fill="rgba(120, 140, 170, 0.35)"
            />
          );
        })}
        <line
          x1={nowX}
          x2={nowX}
          y1={chartInnerBox(LAYOUT).y0}
          y2={chartInnerBox(LAYOUT).y1}
          stroke="rgba(255,255,255,0.2)"
          strokeDasharray="4 4"
        />
        {histPath ? (
          <path d={histPath} fill="none" stroke="rgba(100, 200, 255, 0.9)" strokeWidth={2} />
        ) : null}
        {payload.forward.curve.map((pt) => {
          const x = timeToX(parseMs(pt.expiry_utc), scale);
          const y = priceToY(pt.mark_price_usd, yMin, yMax);
          return (
            <circle
              key={pt.expiry_date}
              cx={x}
              cy={y}
              r={4}
              fill="rgba(255, 180, 80, 0.9)"
            />
          );
        })}
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
            stroke="rgba(255, 180, 80, 0.55)"
            strokeWidth={1.5}
            strokeDasharray="6 4"
          />
        ) : null}
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
        <text x={chartInnerBox(LAYOUT).x0} y={LAYOUT.height - 8} fill="#8ea4bd" fontSize={11}>
          {formatAxisPrice(yMin)} – {formatAxisPrice(yMax)}
        </text>
      </svg>
      <p className="micro">Drag on the chart to draw a thesis region (simulation only).</p>
    </div>
  );
}
