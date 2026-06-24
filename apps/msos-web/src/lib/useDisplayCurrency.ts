"use client";

import { useEffect, useState } from "react";

import {
  formatMoney as formatMoneyUsd,
  loadStoredDisplayCurrency,
  type DisplayCurrency,
} from "@/lib/displayCurrency";

export function useDisplayCurrency() {
  const [currency, setCurrency] = useState<DisplayCurrency>("USD");

  useEffect(() => {
    setCurrency(loadStoredDisplayCurrency());
    const onChange = (event: Event) => {
      const detail = (event as CustomEvent<DisplayCurrency>).detail;
      if (detail) setCurrency(detail);
    };
    window.addEventListener("msos-currency-change", onChange);
    return () => window.removeEventListener("msos-currency-change", onChange);
  }, []);

  return {
    currency,
    formatMoney: (usd: number) => formatMoneyUsd(usd, currency),
  };
}
