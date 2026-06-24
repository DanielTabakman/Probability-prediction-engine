"use client";

import { useEffect, useState } from "react";

import {
  DISPLAY_CURRENCY_OPTIONS,
  loadStoredDisplayCurrency,
  saveDisplayCurrency,
  type DisplayCurrency,
} from "@/lib/displayCurrency";

export function CurrencySelect({ className = "" }: { className?: string }) {
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
    <label className={`currency-select ${className}`.trim()}>
      <span className="sr-only">Display currency</span>
      <select
        value={currency}
        onChange={(event) => onChange(event.target.value as DisplayCurrency)}
        aria-label="Display currency"
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
