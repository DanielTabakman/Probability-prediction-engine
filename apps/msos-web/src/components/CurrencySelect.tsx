"use client";

import { useEffect, useState } from "react";

import {
  DISPLAY_CURRENCY_OPTIONS,
  currencyHint,
  loadStoredDisplayCurrency,
  saveDisplayCurrency,
  type DisplayCurrency,
} from "@/lib/displayCurrency";

type CurrencySelectProps = {
  className?: string;
  /** setup = Strategy Lab expiry row; sidebar = app shell. */
  variant?: "default" | "setup" | "sidebar";
};

export function CurrencySelect({
  className = "",
  variant = "default",
}: CurrencySelectProps) {
  const [currency, setCurrency] = useState<DisplayCurrency>("USD");

  useEffect(() => {
    setCurrency(loadStoredDisplayCurrency());
  }, []);

  function onChange(next: DisplayCurrency) {
    setCurrency(next);
    saveDisplayCurrency(next);
    window.dispatchEvent(new CustomEvent("msos-currency-change", { detail: next }));
  }

  return (
    <label
      className={`currency-select currency-select-${variant} ${className}`.trim()}
      title={currencyHint(currency)}
    >
      <span className="sr-only">Display currency</span>
      <select
        value={currency}
        onChange={(event) => onChange(event.target.value as DisplayCurrency)}
        aria-label="Display currency"
        title={currencyHint(currency)}
      >
        {DISPLAY_CURRENCY_OPTIONS.map((opt) => (
          <option key={opt.id} value={opt.id}>
            {opt.label}
          </option>
        ))}
      </select>
    </label>
  );
}
