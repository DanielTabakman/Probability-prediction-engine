/**
 * Build thesis confirm copy from Strategy Lab local state + live display payload (display only).
 */

import type { CompareColumn } from "@/data/thesisConfirmFixtures";
import { buildOutcomeFromTuning } from "@/lib/beliefPresets";
import {
  buildTuningLabel,
  buildTuningPhrase,
  isMarketTuning,
  type BeliefTuning,
} from "@/lib/beliefTuning";
import {
  optionsTrustSourceLabel,
  optionsVenueReferenceLabel,
  resolveDisplayAssetMeta,
  type DisplayAssetMeta,
  type DisplayPayload,
} from "@/lib/ppeDisplayPayload";
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

function buildGapDescription(tuning: BeliefTuning, marketPct: number, thesisPct: number): string {
  if (isMarketTuning(tuning)) {
    return "Matches what options imply";
  }

  const forwardHigh = tuning.forward_mult > 1.002;
  const forwardLow = tuning.forward_mult < 0.998;
  const volHigh = tuning.vol_mult > 1.02;
  const volLow = tuning.vol_mult < 0.98;

  if (forwardHigh && !volHigh && !volLow) {
    return "You expect a higher finish than options imply";
  }
  if (forwardLow && !volHigh && !volLow) {
    return "You expect a lower finish than options imply";
  }
  if (!forwardHigh && !forwardLow && volHigh) {
    return "You expect bigger swings than options imply";
  }
  if (!forwardHigh && !forwardLow && volLow) {
    return "You expect a calmer path than options imply";
  }
  if ((forwardHigh || forwardLow) && (volHigh || volLow)) {
    const direction = forwardHigh ? "higher" : "lower";
    const vol = volHigh ? "with more vol" : "with less vol";
    return `You expect ${direction} ${vol} than options imply`;
  }

  if (marketPct >= 0.3) {
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

  if (forwardHigh || forwardLow) {
    return forwardHigh
      ? "You lean higher versus what options imply"
      : "You lean lower versus what options imply";
  }

  return "Your view differs from what options imply";
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
      value: buildGapDescription(tuning, marketPct, thesisPct),
      tone: "teal",
    },
  ];
}

export function buildThesisRestatement(
  tuning: BeliefTuning,
  expiryLabel: string,
  assetMeta?: DisplayAssetMeta,
) {
  const asset = assetMeta ?? resolveDisplayAssetMeta(null);
  const phrase = buildTuningPhrase(tuning);
  return {
    prefix: `I think ${asset.id} will`,
    emphasis: phrase,
    suffix: "over the selected horizon —",
    horizon: expiryLabel,
  };
}

export function buildThesisDraftFromLab(
  payload: DisplayPayload | null,
  tuning: BeliefTuning,
  expiry: string | null,
  assetMeta?: DisplayAssetMeta,
): Partial<ThesisRecord> {
  const asset = assetMeta ?? resolveDisplayAssetMeta(payload);
  const instrument = asset.instrument_label ?? asset.label;
  const resolvedExpiry = expiry?.trim() || payload?.series_by_expiry?.[0]?.expiry_date || "";
  const marketWidthStr = payload ? marketWidthFromPayload(payload) : "—";
  const marketPct = parsePctFromWidth(marketWidthStr) ?? 6.8;
  const thesisPct = Math.round(marketPct * tuning.vol_mult * 10) / 10;
  const outcome = payload
    ? buildOutcomeFromTuning(tuning, payload, true, resolvedExpiry || undefined, asset)
    : null;

  return {
    instrument,
    assetId: asset.id,
    horizonDays: resolvedExpiry ? daysUntilExpiry(resolvedExpiry) : 30,
    marketRangePct: marketPct,
    thesisRangePct: thesisPct,
    referenceLabel: payload
      ? `${instrument} · live · exp ${resolvedExpiry || "—"}`
      : `${instrument} · live implied distribution`,
    trustLabel: payload ? optionsTrustSourceLabel(asset) : "Offline · demo values",
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

export function buildConfirmChecklist(
  expiry: string | null,
  live: boolean,
  assetMeta?: DisplayAssetMeta,
) {
  const asset = assetMeta ?? resolveDisplayAssetMeta(null);
  const instrument = asset.instrument_label ?? asset.label;
  return [
    {
      id: "reference",
      label: live
        ? `Market reference — live ${instrument} from ${optionsVenueReferenceLabel(asset)}`
        : "Market reference — offline; confirm when live data returns",
    },
    {
      id: "trust",
      label: live ? "Data looks current — quotes refreshed recently" : "Data quality — using last known values",
    },
    {
      id: "horizon",
      label: expiry
        ? `Timeframe locked — ${asset.id} · exp ${expiry}`
        : "Timeframe — pick an expiry in Strategy Lab",
    },
  ];
}
