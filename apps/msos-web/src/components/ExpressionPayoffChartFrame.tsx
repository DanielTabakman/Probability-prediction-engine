"use client";

import { useEffect, useState } from "react";

import { ExpressionPayoffChart } from "@/components/ExpressionPayoffChart";
import type { ComponentProps } from "react";

type Props = ComponentProps<typeof ExpressionPayoffChart>;

export function ExpressionPayoffChartFrame(props: Props) {
  const [fullscreen, setFullscreen] = useState(false);

  useEffect(() => {
    if (!fullscreen) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setFullscreen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [fullscreen]);

  const chart = (
    <ExpressionPayoffChart {...props} className={fullscreen ? "chart-fullscreen-inner" : undefined} />
  );

  return (
    <>
      <button
        type="button"
        className="expression-chart-expand"
        onClick={() => setFullscreen(true)}
        aria-label="Expand chart to full screen"
      >
        {chart}
        <span className="expression-chart-expand-hint">Click to expand</span>
      </button>
      {fullscreen ? (
        <div
          className="chart-fullscreen-backdrop"
          role="dialog"
          aria-modal="true"
          aria-label="Trade vs market chart full screen"
          onClick={() => setFullscreen(false)}
        >
          <div className="chart-fullscreen-panel" onClick={(event) => event.stopPropagation()}>
            <button
              type="button"
              className="btn slim chart-fullscreen-close"
              onClick={() => setFullscreen(false)}
            >
              Close
            </button>
            {chart}
          </div>
        </div>
      ) : null}
    </>
  );
}
