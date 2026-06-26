"use client";

import { LabSetupRow } from "@/components/LabSetupRow";
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
    <section className="expiry-market-context" aria-label="Market context for selected expiry">
      <LabSetupRow
        expiry={context.expiryDate}
        expiryOptions={expiryOptions}
        onExpiryChange={onExpiryChange}
        expiryDisabled={expiryPickerDisabled}
      />
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
              : context.marketBestGuessFallback}
          </div>
        </div>
        <div className="expiry-market-context-cell">
          <div className="expiry-market-context-k">Typical range (middle 50%)</div>
          <div className="expiry-market-context-v amber">
            {context.typicalRangeUsd
              ? `${formatMoney(context.typicalRangeUsd.q1)} – ${formatMoney(context.typicalRangeUsd.q3)}`
              : context.typicalRangeFallback}
          </div>
        </div>
      </div>
      <p className="micro expiry-market-context-note">
        Purple on the chart = what option prices imply. Teal = your view after you adjust.
      </p>
    </section>
  );
}
