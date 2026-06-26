"use client";

import { ExpiryPicker, formatExpiryLabel } from "@/components/ExpiryPicker";
import {
  buildTuningLabel,
  buildTuningPhrase,
  isMarketTuning,
  type BeliefNudgeAxis,
  type BeliefTuning,
} from "@/lib/beliefTuning";
import { BELIEF_TAIL_LIMIT_NOTE } from "@/lib/beliefTuningCopy";

type BeliefBuilderProps = {
  expiryLabel: string;
  expiryOptions: string[];
  onExpiryChange: (expiry: string) => void;
  expiryPickerDisabled?: boolean;
  /** When true, expiry is chosen in the strip above — show date as text only. */
  hideInlineExpiryPicker?: boolean;
  tuning: BeliefTuning;
  onNudge: (axis: BeliefNudgeAxis) => void;
  onReset: () => void;
};

function BeliefPairButton({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      className={`belief-preset${active ? " active" : ""}`}
      aria-pressed={active}
      onClick={onClick}
    >
      {label}
    </button>
  );
}

export function BeliefBuilder({
  expiryLabel,
  expiryOptions,
  onExpiryChange,
  expiryPickerDisabled = false,
  hideInlineExpiryPicker = false,
  tuning,
  onNudge,
  onReset,
}: BeliefBuilderProps) {
  const active = !isMarketTuning(tuning);
  const viewLabel = buildTuningLabel(tuning);
  const phrase = buildTuningPhrase(tuning);
  const expiryChip = hideInlineExpiryPicker ? (
    <span className="selectchip muted">{formatExpiryLabel(expiryLabel)}</span>
  ) : (
    <ExpiryPicker
      value={expiryLabel}
      options={expiryOptions}
      onChange={onExpiryChange}
      disabled={expiryPickerDisabled}
      className="selectchip"
    />
  );

  return (
    <div className="belief-builder" data-tour="lab-belief">
      <div className="belief-builder-head">
        <h3>What do you believe?</h3>
        <button
          type="button"
          className="btn slim dark belief-reset"
          onClick={onReset}
          disabled={!active}
        >
          Reset to market
        </button>
      </div>

      <p className="selectline" aria-live="polite">
        {active ? (
          <>
            I think BTC will {phrase} by {expiryChip}.
          </>
        ) : (
          <>
            Use the buttons below to say how you disagree with the market — for{" "}
            {expiryChip}.
          </>
        )}
      </p>

      <div className="belief-axis-list" aria-label="Belief controls">
        <div className="belief-axis-row" role="group" aria-label="Price versus market">
          <span className="belief-axis-label">Price</span>
          <div className="belief-axis-pair">
            <BeliefPairButton
              label="Higher"
              active={tuning.forward_mult > 1.002}
              onClick={() => onNudge("higher")}
            />
            <BeliefPairButton
              label="Lower"
              active={tuning.forward_mult < 0.998}
              onClick={() => onNudge("lower")}
            />
          </div>
        </div>

        <div className="belief-axis-row" role="group" aria-label="Volatility versus market">
          <span className="belief-axis-label">Volatility</span>
          <div className="belief-axis-pair">
            <BeliefPairButton
              label="More vol"
              active={tuning.vol_mult > 1.02}
              onClick={() => onNudge("more_vol")}
            />
            <BeliefPairButton
              label="Less vol"
              active={tuning.vol_mult < 0.98}
              onClick={() => onNudge("less_vol")}
            />
          </div>
        </div>
      </div>

      <p className="micro">
        {active
          ? `Your view: ${viewLabel}. Buttons nudge the curve; sliders fine-tune.`
          : "Each button push nudges the teal curve. Use Reset to return to the market view."}
      </p>
      <p className="micro belief-tail-note">{BELIEF_TAIL_LIMIT_NOTE}</p>
    </div>
  );
}
