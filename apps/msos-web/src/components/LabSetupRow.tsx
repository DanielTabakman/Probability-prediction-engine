"use client";

import { CurrencySelect } from "@/components/CurrencySelect";
import { ExpiryPicker } from "@/components/ExpiryPicker";

type LabSetupRowProps = {
  expiry: string;
  expiryOptions: string[];
  onExpiryChange: (expiry: string) => void;
  expiryDisabled?: boolean;
};

/** Strategy Lab setup — expiry + display currency together. */
export function LabSetupRow({
  expiry,
  expiryOptions,
  onExpiryChange,
  expiryDisabled = false,
}: LabSetupRowProps) {
  return (
    <div className="lab-setup-row" data-tour="lab-expiry">
      <div className="lab-setup-field">
        <span className="lab-setup-k">Expiry</span>
        <ExpiryPicker
          className="lab-setup-expiry"
          value={expiry}
          options={expiryOptions}
          onChange={onExpiryChange}
          disabled={expiryDisabled || expiryOptions.length <= 1}
        />
      </div>
      <div className="lab-setup-field">
        <span className="lab-setup-k">Display currency</span>
        <CurrencySelect className="lab-setup-currency" variant="setup" />
      </div>
    </div>
  );
}
