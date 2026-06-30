"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { buildStrategyLabPathWithAssetAndExpiry } from "@/components/AppNav";
import { ForwardConsistencyPanel } from "@/components/ForwardConsistencyPanel";
import {
  DEMO_FORWARD_CONSISTENCY_DASHBOARD,
  fetchForwardConsistencyDashboard,
  statusBadgeLabel,
  type ForwardConsistencyDashboardPayload,
  type ForwardConsistencyHeatmapCell,
  type ForwardConsistencyStatus,
} from "@/lib/forwardConsistency";
import { DEMO_FOOTER } from "@/lib/publicCopy";
import { resolveDisplayAssetMeta, type LabAssetId } from "@/lib/ppeDisplayPayload";

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

function formatNetEdge(value: number | null | undefined): string {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return "—";
  }
  const prefix = value > 0 ? "+" : "";
  return `${prefix}${value.toFixed(0)}`;
}

function uniqueSorted(values: string[]): string[] {
  return [...new Set(values.filter(Boolean))].sort();
}

type SelectedCell = {
  asset_id: string;
  expiry_date: string;
};

export function ForwardConsistencyDashboardContent() {
  const [dashboard, setDashboard] = useState<ForwardConsistencyDashboardPayload | null>(null);
  const [live, setLive] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<SelectedCell | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    void fetchForwardConsistencyDashboard().then((data) => {
      if (cancelled) return;
      if (data?.kind === "forward_consistency_dashboard" && data.cells?.length) {
        setDashboard(data);
        setLive(true);
        setSelected({ asset_id: data.cells[0].asset_id, expiry_date: data.cells[0].expiry_date });
      } else {
        setDashboard(DEMO_FORWARD_CONSISTENCY_DASHBOARD);
        setLive(false);
        const first = DEMO_FORWARD_CONSISTENCY_DASHBOARD.cells?.[0];
        if (first) {
          setSelected({ asset_id: first.asset_id, expiry_date: first.expiry_date });
        }
      }
      setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const cells = dashboard?.cells ?? [];
  const summary = dashboard?.summary;

  const assetIds = useMemo(() => uniqueSorted(cells.map((cell) => cell.asset_id)), [cells]);
  const expiryDates = useMemo(() => uniqueSorted(cells.map((cell) => cell.expiry_date)), [cells]);

  const cellByKey = useMemo(() => {
    const map = new Map<string, ForwardConsistencyHeatmapCell>();
    for (const cell of cells) {
      map.set(`${cell.asset_id}:${cell.expiry_date}`, cell);
    }
    return map;
  }, [cells]);

  const selectedCell =
    selected && cellByKey.get(`${selected.asset_id}:${selected.expiry_date}`);

  const assetMeta = resolveDisplayAssetMeta(
    null,
    (selected?.asset_id ?? "BTC") as LabAssetId,
  );

  return (
    <>
      <header className="topline">
        <div>
          <div className="crumb">Ops</div>
          <h1 className="title">Forward consistency</h1>
          <p className="monitor-lead">
            Asset × expiry heatmap — options-implied forward vs futures/perp. Research only, not
            trade signals.
          </p>
        </div>
        <div className="tools">
          <span className="pill">
            <span
              className={`dot ${live ? "teal" : "amber"}`}
              aria-hidden="true"
            />
            {loading ? "Loading…" : live ? "Live dashboard" : "Sample data"}
          </span>
        </div>
      </header>

      <section className="kpi-row fcr-summary" aria-label="Forward consistency summary">
        <div className="kpi">
          <div className="label">Assets checked</div>
          <div className="num">{summary?.assets_checked ?? "—"}</div>
        </div>
        <div className="kpi">
          <div className="label">Expiries checked</div>
          <div className="num">{summary?.expiries_checked ?? "—"}</div>
        </div>
        <div className="kpi">
          <div className="label">Watch</div>
          <div className="num">{summary?.watch_count ?? "—"}</div>
        </div>
        <div className="kpi">
          <div className="label">Possible arb</div>
          <div className="num">{summary?.possible_count ?? "—"}</div>
        </div>
        <div className="kpi">
          <div className="label">Bad data</div>
          <div className="num">{summary?.bad_data_count ?? "—"}</div>
        </div>
      </section>

      <section className="panel compact fcr-heatmap-panel" aria-label="Forward consistency heatmap">
        <div className="panel-head">
          <h2>Heatmap</h2>
          <p className="panel-sub">Click a cell for detail. Net edge in USD after estimated costs.</p>
        </div>
        <div className="fcr-heatmap-scroll">
          <table className="fcr-heatmap">
            <thead>
              <tr>
                <th scope="col">Asset</th>
                {expiryDates.map((expiry) => (
                  <th key={expiry} scope="col">
                    {expiry}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {assetIds.map((assetId) => (
                <tr key={assetId}>
                  <th scope="row">{assetId}</th>
                  {expiryDates.map((expiry) => {
                    const cell = cellByKey.get(`${assetId}:${expiry}`);
                    if (!cell) {
                      return (
                        <td key={`${assetId}-${expiry}`} className="fcr-heatmap-empty">
                          —
                        </td>
                      );
                    }
                    const isSelected =
                      selected?.asset_id === assetId && selected?.expiry_date === expiry;
                    return (
                      <td key={`${assetId}-${expiry}`}>
                        <button
                          type="button"
                          className={`fcr-heatmap-cell ${statusTone(cell.status)} ${isSelected ? "selected" : ""}`.trim()}
                          onClick={() => setSelected({ asset_id: assetId, expiry_date: expiry })}
                          aria-pressed={isSelected}
                          aria-label={`${assetId} ${expiry}: ${statusBadgeLabel(cell.status)}`}
                        >
                          <span className="fcr-heatmap-status">
                            {statusBadgeLabel(cell.status)}
                          </span>
                          <span className="fcr-heatmap-edge">{formatNetEdge(cell.net_edge_usd)}</span>
                        </button>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {selected && selectedCell ? (
        <section className="fcr-detail">
          <div className="fcr-detail-actions">
            <Link
              href={buildStrategyLabPathWithAssetAndExpiry(selected.asset_id, selected.expiry_date)}
              className="btn slim"
            >
              Open in Strategy Lab
            </Link>
          </div>
          <ForwardConsistencyPanel
            assetMeta={assetMeta}
            expiryDate={selected.expiry_date}
            displayPayload={null}
            live={live}
          />
          {selectedCell.quality_flags.length > 0 ? (
            <p className="micro fcr-quality-flags">
              Quality flags: {selectedCell.quality_flags.join(", ")}
            </p>
          ) : null}
        </section>
      ) : null}

      <details className="panel compact fcr-raw-drawer">
        <summary>Raw JSON (ops)</summary>
        <pre className="fcr-raw-json">
          {JSON.stringify(
            {
              dashboard,
              selected_cell: selectedCell ?? null,
            },
            null,
            2,
          )}
        </pre>
      </details>

      <p className="micro fcr-footer">{DEMO_FOOTER}</p>
    </>
  );
}
