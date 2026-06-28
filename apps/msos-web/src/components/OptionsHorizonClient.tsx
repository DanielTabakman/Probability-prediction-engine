"use client";

import Link from "next/link";
import type { ChangeEvent } from "react";
import { useCallback, useEffect, useState } from "react";

import { LabeledDistributionChart } from "@/components/LabeledDistributionChart";
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

function expiryTsFromUtc(expiryUtc: string): number {
  return Math.floor(new Date(expiryUtc).getTime() / 1000);
}

export function OptionsHorizonClient({ initialPayload }: OptionsHorizonClientProps) {
  const [payload, setPayload] = useState<HorizonChartPayload | null>(initialPayload);
  const [region, setRegion] = useState<HorizonRegionIntent | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(!initialPayload);
  const [expiryLoading, setExpiryLoading] = useState(false);

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

  const expiryOptions =
    payload?.forward.curve.map((pt) => ({
      expiryDate: pt.expiry_date,
      expiryTs: expiryTsFromUtc(pt.expiry_utc),
    })) ?? [];

  const selectedExpiryTs = payload?.implied?.expiry_ts ?? expiryOptions[0]?.expiryTs ?? "";
  const impliedChartLayout = { width: 360, height: 260, padLeft: 54, padRight: 14, padTop: 14, padBottom: 38 };

  const onExpiryChange = useCallback(async (event: ChangeEvent<HTMLSelectElement>) => {
    const nextExpiryTs = Number(event.target.value);
    if (!Number.isFinite(nextExpiryTs)) return;
    setExpiryLoading(true);
    const nextPayload = await fetchHorizonChartPayload({ expiryTs: nextExpiryTs });
    if (nextPayload) {
      setPayload(nextPayload);
      setRegion(null);
      setPreview(null);
    }
    setExpiryLoading(false);
  }, []);

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

      <div className="options-horizon-layout">
        <OptionsHorizonChart payload={payload} region={region} onRegionChange={onRegionChange} />

        <aside className="options-horizon-side" aria-label="Options Horizon chart controls">
          <section className="options-horizon-panel">
            <label className="options-horizon-field">
              <span>Expiry</span>
              <select
                value={selectedExpiryTs}
                onChange={onExpiryChange}
                disabled={expiryLoading || !expiryOptions.length}
              >
                {expiryOptions.map((option) => (
                  <option key={option.expiryTs} value={option.expiryTs}>
                    {option.expiryDate}
                  </option>
                ))}
              </select>
            </label>
            <div className="options-horizon-stat-grid">
              <div>
                <span>Spot</span>
                <strong>
                  ${payload.spot_usd.toLocaleString("en-US", { maximumFractionDigits: 0 })}
                </strong>
              </div>
              <div>
                <span>Implied forward</span>
                <strong>
                  {payload.implied
                    ? `$${payload.implied.forward_usd.toLocaleString("en-US", { maximumFractionDigits: 0 })}`
                    : "Unavailable"}
                </strong>
              </div>
              <div>
                <span>ATM IV</span>
                <strong>
                  {payload.implied
                    ? `${(payload.implied.atm_iv_annual * 100).toFixed(1)}%`
                    : "Unavailable"}
                </strong>
              </div>
            </div>
            <p className="micro">
              Display-only options context. Changing expiry refetches the Python chart payload.
            </p>
          </section>

          <section className="options-horizon-panel options-horizon-distribution-panel">
            <div>
              <p className="eyebrow">Implied distribution</p>
              <h2>{payload.implied?.expiry_date ?? "Selected expiry"}</h2>
            </div>
            {payload.implied ? (
              <LabeledDistributionChart
                pricesUsd={payload.implied.prices_usd}
                marketPdfPct={payload.implied.pdf_pct}
                spotUsd={payload.spot_usd}
                ariaLabel={`Options-implied distribution for ${payload.asset_id} at ${payload.implied.expiry_date}`}
                curveLabels={{
                  market_legend: "Options-implied probability",
                  belief_legend: "Your view",
                  payoff_legend: "Payoff at expiry",
                  market_method: "Python payload",
                }}
                priceAxisLabel="Price at expiry"
                layout={impliedChartLayout}
              />
            ) : (
              <p className="micro">Implied distribution unavailable for this expiry.</p>
            )}
          </section>
        </aside>
      </div>

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
