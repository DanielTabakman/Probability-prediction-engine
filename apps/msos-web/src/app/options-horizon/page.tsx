import type { Metadata } from "next";

import { AppShell } from "@/components/AppShell";
import { OptionsHorizonClient } from "@/components/OptionsHorizonClient";
import type { HorizonChartPayload } from "@/lib/horizonChartPayload";
import { HORIZON_CHART_API_URL } from "@/lib/horizonChartPayload";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Options Horizon | Market Structure OS",
  description:
    "Chart-first BTC view — spot, volume, options-implied forward, and thesis region (simulation only).",
};

async function fetchServerChartPayload(): Promise<HorizonChartPayload | null> {
  const base = process.env.MSOS_INTERNAL_ORIGIN ?? "http://127.0.0.1:3000";
  try {
    const url = HORIZON_CHART_API_URL.startsWith("http")
      ? HORIZON_CHART_API_URL
      : `${base}${HORIZON_CHART_API_URL}`;
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) return null;
    return (await res.json()) as HorizonChartPayload;
  } catch {
    return null;
  }
}

export default async function OptionsHorizonPage() {
  const initialPayload = await fetchServerChartPayload();

  return (
    <AppShell activeNavId="options-horizon">
      <OptionsHorizonClient initialPayload={initialPayload} />
    </AppShell>
  );
}
