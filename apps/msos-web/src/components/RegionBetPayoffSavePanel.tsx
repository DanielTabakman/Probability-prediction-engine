"use client";

import { useMemo, useState } from "react";

import type { RegionBetContract } from "@/lib/regionBet";
import {
  buildRegionBetPayoffExplanation,
  canConfirmRegionBetPayoff,
  restoreRegionBetFrozenEntrySnapshot,
} from "@/lib/regionBetPayoff";

export type RegionBetPayoffSaveStatus = "idle" | "saving" | "saved" | "invalid" | "offline";

type RegionBetPayoffSavePanelProps = {
  draft: RegionBetContract;
  status: RegionBetPayoffSaveStatus;
  onConfirmPayoff: () => void;
};

export function RegionBetPayoffSavePanel({
  draft,
  status,
  onConfirmPayoff,
}: RegionBetPayoffSavePanelProps) {
  const [confirmed, setConfirmed] = useState(false);
  const explanation = useMemo(() => buildRegionBetPayoffExplanation(draft), [draft]);
  const frozen = restoreRegionBetFrozenEntrySnapshot(draft);
  const canConfirm = !frozen && confirmed && canConfirmRegionBetPayoff(draft);
  const statusCopy =
    status === "saving"
      ? "Saving active paper Region Bet..."
      : status === "saved"
        ? "Active paper Region Bet saved with a frozen entry snapshot."
        : status === "invalid"
          ? "Select a paper expression and confirm the payoff explanation before activation."
          : status === "offline"
            ? "Saved locally; server sync can retry from this Region Bet contract."
            : frozen
              ? "Frozen entry snapshot is attached to this monitorable paper Region Bet."
              : "Draft remains editable until you confirm the payoff explanation.";

  return (
    <div className="panel chart" data-testid="region-bet-payoff-save-panel">
      <div className="panel-head">
        <div>
          <h2>Payoff explanation and save</h2>
          <div className="panel-sub">
            Confirmation freezes the entry snapshot for monitoring. Paper only.
          </div>
        </div>
        <span className="tag teal">Confirm</span>
      </div>

      {explanation ? (
        <>
          <div className="decision-strip">
            <div>
              <strong>{explanation.headline}</strong>
              <p>{explanation.payoff_copy}</p>
            </div>
          </div>
          <div aria-label="Payoff scenarios">
            {explanation.scenario_copy.map((scenario) => (
              <div className="option-row dimmed" key={scenario.id}>
                <div>
                  <h3>{scenario.label}</h3>
                  <p>{scenario.copy}</p>
                </div>
              </div>
            ))}
          </div>
          <p className="micro">{explanation.limitation}</p>
        </>
      ) : (
        <p className="micro">
          Choose a paper expression before saving an active monitorable Region Bet.
        </p>
      )}

      {frozen ? (
        <div className="score" aria-label="Frozen entry snapshot">
          <div className="small-panel">
            <div className="k">Entry spot</div>
            <div className="v teal">{frozen.entry.spot_usd}</div>
          </div>
          <div className="small-panel">
            <div className="k">Observed</div>
            <div className="v">{frozen.market_snapshot.as_of_utc.slice(0, 10)}</div>
          </div>
          <div className="small-panel">
            <div className="k">Expression</div>
            <div className="v amber">{frozen.selected_expression_ref.expression_id}</div>
          </div>
        </div>
      ) : null}

      <label>
        <input
          type="checkbox"
          checked={confirmed || Boolean(frozen)}
          disabled={Boolean(frozen)}
          onChange={(event) => setConfirmed(event.currentTarget.checked)}
        />
        <span>I confirm this paper payoff explanation and want to save it for monitoring.</span>
      </label>

      <div className="decision-strip">
        <div>
          <strong>{statusCopy}</strong>
        </div>
        <button
          type="button"
          className="btn slim primary"
          disabled={!canConfirm || status === "saving"}
          onClick={onConfirmPayoff}
        >
          Confirm and save
        </button>
      </div>
    </div>
  );
}
