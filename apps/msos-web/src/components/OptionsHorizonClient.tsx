"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import { OptionsHorizonChart } from "@/components/OptionsHorizonChart";
import {
  fetchHorizonChartPayload,
  fetchHorizonRegionPreview,
  strategyLabDeepLink,
  type HorizonChartPayload,
} from "@/lib/horizonChartPayload";
import {
  loadHorizonRegion,
  newRegionId,
  saveHorizonRegion,
  type HorizonRegionIntent,
} from "@/lib/horizonRegion";

type OptionsHorizonClientProps = {
  initialPayload: HorizonChartPayload | null;
};

export function OptionsHorizonClient({ initialPayload }: OptionsHorizonClientProps) {
  const [payload, setPayload] = useState<HorizonChartPayload | null>(initialPayload);
  const [region, setRegion] = useState<HorizonRegionIntent | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(!initialPayload);

  useEffect(() => {
    setRegion(loadHorizonRegion());
  }, []);

  useEffect(() => {
    if (initialPayload) return;
    void (async () => {
      setLoading(true);
      const data = await fetchHorizonChartPayload();
      setPayload(data);
      setLoading(false);
    })();
  }, [initialPayload]);

  const onRegionChange = useCallback(
    async (box: HorizonRegionIntent["region"] | null) => {
      if (!box || !payload?.implied) {
        setRegion(null);
        setPreview(null);
        return;
      }
      const intent: HorizonRegionIntent = {
        schema_version: 1,
        id: newRegionId(),
        asset_id: payload.asset_id,
        venue: "deribit",
        created_at_utc: new Date().toISOString(),
        region: box,
        bias: "bullish_in_region",
        linked_expiry_ts: payload.implied.expiry_ts,
      };
      const prev = await fetchHorizonRegionPreview({
        priceMinUsd: box.price_min_usd,
        priceMaxUsd: box.price_max_usd,
        timeEndUtc: box.time_end_utc,
        expiryTs: payload.implied.expiry_ts,
        forwardUsd: payload.implied.forward_usd,
        atmIvAnnual: payload.implied.atm_iv_annual,
        tYears: payload.implied.T_years,
      });
      if (prev?.computed) {
        intent.computed = {
          implied_mass_pct: prev.computed.implied_mass_pct,
          method: prev.computed.method,
          as_of_utc: payload.as_of_utc,
        };
        setPreview(
          `Implied mass in region: ${prev.computed.implied_mass_pct.toFixed(1)}% (${prev.computed.method.replace(/_/g, " ")}).`,
        );
      } else {
        setPreview("Could not compute implied mass for this region.");
      }
      setRegion(intent);
      saveHorizonRegion(intent);
    },
    [payload],
  );

  if (loading) {
    return <p className="footer-note">Loading Options Horizon…</p>;
  }
  if (!payload) {
    return (
      <div className="panel-sub">
        <p>Chart data unavailable. Ensure the display API is running.</p>
      </div>
    );
  }

  const labLink = strategyLabDeepLink(payload);

  return (
    <div className="options-horizon-work">
      <header className="page-header">
        <div>
          <p className="eyebrow">Options Horizon</p>
          <h1>Price, implied forward, and thesis region</h1>
          <p className="panel-sub">
            Simulation only — not order execution. BTC spot + volume, futures forward curve, and
            options-implied slice at {payload.implied?.expiry_date ?? "selected expiry"}.
          </p>
        </div>
      </header>

      <OptionsHorizonChart payload={payload} region={region} onRegionChange={onRegionChange} />

      {preview ? (
        <div className="panel-sub options-horizon-preview" role="status">
          <strong>Thesis region</strong>
          <p>{preview}</p>
          <p className="micro">
            Suggested next step: open Strategy Lab to explore expressions that fit this region
            (simulation).
          </p>
          <Link href={labLink} className="btn slim primary">
            Open in Strategy Lab
          </Link>
        </div>
      ) : null}

      <div className="panel-sub micro">
        Archive: {payload.archive.available_days} day(s) collected
        {payload.archive.replay_ready
          ? " — replay scrubber eligible"
          : ` — replay after ${payload.archive.replay_threshold_days} days`}
      </div>
    </div>
  );
}
