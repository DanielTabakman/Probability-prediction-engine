"use client";

import { useEffect, useState } from "react";

import { ExpiryPicker } from "@/components/ExpiryPicker";
import {
  buildBeliefViewLabel,
  buildBeliefViewPhrase,
  hasBeliefView,
  loadStoredBeliefView,
  saveBeliefView,
  toggleBeliefDirection,
  toggleBeliefVolatility,
  type BeliefDirection,
  type BeliefView,
  type BeliefVolatility,
} from "@/lib/beliefPresets";

type BeliefBuilderProps = {
  expiryLabel: string;
  expiryOptions: string[];
  onExpiryChange: (expiry: string) => void;
  expiryPickerDisabled?: boolean;
  view: BeliefView;
  onChange: (view: BeliefView) => void;
};

function BeliefPairButton({
  label,
  active,
  disabled,
  onClick,
}: {
  label: string;
  active: boolean;
  disabled?: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      className={`belief-preset${active ? " active" : ""}`}
      aria-pressed={active}
      disabled={disabled}
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
  view,
  onChange,
}: BeliefBuilderProps) {
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    const stored = loadStoredBeliefView();
    if (hasBeliefView(stored)) {
      onChange(stored);
    }
    setHydrated(true);
  }, [onChange]);

  function applyView(next: BeliefView) {
    saveBeliefView(next);
    onChange(next);
  }

  function handleDirection(direction: BeliefDirection) {
    applyView(toggleBeliefDirection(view, direction));
  }

  function handleVolatility(volatility: BeliefVolatility) {
    applyView(toggleBeliefVolatility(view, volatility));
  }

  const active = hasBeliefView(view);
  const viewLabel = buildBeliefViewLabel(view);

  return (
    <div className="belief-builder">
      <h3>What do you believe?</h3>
      <p className="selectline" aria-live="polite">
        {active ? (
          <>
            I think BTC will {buildBeliefViewPhrase(view)} by{" "}
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
            Tap <strong>Higher</strong> or <strong>Lower</strong> for price,{" "}
            <strong>More vol</strong> or <strong>Less vol</strong> for range — by{" "}
            <ExpiryPicker
              value={expiryLabel}
              options={expiryOptions}
              onChange={onExpiryChange}
              disabled={expiryPickerDisabled}
              className="selectchip"
            />
            .
          </>
        )}
      </p>

      <div className="belief-axis-list" aria-label="Belief controls">
        <div className="belief-axis-row" role="group" aria-label="Price versus market">
          <span className="belief-axis-label">Price</span>
          <div className="belief-axis-pair">
            <BeliefPairButton
              label="Higher"
              active={view.direction === "higher"}
              disabled={!hydrated}
              onClick={() => handleDirection("higher")}
            />
            <BeliefPairButton
              label="Lower"
              active={view.direction === "lower"}
              disabled={!hydrated}
              onClick={() => handleDirection("lower")}
            />
          </div>
        </div>

        <div className="belief-axis-row" role="group" aria-label="Volatility versus market">
          <span className="belief-axis-label">Volatility</span>
          <div className="belief-axis-pair">
            <BeliefPairButton
              label="More vol"
              active={view.volatility === "more"}
              disabled={!hydrated}
              onClick={() => handleVolatility("more")}
            />
            <BeliefPairButton
              label="Less vol"
              active={view.volatility === "less"}
              disabled={!hydrated}
              onClick={() => handleVolatility("less")}
            />
          </div>
        </div>
      </div>

      <p className="micro">
        {active
          ? `Your view: ${viewLabel}. Tap again to clear a button. Chart updates as you push.`
          : "Push the buttons to see how your view differs from what options price."}
      </p>
    </div>
  );
}
