"use client";

import { useEffect, useState } from "react";

import { strategyLabBeliefBuilder } from "@/content/strategyLab";
import {
  BELIEF_PRESETS,
  buildBeliefSentence,
  loadStoredBeliefPresetId,
  saveBeliefPresetId,
  type BeliefPreset,
  type BeliefPresetId,
} from "@/lib/beliefPresets";

type BeliefBuilderProps = {
  expiryLabel: string;
  selectedId: BeliefPresetId | null;
  onSelect: (preset: BeliefPreset) => void;
};

export function BeliefBuilder({ expiryLabel, selectedId, onSelect }: BeliefBuilderProps) {
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
  const [chipHigher, chipLower, chipMoreVol, chipLessVol] = strategyLabBeliefBuilder.pickOneChips;

  return (
    <div className="belief-builder">
      <h3>{strategyLabBeliefBuilder.title}</h3>
      <p className="selectline" aria-live="polite">
        {selected ? (
          buildBeliefSentence(selected, expiryLabel)
        ) : (
          <>
            {strategyLabBeliefBuilder.pickOnePrefix}{" "}
            <span className="selectchip muted">{chipHigher}</span>,{" "}
            <span className="selectchip muted">{chipLower}</span>,{" "}
            <span className="selectchip muted">{chipMoreVol}</span>, or{" "}
            <span className="selectchip muted">{chipLessVol}</span>{" "}
            {strategyLabBeliefBuilder.pickOneSuffix}
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
        {selected ? strategyLabBeliefBuilder.hintSelected : strategyLabBeliefBuilder.hintDefault}
      </p>
    </div>
  );
}
