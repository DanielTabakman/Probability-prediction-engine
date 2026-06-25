"use client";

import { ExpiryPicker } from "@/components/ExpiryPicker";
import { useDisplayCurrency } from "@/lib/useDisplayCurrency";
import type { ExpiryMarketContext } from "@/lib/expiryMarketContext";

type ExpiryMarketContextStripProps = {
  context: ExpiryMarketContext;
  expiryOptions: string[];
  onExpiryChange: (expiry: string) => void;
  expiryPickerDisabled?: boolean;
};

export function ExpiryMarketContextStrip({
  context,
  expiryOptions,
  onExpiryChange,
  expiryPickerDisabled = false,
}: ExpiryMarketContextStripProps) {
  const { formatMoney } = useDisplayCurrency();

  return (
    <section className="expiry-market-context" aria-label="Market context for selected expiry" data-tour="lab-expiry">
      <div className="expiry-market-context-row">
        <span className="expiry-market-context-k">Expiry</span>
        <ExpiryPicker
          className="metric-expiry-value"
          value={context.expiryDate}
          options={expiryOptions}
          onChange={onExpiryChange}
          disabled={expiryPickerDisabled || expiryOptions.length <= 1}
        />
      </div>
      <div className="expiry-market-context-grid">
        <div className="expiry-market-context-cell">
          <div className="expiry-market-context-k">Today&apos;s BTC</div>
          <div className="expiry-market-context-v">{formatMoney(context.spotUsd)}</div>
        </div>
        <div className="expiry-market-context-cell">
          <div className="expiry-market-context-k">Market&apos;s best guess on this date</div>
          <div className="expiry-market-context-v teal">
            {context.marketBestGuessUsd != null
              ? formatMoney(context.marketBestGuessUsd)
              : context.marketBestGuessLabel}
          </div>
        </div>
        <div className="expiry-market-context-cell">
          <div className="expiry-market-context-k">Typical range (middle 50%)</div>
          <div className="expiry-market-context-v amber">{context.typicalRangeLabel}</div>
        </div>
      </div>
      <p className="micro expiry-market-context-note">
        Purple on the chart = what option prices imply. Teal = your view after you adjust.
      </p>
    </section>
  );
}
