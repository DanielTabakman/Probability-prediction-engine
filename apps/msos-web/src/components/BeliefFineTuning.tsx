"use client";

import {
  BELIEF_TUNING_BOUNDS,
  clampTuningValue,
  formatCenterShiftLabel,
  formatRangeWidthLabel,
  type BeliefTuning,
} from "@/lib/beliefTuning";

type BeliefFineTuningProps = {
  tuning: BeliefTuning;
  disabled?: boolean;
  onChange: (next: BeliefTuning) => void;
};

export function BeliefFineTuning({ tuning, disabled = false, onChange }: BeliefFineTuningProps) {
  const forwardBounds = BELIEF_TUNING_BOUNDS.forward_mult;
  const volBounds = BELIEF_TUNING_BOUNDS.vol_mult;

  return (
    <div className="controls" aria-label="Fine-tune your view">
      <div className="control">
        <div className="control-label">Center shift</div>
        <div className="control-value">{formatCenterShiftLabel(tuning.forward_mult)}</div>
        <input
          type="range"
          className="slider-input"
          min={forwardBounds.min}
          max={forwardBounds.max}
          step={0.01}
          value={tuning.forward_mult}
          disabled={disabled}
          aria-label="Center shift versus market"
          onChange={(event) =>
            onChange({
              ...tuning,
              forward_mult: clampTuningValue(
                "forward_mult",
                Number.parseFloat(event.target.value),
              ),
            })
          }
        />
      </div>
      <div className="control">
        <div className="control-label">Range width</div>
        <div className="control-value">{formatRangeWidthLabel(tuning.vol_mult)}</div>
        <input
          type="range"
          className="slider-input"
          min={volBounds.min}
          max={volBounds.max}
          step={0.01}
          value={tuning.vol_mult}
          disabled={disabled}
          aria-label="Range width versus market volatility"
          onChange={(event) =>
            onChange({
              ...tuning,
              vol_mult: clampTuningValue("vol_mult", Number.parseFloat(event.target.value)),
            })
          }
        />
      </div>
      <div className="control muted">
        <div className="control-label">Tail weight</div>
        <div className="control-value">Coming soon</div>
        <div className="slider preview muted" aria-hidden="true" />
      </div>
    </div>
  );
}
