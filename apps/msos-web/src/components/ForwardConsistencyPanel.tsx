"use client";

import { useEffect, useState } from "react";

import {
  DEMO_FORWARD_CONSISTENCY,
  fetchForwardConsistencyPayload,
  statusBadgeLabel,
  type ForwardConsistencyPayload,
  type ForwardConsistencyStatus,
} from "@/lib/forwardConsistency";
import type { DisplayAssetMeta, DisplayPayload } from "@/lib/ppeDisplayPayload";
import { findSeriesByExpiry } from "@/lib/ppeDisplayPayload";
import { useDisplayCurrency } from "@/lib/useDisplayCurrency";

type ForwardConsistencyPanelProps = {
  assetMeta: DisplayAssetMeta;
  expiryDate: string;
  displayPayload: DisplayPayload | null;
  live: boolean;
};

function statusTone(status: ForwardConsistencyStatus | undefined): string {
  switch (status) {
    case "POSSIBLE_ARB":
      return "amber";
    case "WATCH":
      return "teal";
    case "BAD_DATA":
    case "NOT_COMPARABLE":
      return "muted";
    default:
      return "";
  }
}

export function ForwardConsistencyPanel({
  assetMeta,
  expiryDate,
  displayPayload,
  live,
}: ForwardConsistencyPanelProps) {
  const { formatMoney } = useDisplayCurrency();
  const [payload, setPayload] = useState<ForwardConsistencyPayload | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!expiryDate) {
      setPayload(null);
      return;
    }
    if (!live) {
      setPayload({ ...DEMO_FORWARD_CONSISTENCY, asset_id: assetMeta.id, expiry_date: expiryDate });
      return;
    }
    let cancelled = false;
    setLoading(true);
    void fetchForwardConsistencyPayload(expiryDate, assetMeta.id).then((data) => {
      if (!cancelled) {
        setPayload(data);
        setLoading(false);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [live, expiryDate, assetMeta.id]);

  const series = displayPayload ? findSeriesByExpiry(displayPayload, expiryDate) : undefined;
  const chartMedian =
    series?.quartiles_usd?.median_usd ?? series?.mean_usd ?? displayPayload?.spot_usd ?? null;

  const status = payload?.status;
  const fmt = (value: number | null | undefined) =>
    typeof value === "number" && Number.isFinite(value) ? formatMoney(value) : "—";

  return (
    <section
      className="forward-consistency panel compact"
      aria-label="No-arbitrage forward consistency check"
    >
      <div className="forward-consistency-header">
        <h3>No-Arbitrage Check</h3>
        <span className={`forward-consistency-badge ${statusTone(status)}`.trim()}>
          {loading ? "Loading…" : statusBadgeLabel(status)}
        </span>
      </div>
      <p className="micro forward-consistency-note">
        {payload?.copy_note ??
          "Spot vs future distribution is not arbitrage. This checks whether options imply a different executable forward than the futures/perp market after spreads and estimated costs."}
      </p>
      <div className="forward-consistency-grid">
        <div className="forward-consistency-cell">
          <div className="forward-consistency-k">Spot</div>
          <div className="forward-consistency-v">
            {fmt(payload?.spot_usd ?? displayPayload?.spot_usd)}
          </div>
        </div>
        <div className="forward-consistency-cell">
          <div className="forward-consistency-k">Chart median (not for arb)</div>
          <div className="forward-consistency-v muted">{fmt(chartMedian)}</div>
        </div>
        <div className="forward-consistency-cell">
          <div className="forward-consistency-k">Synthetic forward bid / ask</div>
          <div className="forward-consistency-v">
            {fmt(payload?.synthetic_bid)} – {fmt(payload?.synthetic_ask)}
          </div>
        </div>
        <div className="forward-consistency-cell">
          <div className="forward-consistency-k">Future / perp bid / ask</div>
          <div className="forward-consistency-v">
            {fmt(payload?.future_bid)} – {fmt(payload?.future_ask)}
          </div>
        </div>
        <div className="forward-consistency-cell">
          <div className="forward-consistency-k">Gross edge</div>
          <div className="forward-consistency-v">{fmt(payload?.gross_edge_usd)}</div>
        </div>
        <div className="forward-consistency-cell">
          <div className="forward-consistency-k">Est. cost</div>
          <div className="forward-consistency-v">{fmt(payload?.estimated_cost_usd)}</div>
        </div>
        <div className="forward-consistency-cell">
          <div className="forward-consistency-k">Net edge</div>
          <div className={`forward-consistency-v ${statusTone(status)}`.trim()}>
            {fmt(payload?.net_edge_usd)}
          </div>
        </div>
      </div>
      {payload?.detail ? (
        <p className="micro forward-consistency-detail">{payload.detail}</p>
      ) : null}
      {status === "POSSIBLE_ARB" && payload?.legs && payload.legs.length > 0 ? (
        <div className="forward-consistency-legs">
          <div className="forward-consistency-k">Suggested legs (simulation only)</div>
          <ul>
            {payload.legs.map((leg) => (
              <li key={`${leg.side}-${leg.instrument_type}`}>
                {leg.side.toUpperCase()} — {leg.label}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      <p className="micro forward-consistency-footer">Research only — not order execution.</p>
    </section>
  );
}
