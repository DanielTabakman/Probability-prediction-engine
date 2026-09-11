"use client";

import { useEffect, useMemo, useState } from "react";

import { OptionsHorizonComparisonPanel } from "@/components/OptionsHorizonComparisonPanel";
import { fetchHorizonChartPayload, type HorizonChartPayload } from "@/lib/horizonChartPayload";
import {
  buildRegionBetMarketCompareFromChart,
  regionBetMarketCompareFetchParams,
} from "@/lib/regionBetMarketCompare";
import type { RegionBetGuidedShellSnapshot } from "@/lib/regionBetGuidedShell";

type RegionBetMarketComparePanelProps = {
  snapshot: RegionBetGuidedShellSnapshot;
};

export function RegionBetMarketComparePanel({ snapshot }: RegionBetMarketComparePanelProps) {
  const [payload, setPayload] = useState<HorizonChartPayload | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchParams = useMemo(
    () => regionBetMarketCompareFetchParams(snapshot),
    [snapshot],
  );

  useEffect(() => {
    let cancelled = false;
    if (!fetchParams) {
      setPayload(null);
      setLoading(false);
      return () => {
        cancelled = true;
      };
    }

    setLoading(true);
    void fetchHorizonChartPayload(fetchParams).then((nextPayload) => {
      if (cancelled) return;
      setPayload(nextPayload);
      setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [fetchParams]);

  const compare = useMemo(
    () => buildRegionBetMarketCompareFromChart(snapshot, payload),
    [payload, snapshot],
  );

  return (
    <div className="panel chart" data-testid="region-bet-market-compare-panel">
      <div className="panel-head">
        <div>
          <h2>Compare listed windows</h2>
          <div className="panel-sub">
            Current Region Bet context, shown against display-only Options Horizon buckets.
          </div>
        </div>
        <span className="tag">Compare</span>
      </div>

      <div className="score" aria-label="Region Bet compare context">
        <div className="small-panel">
          <div className="k">Asset</div>
          <div className="v teal">{snapshot.symbol ?? snapshot.asset_id}</div>
        </div>
        <div className="small-panel">
          <div className="k">Window</div>
          <div className="v">{snapshot.expiry_utc.slice(0, 10)}</div>
        </div>
        <div className="small-panel">
          <div className="k">Region</div>
          <div className="v amber">
            {snapshot.selected_region.price_min_usd} to {snapshot.selected_region.price_max_usd}
          </div>
        </div>
      </div>

      {loading ? (
        <p className="micro">Loading listed-window comparison...</p>
      ) : compare ? (
        <OptionsHorizonComparisonPanel comparison={compare.comparison} />
      ) : (
        <p className="micro">
          Listed-window comparison is unavailable for this draft. Educational comparison only; not financial advice, not a recommendation, and not order execution.
        </p>
      )}
    </div>
  );
}
