/**
 * Build thesis confirm copy from Strategy Lab local state + live display payload (display only).
 */

import type { CompareColumn } from "@/data/thesisConfirmFixtures";
import { buildOutcomeFromTuning } from "@/lib/beliefPresets";
import { buildTuningLabel, buildTuningPhrase, type BeliefTuning } from "@/lib/beliefTuning";
import type { DisplayPayload } from "@/lib/ppeDisplayPayload";
import type { ThesisRecord } from "@/lib/thesisPersistence";

function parsePctFromWidth(value: string): number | null {
  const match = value.match(/([\d.]+)\s*%/);
  return match ? Number.parseFloat(match[1]) : null;
}

function marketWidthFromPayload(payload: DisplayPayload): string {
  const rows = payload.summary?.table_rows ?? [];
  const lognormal = rows.find((row) => {
    const method = (row.Method ?? row.method ?? "").toLowerCase();
    return method.includes("lognormal") || method.includes("reference");
  });
  return lognormal?.["Implied range width (IQR)"] ?? "—";
}

function daysUntilExpiry(expiry: string): number {
  const iso = expiry.length <= 10 ? expiry : expiry.slice(0, 10);
  const parsed = Date.parse(iso);
  if (Number.isNaN(parsed)) {
    return 30;
  }
  return Math.max(1, Math.ceil((parsed - Date.now()) / 86_400_000));
}

function buildDifferencePlain(marketPct: number, thesisPct: number, viewLabel: string): string {
  if (!marketPct) {
    return viewLabel;
  }
  const diff = marketPct - thesisPct;
  if (Math.abs(diff) < 0.3) {
    return "About the same range width as options imply";
  }
  const rel = Math.round((Math.abs(diff) / marketPct) * 100);
  if (diff > 0) {
    return `You expect a calmer market — ~${rel}% narrower than options imply`;
  }
  return `You expect more swing than options imply — ~${rel}% wider`;
}

export function buildCompareColumnsFromLab(
  payload: DisplayPayload | null,
  tuning: BeliefTuning,
): CompareColumn[] {
  if (!payload) {
    return [
      { label: "What options price in", value: "Loading live data…", tone: "amber" },
      { label: "Your view", value: buildTuningLabel(tuning), tone: "teal" },
      { label: "The gap", value: "—", tone: "teal" },
    ];
  }
  const marketWidthStr = marketWidthFromPayload(payload);
  const marketPct = parsePctFromWidth(marketWidthStr) ?? 0;
  const thesisPct = Math.round(marketPct * tuning.vol_mult * 10) / 10;
  const viewLabel = buildTuningLabel(tuning);
  return [
    {
      label: "What options price in",
      value: marketWidthStr.includes("%")
        ? `Typical swing about ${marketWidthStr}`
        : `Typical swing about ${marketPct}%`,
      tone: "amber",
    },
    { label: "Your view", value: viewLabel, tone: "teal" },
    {
      label: "The gap",
      value: buildDifferencePlain(marketPct, thesisPct, viewLabel),
      tone: "teal",
    },
  ];
}

export function buildThesisRestatement(tuning: BeliefTuning, expiryLabel: string) {
  const phrase = buildTuningPhrase(tuning);
  return {
    prefix: "I think BTC will",
    emphasis: phrase,
    suffix: "over the selected horizon —",
    horizon: expiryLabel,
  };
}

export function buildThesisDraftFromLab(
  payload: DisplayPayload | null,
  tuning: BeliefTuning,
  expiry: string | null,
): Partial<ThesisRecord> {
  const resolvedExpiry = expiry?.trim() || payload?.series_by_expiry?.[0]?.expiry_date || "";
  const marketWidthStr = payload ? marketWidthFromPayload(payload) : "—";
  const marketPct = parsePctFromWidth(marketWidthStr) ?? 6.8;
  const thesisPct = Math.round(marketPct * tuning.vol_mult * 10) / 10;
  const outcome = payload
    ? buildOutcomeFromTuning(tuning, payload, true, resolvedExpiry || undefined)
    : null;

  return {
    instrument: "BTC options",
    horizonDays: resolvedExpiry ? daysUntilExpiry(resolvedExpiry) : 30,
    marketRangePct: marketPct,
    thesisRangePct: thesisPct,
    referenceLabel: payload
      ? `BTC options · live · exp ${resolvedExpiry || "—"}`
      : "BTC options · live implied distribution",
    trustLabel: payload ? "Good · Deribit" : "Offline · demo values",
    expiryDate: resolvedExpiry || undefined,
    beliefSnapshot: {
      forwardMult: tuning.forward_mult,
      volMult: tuning.vol_mult,
      viewLabel: buildTuningLabel(tuning),
    },
    disagreementLine: outcome?.headline,
    spotUsdAtConfirm: payload?.spot_usd,
  };
}

export function buildConfirmChecklist(expiry: string | null, live: boolean) {
  return [
    {
      id: "reference",
      label: live
        ? "Market reference — live BTC options from Deribit"
        : "Market reference — offline; confirm when live data returns",
    },
    {
      id: "trust",
      label: live ? "Data looks current — quotes refreshed recently" : "Data quality — using last known values",
    },
    {
      id: "horizon",
      label: expiry
        ? `Timeframe locked — BTC · exp ${expiry}`
        : "Timeframe — pick an expiry in Strategy Lab",
    },
  ];
}
