"use client";

import { useEffect, useState } from "react";

import { ExpiryPicker } from "@/components/ExpiryPicker";
import {
  BELIEF_PRESETS,
  loadStoredBeliefPresetId,
  saveBeliefPresetId,
  type BeliefPreset,
  type BeliefPresetId,
} from "@/lib/beliefPresets";

type BeliefBuilderProps = {
  expiryLabel: string;
  expiryOptions: string[];
  onExpiryChange: (expiry: string) => void;
  expiryPickerDisabled?: boolean;
  selectedId: BeliefPresetId | null;
  onSelect: (preset: BeliefPreset) => void;
};

export function BeliefBuilder({
  expiryLabel,
  expiryOptions,
  onExpiryChange,
  expiryPickerDisabled = false,
  selectedId,
  onSelect,
}: BeliefBuilderProps) {
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    const stored = loadStoredBeliefPresetId();
    if (stored) {
      const preset = BELIEF_PRESETS.find((p) => p.id === stored);
      if (preset) onSelect(preset);
    }
    setHydrated(true);
  }, [onSelect]);

  function handleSelect(preset: BeliefPreset) {
    saveBeliefPresetId(preset.id);
    onSelect(preset);
  }

  const selected = BELIEF_PRESETS.find((p) => p.id === selectedId) ?? null;

  return (
    <div className="belief-builder">
      <h3>What do you believe?</h3>
      <p className="selectline" aria-live="polite">
        {selected ? (
          <>
            I think BTC will {selected.directionPhrase} by{" "}
            <ExpiryPicker
              value={expiryLabel}
              options={expiryOptions}
              onChange={onExpiryChange}
              disabled={expiryPickerDisabled}
              className="selectchip"
            />
            .
          </>
        ) : (
          <>
            Pick one —{" "}
            <span className="selectchip muted">higher</span>,{" "}
            <span className="selectchip muted">lower</span>,{" "}
            <span className="selectchip muted">more vol</span>, or{" "}
            <span className="selectchip muted">less vol</span> than options imply.
          </>
        )}
      </p>

      <div className="belief-preset-grid" role="group" aria-label="Belief presets">
        {BELIEF_PRESETS.map((preset) => {
          const active = preset.id === selectedId;
          return (
            <button
              key={preset.id}
              type="button"
              className={`belief-preset${active ? " active" : ""}`}
              aria-pressed={active}
              onClick={() => handleSelect(preset)}
              disabled={!hydrated}
            >
              {preset.label}
            </button>
          );
        })}
      </div>

      <p className="micro">
        {selected
          ? "This compares your view to the market curve — not a trade recommendation."
          : "Tap a button to see how your view differs from what options price."}
      </p>
    </div>
  );
}
