"use client";

import type {
  RegionBetGuidedShellStep,
  RegionBetGuidedShellSnapshot,
  RegionBetGuidedShellPatch,
} from "@/lib/regionBetGuidedShell";
import { RegionBetMarketComparePanel } from "@/components/RegionBetMarketComparePanel";
import {
  RegionBetPayoffSavePanel,
  type RegionBetPayoffSaveStatus,
} from "@/components/RegionBetPayoffSavePanel";
import { RegionBetRiskExpressionPanel } from "@/components/RegionBetRiskExpressionPanel";
import type { RegionBetContract } from "@/lib/regionBet";

export type RegionBetGuidedAssetOption = {
  asset_id: string;
  symbol?: string;
  venue?: string;
  spot_usd: number;
};

type RegionBetGuidedShellPanelProps = {
  step: RegionBetGuidedShellStep;
  draft: RegionBetContract;
  snapshot: RegionBetGuidedShellSnapshot;
  assetOptions: RegionBetGuidedAssetOption[];
  onDraftChange: (patch: RegionBetGuidedShellPatch) => void;
  onConfirmPayoff: () => void;
  payoffSaveStatus: RegionBetPayoffSaveStatus;
};

function datetimeValue(value: string | undefined): string {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toISOString().slice(0, 16);
}

function fromDatetimeInput(value: string): string | undefined {
  if (!value) return undefined;
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? undefined : parsed.toISOString();
}

function numberOrCurrent(value: string, current: number): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : current;
}

export function RegionBetGuidedShellPanel({
  step,
  draft,
  snapshot,
  assetOptions,
  onDraftChange,
  onConfirmPayoff,
  payoffSaveStatus,
}: RegionBetGuidedShellPanelProps) {
  if (step === "asset") {
    return (
      <div className="panel chart" data-testid="region-bet-guided-shell-panel">
        <div className="panel-head">
          <div>
            <h2>Choose the asset</h2>
            <div className="panel-sub">Simulation-only Region Bet draft.</div>
          </div>
          <span className="tag">Paper</span>
        </div>
        <div className="lab-setup-row">
          <label>
            <span>Asset</span>
            <select
              value={draft.asset.asset_id}
              onChange={(event) => {
                const selected = assetOptions.find(
                  (item) => item.asset_id === event.currentTarget.value,
                );
                if (!selected) return;
                onDraftChange({
                  asset: {
                    asset_id: selected.asset_id,
                    symbol: selected.symbol ?? selected.asset_id,
                    venue: selected.venue,
                  },
                  entry: { spot_usd: selected.spot_usd },
                });
              }}
            >
              {assetOptions.map((asset) => (
                <option key={asset.asset_id} value={asset.asset_id}>
                  {asset.symbol ?? asset.asset_id}
                </option>
              ))}
            </select>
          </label>
          <label>
            <span>Spot reference</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={draft.entry.spot_usd}
              onChange={(event) =>
                onDraftChange({
                  entry: {
                    spot_usd: numberOrCurrent(event.currentTarget.value, draft.entry.spot_usd),
                  },
                })
              }
            />
          </label>
        </div>
      </div>
    );
  }

  if (step === "window") {
    return (
      <div className="panel chart" data-testid="region-bet-guided-shell-panel">
        <div className="panel-head">
          <div>
            <h2>Set the expiry window</h2>
            <div className="panel-sub">Forward and back keeps these dates on the same draft.</div>
          </div>
          <span className="tag">Window</span>
        </div>
        <div className="lab-setup-row">
          <label>
            <span>Expiry</span>
            <input
              type="datetime-local"
              value={datetimeValue(draft.target.expiry_utc)}
              onChange={(event) => {
                const next = fromDatetimeInput(event.currentTarget.value);
                if (next) onDraftChange({ target: { expiry_utc: next } });
              }}
            />
          </label>
          <label>
            <span>Window start</span>
            <input
              type="datetime-local"
              value={datetimeValue(draft.target.window_start_utc)}
              onChange={(event) => {
                const next = fromDatetimeInput(event.currentTarget.value);
                if (next) {
                  onDraftChange({
                    target: { window_start_utc: next },
                    selected_region: { time_start_utc: next },
                  });
                }
              }}
            />
          </label>
          <label>
            <span>Window end</span>
            <input
              type="datetime-local"
              value={datetimeValue(draft.target.window_end_utc)}
              onChange={(event) => {
                const next = fromDatetimeInput(event.currentTarget.value);
                if (next) {
                  onDraftChange({
                    target: { window_end_utc: next },
                    selected_region: { time_end_utc: next },
                  });
                }
              }}
            />
          </label>
        </div>
      </div>
    );
  }

  if (step === "region") {
    return (
      <div className="panel chart" data-testid="region-bet-guided-shell-panel">
        <div className="panel-head">
          <div>
            <h2>Select the price-time region</h2>
            <div className="panel-sub">This shell stores the selected box, not execution intent.</div>
          </div>
          <span className="tag">Region</span>
        </div>
        <div className="lab-setup-row">
          <label>
            <span>Price min</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={draft.selected_region.price_min_usd}
              onChange={(event) =>
                onDraftChange({
                  selected_region: {
                    price_min_usd: numberOrCurrent(
                      event.currentTarget.value,
                      draft.selected_region.price_min_usd,
                    ),
                  },
                })
              }
            />
          </label>
          <label>
            <span>Price max</span>
            <input
              type="number"
              min="0"
              step="0.01"
              value={draft.selected_region.price_max_usd}
              onChange={(event) =>
                onDraftChange({
                  selected_region: {
                    price_max_usd: numberOrCurrent(
                      event.currentTarget.value,
                      draft.selected_region.price_max_usd,
                    ),
                  },
                })
              }
            />
          </label>
        </div>
      </div>
    );
  }

  if (step === "compare") {
    return <RegionBetMarketComparePanel snapshot={snapshot} />;
  }

  return (
    <>
      <div className="panel chart" data-testid="region-bet-guided-shell-panel">
        <div className="panel-head">
          <div>
            <h2>Review the Region Bet</h2>
            <div className="panel-sub">Draft persistence uses the Region Bet contract.</div>
          </div>
          <span className="tag teal">Ready</span>
        </div>
        <div className="score" aria-label="Region Bet draft summary">
          <div className="small-panel">
            <div className="k">Asset</div>
            <div className="v teal">{snapshot.symbol ?? snapshot.asset_id}</div>
          </div>
          <div className="small-panel">
            <div className="k">Expiry</div>
            <div className="v">{snapshot.expiry_utc.slice(0, 10)}</div>
          </div>
          <div className="small-panel">
            <div className="k">Region</div>
            <div className="v amber">
              {snapshot.selected_region.price_min_usd} to {snapshot.selected_region.price_max_usd}
            </div>
          </div>
        </div>
        <label>
          <span>Note</span>
          <textarea
            value={draft.user_note ?? ""}
            onChange={(event) => onDraftChange({ user_note: event.currentTarget.value })}
          />
        </label>
      </div>
      <RegionBetRiskExpressionPanel draft={draft} onDraftChange={onDraftChange} />
      <RegionBetPayoffSavePanel
        draft={draft}
        status={payoffSaveStatus}
        onConfirmPayoff={onConfirmPayoff}
      />
    </>
  );
}
