"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import type { LabDataMode } from "@/lib/strategyLabCopy";
import { ExpiryPicker } from "@/components/ExpiryPicker";
import { StrategyLabInteractivePanel } from "@/components/StrategyLabInteractivePanel";
import { outcomeSummary, strategyLabMetrics } from "@/data/strategyLabFixtures";
import {
  buildLabMetricsFromPayload,
  listExpiryDates,
  type DisplayPayload,
  type LabMetric,
} from "@/lib/ppeDisplayPayload";
import { saveStrategyLabExpiry } from "@/lib/strategyLabExpiry";

const DEMO_EXPIRY_OPTIONS = ["30 days", "60 days", "90 days"];

type StrategyLabWorkSectionProps = {
  displayPayload: DisplayPayload | null;
  dataMode: LabDataMode;
};

export function StrategyLabWorkSection({ displayPayload, dataMode }: StrategyLabWorkSectionProps) {
  const live = dataMode === "live" && displayPayload != null;
  const expiryOptions = useMemo(
    () => (live && displayPayload ? listExpiryDates(displayPayload) : DEMO_EXPIRY_OPTIONS),
    [live, displayPayload],
  );
  const [selectedExpiry, setSelectedExpiry] = useState(() => expiryOptions[0] ?? "30 days");

  const resolvedExpiry = expiryOptions.includes(selectedExpiry)
    ? selectedExpiry
    : (expiryOptions[0] ?? selectedExpiry);

  const handleExpiryChange = useCallback((expiry: string) => {
    setSelectedExpiry(expiry);
    saveStrategyLabExpiry(expiry);
  }, []);

  useEffect(() => {
    if (resolvedExpiry) {
      saveStrategyLabExpiry(resolvedExpiry);
    }
  }, [resolvedExpiry]);

  const metrics: LabMetric[] = useMemo(() => {
    if (!live || !displayPayload) {
      return strategyLabMetrics.map((metric) =>
        metric.label === "Expiry" ? { ...metric, value: resolvedExpiry } : metric,
      );
    }
    return buildLabMetricsFromPayload(displayPayload, resolvedExpiry);
  }, [live, displayPayload, resolvedExpiry]);

  return (
    <>
      <section className="metrics" aria-label="Lab context" data-tour="lab-expiry">
        {metrics.map((metric) => (
          <div key={metric.label} className="metric">
            <div className="label">{metric.label}</div>
            {metric.label === "Expiry" ? (
              <ExpiryPicker
                className="metric-expiry-value"
                value={resolvedExpiry}
                options={expiryOptions}
                onChange={handleExpiryChange}
                disabled={expiryOptions.length <= 1}
              />
            ) : (
              <div className={`value ${metric.tone ?? ""}`.trim()}>{metric.value}</div>
            )}
          </div>
        ))}
      </section>

      <section className="work strategy-lab-work">
        <StrategyLabInteractivePanel
          displayPayload={displayPayload}
          live={live}
          dataMode={dataMode}
          defaultOutcome={outcomeSummary}
          selectedExpiry={resolvedExpiry}
          onExpiryChange={handleExpiryChange}
          expiryOptions={expiryOptions}
        />
      </section>
    </>
  );
}
